import pytest
from django.urls import reverse
from django.utils import timezone
from django.core import mail, signing
from django.test import override_settings
from rest_framework.test import APIClient

from accounts.models import User
from properties.models import Category, Property
from search.models import SavedSearch, SearchAlert
from search.services import run_saved_search_alerts
from inquiries.models import Inquiry
from favorites.models import Favorite
from visits.models import Visit
from propvista.mail import (
    send_login_alert,
    send_password_changed_email,
    send_security_alert,
    send_inquiry_received_email,
    send_property_approved_email,
    send_property_rejected_email,
    send_property_favorited_email,
    send_templated_email,
)

@pytest.fixture
def category(db):
    return Category.objects.create(name="Residential", slug="residential")

@pytest.fixture
def seller(db):
    return User.objects.create_user(username="seller_prod", password="Pass@12345", role=User.Role.SELLER, email="seller@example.com")

@pytest.fixture
def buyer(db):
    return User.objects.create_user(username="buyer_prod", password="Pass@12345", role=User.Role.BUYER, email="buyer@example.com")

@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(username="admin_prod", password="Pass@12345", email="admin@example.com")

@pytest.fixture
def active_property(db, seller, category):
    return Property.objects.create(
        title="Juhu Beach Villa",
        description="Premium beach view villa.",
        price=20000000,
        property_type=Property.PropertyType.VILLA,
        category=category,
        bedrooms=4,
        bathrooms=4,
        area_sqft=3000,
        address="Juhu",
        city="Mumbai",
        locality="Juhu",
        pincode="400049",
        approval_status=Property.ApprovalStatus.APPROVED,
        status=Property.Status.ACTIVE,
        created_by=seller,
    )

@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_demo_login_and_logout(client, db):
    User.objects.create_user(username="buyer", password="Pass@12345", role=User.Role.BUYER)
    # Test demo login redirects and actions
    response = client.get(reverse("accounts:demo_login", args=["buyer"]))
    assert response.status_code == 302
    assert response.url == reverse("accounts:dashboard")

    # Invalid role should return 404
    response = client.get(reverse("accounts:demo_login", args=["non_existent"]))
    assert response.status_code == 404

    # Demo logout
    response = client.get(reverse("accounts:demo_logout"))
    assert response.status_code == 302
    assert response.url == reverse("home")

@pytest.mark.django_db
def test_verify_email_edge_cases(client, buyer):
    # Expired token
    token_expired = signing.dumps({"user_id": buyer.pk, "email": buyer.email})
    # We alter token to simulate bad signature or pass signature errors
    response = client.get(reverse("accounts:verify_email", args=[token_expired + "invalid"]))
    assert response.status_code == 302
    assert buyer.is_verified is False

    # Check bad signature explicitly
    response = client.get(reverse("accounts:verify_email", args=["completely-invalid-signature"]))
    assert response.status_code == 302

@pytest.mark.django_db
def test_profile_form_errors_and_password_change(client, buyer):
    client.force_login(buyer)
    
    # POST to profile with change_password with invalid password form
    response = client.post(
        reverse("accounts:profile"),
        {
            "change_password": "1",
            "old_password": "wrong_password",
            "new_password1": "short",
            "new_password2": "mismatch",
        }
    )
    assert response.status_code == 200 # Renders with form errors

    # POST to profile with invalid profile details
    response = client.post(
        reverse("accounts:profile"),
        {
            "first_name": "New",
            "last_name": "Buyer",
            "email": "invalid-email-no-domain",
            "phone": "12345" # invalid length/starts with
        }
    )
    assert response.status_code == 200 # Form errors

@pytest.mark.django_db
def test_admin_users_view_filtering(client, admin_user, seller, buyer):
    client.force_login(admin_user)
    response = client.get(reverse("accounts:admin_users"), {"role": "seller"})
    assert response.status_code == 200
    assert seller.username.encode() in response.content
    assert buyer.username.encode() not in response.content

    response = client.get(reverse("accounts:admin_users"), {"role": "buyer"})
    assert response.status_code == 200
    assert buyer.username.encode() in response.content
    assert seller.username.encode() not in response.content

@pytest.mark.django_db
def test_admin_dashboard_monthly_growth_labels(client, admin_user):
    client.force_login(admin_user)
    # Ensure monthly users registration graph executes cleanly
    response = client.get(reverse("accounts:admin_dashboard"))
    assert response.status_code == 200
    assert b"Admin command center" in response.content

@pytest.mark.django_db
def test_user_viewset_permissions_and_filtering(buyer, admin_user, seller):
    api = APIClient()
    
    # Unauthenticated user cannot retrieve lists
    response = api.get("/api/v1/users/")
    assert response.status_code == 401
    
    # Authenticated non-admin sees only themselves
    api.force_authenticate(user=buyer)
    response = api.get("/api/v1/users/")
    assert response.status_code == 200
    res_data = response.json()
    results = res_data.get("results", res_data)
    assert len(results) == 1
    assert results[0]["username"] == buyer.username

    # Authenticated admin sees all users
    api.force_authenticate(user=admin_user)
    response = api.get("/api/v1/users/")
    assert response.status_code == 200
    res_data = response.json()
    results = res_data.get("results", res_data)
    assert len(results) >= 3

@pytest.mark.django_db
def test_homepage(client, active_property):
    # Renders homepage successfully with metrics and trend charts
    response = client.get(reverse("home"))
    assert response.status_code == 200
    assert active_property.title.encode() in response.content

@pytest.mark.django_db
def test_properties_city_page(client, active_property):
    # Verify city page shows matching city properties
    response = client.get(reverse("properties:city", args=["Mumbai"]))
    assert response.status_code == 200
    assert active_property.title.encode() in response.content

@pytest.mark.django_db
def test_property_update_and_delete_views(client, seller, buyer, active_property, category):
    # 1. Unauthorized edit attempt (not seller role)
    client.force_login(buyer)
    url_edit = reverse("properties:update", args=[active_property.slug])
    response = client.get(url_edit)
    assert response.status_code == 403 # role required check

    # 2. Authorized get edit form as Seller (owner)
    client.force_login(seller)
    response = client.get(url_edit)
    assert response.status_code == 200
    
    # 3. Post edit form
    response = client.post(
        url_edit,
        {
            "title": "Juhu Beach Villa (Modified)",
            "description": active_property.description,
            "price": 22000000,
            "property_type": Property.PropertyType.VILLA,
            "category": category.id,
            "bedrooms": 4,
            "bathrooms": 4,
            "area_sqft": 3000,
            "address": "Juhu",
            "city": "Mumbai",
            "locality": "Juhu",
            "pincode": "400049",
            "status": "active",
            "parking": 1,
        }
    )
    assert response.status_code == 302
    active_property.refresh_from_db()
    assert active_property.title == "Juhu Beach Villa (Modified)"
    
    # 4. Get delete confirmation page
    url_delete = reverse("properties:delete", args=[active_property.slug])
    response = client.get(url_delete)
    assert response.status_code == 200
    assert b"Are you sure you want to delete" in response.content or b"Delete" in response.content

    # 5. List properties filtered by owner=me
    response = client.get(reverse("properties:list"), {"owner": "me"})
    assert response.status_code == 200

@pytest.mark.django_db
def test_property_delete_and_submit_approval(client, seller, active_property):
    client.force_login(seller)
    
    # Mark status as pending
    active_property.status = Property.Status.PENDING
    active_property.approval_status = Property.ApprovalStatus.PENDING
    active_property.save()

    # Submit for approval
    response = client.post(reverse("properties:submit", args=[active_property.slug]))
    assert response.status_code == 302
    
    # Delete property
    response = client.post(reverse("properties:delete", args=[active_property.slug]))
    assert response.status_code == 302
    assert not Property.objects.filter(pk=active_property.pk).exists()

@pytest.mark.django_db
def test_ai_draft_inquiry_fallback_and_graceful_degrades(client, buyer, active_property):
    client.force_login(buyer)
    url = reverse("properties:ai_draft_inquiry", args=[active_property.slug])
    
    # Default GET request should fail (expects POST)
    response = client.get(url)
    assert response.status_code == 405

    # POST triggers generation fallback
    response = client.post(url, {"message": "Looking to buy this house"})
    assert response.status_code == 200
    data = response.json()
    assert "draft" in data
    assert "crisp location benefits" in data["draft"].lower() or "add" in data["draft"].lower()

@pytest.mark.django_db
def test_mail_helper_functions(db, buyer, seller, active_property):
    mail.outbox.clear()
    
    # Send empty recipient list
    result = send_templated_email("Empty Test", "Hello", [])
    assert result is False
    assert len(mail.outbox) == 0

    # send_login_alert
    mail.outbox.clear()
    assert send_login_alert(buyer, ip="127.0.0.1") is True
    assert len(mail.outbox) == 1

    # send_password_changed_email
    mail.outbox.clear()
    assert send_password_changed_email(buyer) is True
    assert len(mail.outbox) == 1

    # send_security_alert
    mail.outbox.clear()
    assert send_security_alert(buyer, "suspicious activities") is True
    assert len(mail.outbox) == 1

    # send_inquiry_received_email
    inq = Inquiry.objects.create(
        property=active_property,
        buyer=buyer,
        name="Buyer Tester",
        email="buyer@example.com",
        phone="9876543210",
        message="Hello"
    )
    mail.outbox.clear()
    assert send_inquiry_received_email(inq) is True
    assert len(mail.outbox) == 1

    # send_property_approved_email
    mail.outbox.clear()
    assert send_property_approved_email(active_property) is True
    assert len(mail.outbox) == 1

    # send_property_rejected_email
    active_property.rejection_reason = "Improper pricing"
    active_property.save()
    mail.outbox.clear()
    assert send_property_rejected_email(active_property) is True
    assert len(mail.outbox) == 1

    # send_property_favorited_email
    fav = Favorite.objects.create(user=buyer, property=active_property)
    mail.outbox.clear()
    assert send_property_favorited_email(fav) is True
    assert len(mail.outbox) == 1

@pytest.mark.django_db
def test_saved_search_alerts_and_signals(buyer, active_property):
    # Setup saved search for notifications
    saved = SavedSearch.objects.create(
        user=buyer,
        name="Mumbai watchlist",
        notify_on_new=True,
        query_params={"city": "Mumbai", "q": "beach"}
    )
    
    # Run alerts for our new property
    run_saved_search_alerts(property_obj=active_property)
    
    # Verification
    assert SearchAlert.objects.filter(saved_search=saved, property=active_property).exists()
    from notifications.models import Notification
    assert Notification.objects.filter(user=buyer, title__icontains="Juhu Beach").exists()

@pytest.mark.django_db
def test_saved_search_viewset_extra_logic(buyer):
    api = APIClient()
    api.force_authenticate(user=buyer)
    
    # Create saved search
    response = api.post(
        "/api/v1/saved-searches/",
        {"name": "Villas", "query_params": {"property_type": "villa"}},
        format="json"
    )
    assert response.status_code == 201
    saved_id = response.json()["id"]

    # Update with query_params as JSON string
    response = api.patch(
        f"/api/v1/saved-searches/{saved_id}/",
        {"query_params": '{"property_type": "villa", "city": "Pune"}'},
        format="json"
    )
    assert response.status_code == 200
    saved = SavedSearch.objects.get(pk=saved_id)
    assert saved.query_params.get("city") == "Pune"

    # Update with query_params as invalid JSON string
    response = api.patch(
        f"/api/v1/saved-searches/{saved_id}/",
        {"query_params": 'invalid-json{'},
        format="json"
    )
    assert response.status_code == 200
    saved.refresh_from_db()
    assert saved.query_params == {}

@pytest.mark.django_db
def test_book_visit_views(client, buyer, active_property):
    # Unauthenticated redirect
    url = reverse("visits:book", args=[active_property.slug])
    response = client.post(url)
    assert response.status_code == 302

    # Authenticated get is redirect
    client.force_login(buyer)
    response = client.get(url)
    assert response.status_code == 302

    # POST with valid form
    tomorrow = (timezone.now() + timezone.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    response = client.post(url, {"scheduled_at": tomorrow})
    assert response.status_code == 302
    assert Visit.objects.filter(buyer=buyer, property=active_property).exists()

    # POST with invalid form
    response = client.post(url, {"scheduled_at": "invalid-date"})
    assert response.status_code == 302

@pytest.mark.django_db
def test_favorites_api_extended(buyer, active_property):
    api = APIClient()
    api.force_authenticate(user=buyer)
    
    # create with slug
    response = api.post("/api/v1/favorites/", {"slug": active_property.slug})
    assert response.status_code == 201
    
    # create already saved
    response = api.post("/api/v1/favorites/", {"slug": active_property.slug})
    assert response.status_code == 200

    # list favorites
    response = api.get("/api/v1/favorites/")
    assert response.status_code == 200
    res_data = response.json()
    results = res_data.get("results", res_data)
    assert len(results) == 1
    
    # remove_by_slug
    response = api.delete(f"/api/v1/favorites/by-slug/{active_property.slug}/")
    assert response.status_code == 204

    # remove non-existent
    response = api.delete("/api/v1/favorites/by-slug/non-existent-slug/")
    assert response.status_code == 404

    # toggle non-existent
    response = api.post("/api/v1/favorites/toggle/non-existent-slug/")
    assert response.status_code == 404

@pytest.mark.django_db
def test_leads_api_extended(seller, active_property, buyer):
    api = APIClient()
    
    # buyer role has empty lead query set
    api.force_authenticate(user=buyer)
    response = api.get("/api/v1/leads/")
    assert response.status_code == 200
    res_data = response.json()
    results = res_data.get("results", res_data)
    assert len(results) == 0

    # seller role queryset
    api.force_authenticate(user=seller)
    # create lead with invalid phone number
    response = api.post("/api/v1/leads/", {"property": active_property.pk, "name": "Test Lead", "phone": "12345"}, format="json")
    assert response.status_code == 400
    assert "phone" in response.json()

    # create lead with valid phone number
    response = api.post("/api/v1/leads/", {"property": active_property.pk, "name": "Test Lead", "phone": "9876543210"}, format="json")
    assert response.status_code == 201
    
    # retrieve list
    response = api.get("/api/v1/leads/")
    assert response.status_code == 200
    res_data = response.json()
    results = res_data.get("results", res_data)
    assert len(results) == 1

@pytest.mark.django_db
def test_visits_api_extended(buyer, active_property, seller, admin_user):
    api = APIClient()
    api.force_authenticate(user=buyer)
    
    # scheduled_at past time validation
    past_time = (timezone.now() - timezone.timedelta(days=1)).isoformat()
    response = api.post("/api/v1/visits/", {"property": active_property.pk, "scheduled_at": past_time}, format="json")
    assert response.status_code == 400
    assert "scheduled_at" in response.json()

    # scheduled_at future time (valid)
    future_time = (timezone.now() + timezone.timedelta(days=1)).isoformat()
    response = api.post("/api/v1/visits/", {"property": active_property.pk, "scheduled_at": future_time}, format="json")
    assert response.status_code == 201
    response.json()["id"]

    # test querysets for different roles
    # buyer queryset
    response = api.get("/api/v1/visits/")
    assert response.status_code == 200
    res_data = response.json()
    results = res_data.get("results", res_data)
    assert len(results) == 1

    # seller queryset
    api.force_authenticate(user=seller)
    response = api.get("/api/v1/visits/")
    assert response.status_code == 200
    res_data = response.json()
    results = res_data.get("results", res_data)
    assert len(results) == 1

    # admin queryset
    api.force_authenticate(user=admin_user)
    response = api.get("/api/v1/visits/")
    assert response.status_code == 200
    res_data = response.json()
    results = res_data.get("results", res_data)
    assert len(results) == 1

    # invalid property perform_create
    api.force_authenticate(user=buyer)
    response = api.post("/api/v1/visits/", {"property": 99999, "scheduled_at": future_time}, format="json")
    assert response.status_code == 400

@pytest.fixture
def other_seller(db):
    return User.objects.create_user(username="other_seller_prod", password="Pass@12345", role=User.Role.SELLER, email="other_seller@example.com")

@pytest.mark.django_db
def test_properties_views_edge_cases(client, seller, other_seller, active_property, buyer, category):
    # 1. Unauthorized edit attempt by another seller
    client.force_login(other_seller)
    url_edit = reverse("properties:update", args=[active_property.slug])
    response = client.get(url_edit)
    assert response.status_code == 302 # redirects to detail with error message

    # 2. Unauthorized delete attempt by another seller
    url_delete = reverse("properties:delete", args=[active_property.slug])
    response = client.post(url_delete)
    assert response.status_code == 302 # redirects to detail

    # 3. Status checks for workflows
    # Property is ACTIVE.
    # Reopen active property (should fail because not closed)
    response = client.post(reverse("properties:reopen", args=[active_property.slug]))
    assert response.status_code == 302
    
    # Activate active property (should fail because not approved status)
    response = client.post(reverse("properties:activate", args=[active_property.slug]))
    assert response.status_code == 302

    # Submit active property for approval (should fail because not draft status)
    response = client.post(reverse("properties:submit", args=[active_property.slug]))
    assert response.status_code == 302

    # Mark active property as sold
    client.force_login(seller)
    response = client.post(reverse("properties:mark_sold", args=[active_property.slug]))
    assert response.status_code == 302
    active_property.refresh_from_db()
    assert active_property.status == Property.Status.SOLD

    # Try to mark sold property as closed (should fail because not active)
    response = client.post(reverse("properties:mark_closed", args=[active_property.slug]))
    assert response.status_code == 302

    # Try to mark sold property as sold (should fail because not active)
    response = client.post(reverse("properties:mark_sold", args=[active_property.slug]))
    assert response.status_code == 302

    # 4. Property detail page 404 for unapproved property viewed by buyer
    p_pending = Property.objects.create(
        title="Pending Villa",
        description="Test pending.",
        price=10000000,
        property_type=Property.PropertyType.VILLA,
        category=category,
        bedrooms=3,
        bathrooms=3,
        area_sqft=2000,
        address="Bandra",
        city="Mumbai",
        locality="Bandra",
        pincode="400050",
        approval_status=Property.ApprovalStatus.PENDING,
        status=Property.Status.PENDING,
        created_by=seller,
    )
    client.force_login(buyer)
    response = client.get(reverse("properties:detail", args=[p_pending.slug]))
    assert response.status_code == 404

    # 5. List properties filtering variations
    client.force_login(seller)
    response = client.get(reverse("properties:list"), {"owner": "me", "approval_status": "pending"})
    assert response.status_code == 200

    # 6. Homepage render with Lakh and Thousand price brackets and loops
    # Create smaller price properties
    Property.objects.create(
        title="Lakh Property",
        price=500000, # 5 Lakhs
        property_type=Property.PropertyType.APARTMENT,
        category=category,
        bedrooms=1,
        bathrooms=1,
        area_sqft=500,
        address="Mumbai",
        city="Mumbai",
        locality="Worli",
        pincode="400018",
        approval_status=Property.ApprovalStatus.APPROVED,
        status=Property.Status.ACTIVE,
        created_by=seller,
    )
    Property.objects.create(
        title="Thousand Property",
        price=5000, # 5 Thousand
        property_type=Property.PropertyType.APARTMENT,
        category=category,
        bedrooms=1,
        bathrooms=1,
        area_sqft=500,
        address="Mumbai",
        city="Mumbai",
        locality="Worli",
        pincode="400018",
        approval_status=Property.ApprovalStatus.APPROVED,
        status=Property.Status.ACTIVE,
        created_by=seller,
    )
    # Create inquiry and visit for timeline loop
    Inquiry.objects.create(
        property=active_property,
        buyer=buyer,
        name="Timeline Inquirer",
        email="buyer@example.com",
        phone="9999999999",
        message="Hi"
    )
    Visit.objects.create(
        property=active_property,
        buyer=buyer,
        scheduled_at=timezone.now() + timezone.timedelta(days=2)
    )
    
    response = client.get(reverse("home"))
    assert response.status_code == 200

@pytest.mark.django_db
def test_dashboard_redirects(client, buyer, seller, admin_user):
    client.force_login(buyer)
    response = client.get(reverse("accounts:dashboard"))
    assert response.status_code == 302
    assert response.url == reverse("accounts:buyer_dashboard")

    client.force_login(seller)
    response = client.get(reverse("accounts:dashboard"))
    assert response.status_code == 302
    assert response.url == reverse("accounts:seller_dashboard")

    client.force_login(admin_user)
    response = client.get(reverse("accounts:dashboard"))
    assert response.status_code == 302
    assert response.url == reverse("accounts:admin_dashboard")

@pytest.mark.django_db
def test_inquiries_extended(client, buyer, seller, admin_user, active_property, other_seller):
    # 1. inquiries:list rendering for admin, seller, buyer
    client.force_login(admin_user)
    response = client.get(reverse("inquiries:list"))
    assert response.status_code == 200

    client.force_login(seller)
    response = client.get(reverse("inquiries:list"))
    assert response.status_code == 200

    client.force_login(buyer)
    response = client.get(reverse("inquiries:list"))
    assert response.status_code == 200

    # 2. Inquiry creation validation on sold/closed property
    active_property.status = Property.Status.SOLD
    active_property.save()
    response = client.post(reverse("inquiries:create", args=[active_property.slug]), {"name": "Test", "email": "a@b.com", "phone": "9999999999", "message": "hello"})
    assert response.status_code == 302 # Redirected back with warning message

    # GET request check
    response = client.get(reverse("inquiries:create", args=[active_property.slug]))
    assert response.status_code == 302

    # 3. Status updates and permissions
    inq = Inquiry.objects.create(
        property=active_property,
        buyer=buyer,
        name="Test Inquirer",
        email="buyer@example.com",
        phone="9876543210",
        message="Hello"
    )
    # unauthorized seller updates status
    client.force_login(other_seller)
    response = client.post(reverse("inquiries:update_status", args=[inq.pk]), {"status": "contacted"})
    assert response.status_code == 302 # redirected back with error
    
    # authorized admin updates status with invalid choice
    client.force_login(admin_user)
    response = client.post(reverse("inquiries:update_status", args=[inq.pk]), {"status": "invalid_status_choice"})
    assert response.status_code == 302
    
    # authorized admin updates status with valid choice
    response = client.post(reverse("inquiries:update_status", args=[inq.pk]), {"status": "contacted"})
    assert response.status_code == 302
    inq.refresh_from_db()
    assert inq.status == "contacted"

    # 4. InquiryViewSet API
    api = APIClient()
    api.force_authenticate(user=buyer)
    
    # Queryset test
    response = api.get("/api/v1/inquiries/")
    assert response.status_code == 200
    res_data = response.json()
    results = res_data.get("results", res_data)
    assert len(results) == 1

    # perform_create on SOLD property raises validation error
    response = api.post("/api/v1/inquiries/", {"property": active_property.pk, "name": "Buyer Inq"}, format="json")
    assert response.status_code == 400

@pytest.mark.django_db
def test_leads_views_extended(client, seller, other_seller, active_property, admin_user):
    from leads.models import Lead
    
    # 1. GET requests
    client.force_login(seller)
    response = client.get(reverse("leads:list"))
    assert response.status_code == 200
    
    response = client.get(reverse("leads:create"))
    assert response.status_code == 200

    # 2. POST create lead
    response = client.post(
        reverse("leads:create"),
        {
            "property": active_property.pk,
            "name": "View Lead",
            "phone": "9876543210",
            "stage": "new",
            "score": 90,
        }
    )
    assert response.status_code == 302
    lead = Lead.objects.get(name="View Lead")
    assert lead.owner == seller

    # 3. GET / POST update lead
    url_update = reverse("leads:update", args=[lead.pk])
    response = client.get(url_update)
    assert response.status_code == 200

    # Unauthorized edit
    client.force_login(other_seller)
    response = client.get(url_update)
    assert response.status_code == 302 # redirects back

    # Authorized edit post
    client.force_login(seller)
    response = client.post(
        url_update,
        {
            "property": active_property.pk,
            "name": "View Lead (Updated)",
            "phone": "9876543210",
            "stage": "contacted",
            "score": 95,
        }
    )
    assert response.status_code == 302
    lead.refresh_from_db()
    assert lead.name == "View Lead (Updated)"

@pytest.mark.django_db
def test_market_pulse_view(client, active_property):
    # Verify market pulse renders with chart data and city stats
    url = reverse("properties:market_pulse")
    response = client.get(url)
    assert response.status_code == 200
    assert b"Market Pulse" in response.content
    assert b"Real-time Analytics" in response.content
    # Check context contains serialized data
    assert "city_stats" in response.context
    assert "total_listings" in response.context
    assert response.context["total_listings"] >= 1


