import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.models import User
from notifications.models import Notification
from properties.models import Category, Property
from search.models import SavedSearch, SearchHistory


@pytest.fixture
def category(db):
    return Category.objects.create(name="Residential", slug="residential")


@pytest.fixture
def seller(db):
    return User.objects.create_user(username="sellerx", password="Pass@12345", role=User.Role.SELLER)


@pytest.fixture
def buyer(db):
    return User.objects.create_user(username="buyerx", password="Pass@12345", role=User.Role.BUYER)


@pytest.fixture
def approved_property(db, seller, category):
    return Property.objects.create(
        title="Bandra Sea View",
        description="Premium apartment",
        price=10000000,
        property_type=Property.PropertyType.APARTMENT,
        category=category,
        bedrooms=2,
        bathrooms=2,
        area_sqft=1100,
        address="Bandra",
        city="Mumbai",
        locality="Bandra",
        pincode="400050",
        approval_status=Property.ApprovalStatus.APPROVED,
        status=Property.Status.ACTIVE,
        created_by=seller,
    )


@pytest.mark.django_db
def test_property_view_creates_analytics_event(client, seller, approved_property):
    response = client.get(reverse("properties:detail", args=[approved_property.slug]))
    assert response.status_code == 200
    from analytics.models import PropertyViewEvent

    assert PropertyViewEvent.objects.filter(property=approved_property).exists()


@pytest.mark.django_db
def test_buyer_dashboard_works_without_profile(client, buyer):
    Notification.objects.create(user=buyer, title="Hi", body="Welcome")
    client.force_login(buyer)
    response = client.get(reverse("accounts:buyer_dashboard"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_inquiry_creates_notification_for_seller(client, buyer, seller, approved_property):
    client.force_login(buyer)
    response = client.post(
        reverse("inquiries:create", args=[approved_property.slug]),
        {"name": "Buyer", "email": "buyer@example.com", "phone": "9999999999", "message": "Hi"},
    )
    assert response.status_code == 302
    assert Notification.objects.filter(user=seller, category=Notification.Category.INQUIRY).exists()


@pytest.mark.django_db
def test_favorite_toggle_creates_notification(client, buyer, seller, approved_property):
    client.force_login(buyer)
    response = client.get(reverse("favorites:toggle", args=[approved_property.slug]))
    assert response.status_code == 302
    assert Notification.objects.filter(user=seller, category=Notification.Category.FAVORITE).exists()


@pytest.mark.django_db
def test_notifications_api_marks_read(buyer):
    n = Notification.objects.create(user=buyer, title="t", body="b")
    api = APIClient()
    api.force_authenticate(user=buyer)
    response = api.post(reverse("api-notifications-read", args=[n.pk]))
    assert response.status_code == 200
    n.refresh_from_db()
    assert n.is_read is True


@pytest.mark.django_db
def test_notifications_unread_badge(client, buyer):
    Notification.objects.create(user=buyer, title="t")
    client.force_login(buyer)
    response = client.get(reverse("notifications:unread_badge"))
    assert response.status_code == 200
    assert response.json()["unread"] == 1


@pytest.mark.django_db
def test_search_global_api(client, approved_property):
    response = client.get(reverse("api-search") + "?q=bandra&city=Mumbai")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    assert SearchHistory.objects.filter(keyword="bandra").exists()


@pytest.mark.django_db
def test_property_list_search_filters_all(client, db, seller, category):
    # Create test records
    p1 = Property.objects.create(
        title="Bandra Sea View",
        description="Premium apartment",
        price=10000000,
        property_type=Property.PropertyType.APARTMENT,
        category=category,
        bedrooms=2,
        bathrooms=2,
        area_sqft=1100,
        address="Bandra",
        city="Mumbai",
        locality="Bandra",
        pincode="400050",
        approval_status=Property.ApprovalStatus.APPROVED,
        status=Property.Status.ACTIVE,
        created_by=seller,
    )
    p2 = Property.objects.create(
        title="Delhi Villa",
        description="Luxury villa",
        price=30000000,
        property_type=Property.PropertyType.VILLA,
        category=category,
        bedrooms=4,
        bathrooms=4,
        area_sqft=3500,
        address="Saket",
        city="Delhi",
        locality="Saket",
        pincode="110017",
        approval_status=Property.ApprovalStatus.APPROVED,
        status=Property.Status.ACTIVE,
        created_by=seller,
    )
    
    # 1. Keyword search
    response = client.get(reverse("properties:list"), {"q": "Sea View"})
    assert p1.title.encode() in response.content
    assert p2.title.encode() not in response.content

    # 2. City filter
    response = client.get(reverse("properties:list"), {"city": "Delhi"})
    assert p2.title.encode() in response.content
    assert p1.title.encode() not in response.content

    # 3. Locality filter
    response = client.get(reverse("properties:list"), {"locality": "Bandra"})
    assert p1.title.encode() in response.content
    assert p2.title.encode() not in response.content

    # 4. Property type filter
    response = client.get(reverse("properties:list"), {"property_type": "villa"})
    assert p2.title.encode() in response.content
    assert p1.title.encode() not in response.content

    # 5. Min price
    response = client.get(reverse("properties:list"), {"min_price": "20000000"})
    assert p2.title.encode() in response.content
    assert p1.title.encode() not in response.content

    # 6. Max price
    response = client.get(reverse("properties:list"), {"max_price": "15000000"})
    assert p1.title.encode() in response.content
    assert p2.title.encode() not in response.content

    # 7. Bedrooms
    response = client.get(reverse("properties:list"), {"bedrooms": "3"})
    assert p2.title.encode() in response.content
    assert p1.title.encode() not in response.content

    # 8. Bathrooms
    response = client.get(reverse("properties:list"), {"bathrooms": "3"})
    assert p2.title.encode() in response.content
    assert p1.title.encode() not in response.content

    # 9. Sort
    response = client.get(reverse("properties:list"), {"sort": "price"})
    content = response.content.decode()
    assert content.index("Bandra Sea View") < content.index("Delhi Villa")
    
    response = client.get(reverse("properties:list"), {"sort": "-price"})
    content = response.content.decode()
    assert content.index("Delhi Villa") < content.index("Bandra Sea View")


@pytest.mark.django_db
def test_saved_search_create_and_run(client, buyer, approved_property):
    client.force_login(buyer)
    client.post(reverse("search:saved_create") + "?q=bandra&city=Mumbai", {"name": "Bandra watchlist"})
    saved = SavedSearch.objects.get(user=buyer)
    assert saved.query_params.get("q") == "bandra"
    response = client.get(reverse("search:saved_run", args=[saved.pk]))
    assert response.status_code == 200
    assert b"Bandra Sea View" in response.content


@pytest.mark.django_db
def test_saved_search_create_via_api(client, buyer):
    client.force_login(buyer)
    api = APIClient()
    api.force_authenticate(user=buyer)
    response = api.post(
        reverse("api-saved-searches-list"),
        {"name": "Mumbai 1cr", "query_params": {"q": "sea", "city": "Mumbai", "max_price": "25000000"}},
        format="json",
    )
    assert response.status_code == 201
    assert response.json()["matches_count"] == 0


@pytest.mark.django_db
def test_favorites_api_toggle_and_remove(client, buyer, approved_property):
    api = APIClient()
    api.force_authenticate(user=buyer)
    response = api.post(reverse("api-favorites-toggle", args=[approved_property.slug]))
    assert response.status_code == 201
    response = api.post(reverse("api-favorites-toggle", args=[approved_property.slug]))
    assert response.json()["is_favorite"] is False


@pytest.mark.django_db
def test_visits_api_create(client, buyer, approved_property):
    from django.utils import timezone

    api = APIClient()
    api.force_authenticate(user=buyer)
    response = api.post(
        reverse("api-visits-list"),
        {"property": approved_property.pk, "scheduled_at": (timezone.now() + timezone.timedelta(days=1)).isoformat()},
        format="json",
    )
    assert response.status_code == 201


@pytest.mark.django_db
def test_leads_api_create(client, seller, approved_property):
    api = APIClient()
    api.force_authenticate(user=seller)
    response = api.post(
        reverse("api-leads-list"),
        {"property": approved_property.pk, "name": "Lead", "stage": "new", "score": 80},
        format="json",
    )
    assert response.status_code == 201


@pytest.mark.django_db
def test_inquiry_list_and_status_update(client, buyer, seller, approved_property):
    from inquiries.models import Inquiry
    inquiry = Inquiry.objects.create(
        property=approved_property,
        buyer=buyer,
        name="Buyer Inquirer",
        email="buyer@example.com",
        phone="1234567890",
        message="Hello I want to buy this property."
    )
    client.force_login(seller)
    response = client.get(reverse("inquiries:list"))
    assert response.status_code == 200
    assert b"Buyer Inquirer" in response.content
    
    response = client.post(
        reverse("inquiries:update_status", args=[inquiry.pk]),
        {"status": Inquiry.Status.CONTACTED}
    )
    assert response.status_code == 302
    inquiry.refresh_from_db()
    assert inquiry.status == Inquiry.Status.CONTACTED


@pytest.mark.django_db
def test_admin_approvals_list_and_workflow(client, seller, approved_property):
    admin_user = User.objects.create_superuser(username="adminx", password="Pass@12345", email="admin@example.com")
    approved_property.approval_status = Property.ApprovalStatus.PENDING
    approved_property.save()
    
    client.force_login(admin_user)
    response = client.get(reverse("properties:approvals_list"))
    assert response.status_code == 200
    assert approved_property.title.encode() in response.content
    
    response = client.post(reverse("properties:approve", args=[approved_property.slug]))
    assert response.status_code == 302
    approved_property.refresh_from_db()
    assert approved_property.approval_status == Property.ApprovalStatus.APPROVED
    
    response = client.post(reverse("properties:reject", args=[approved_property.slug]), {"reason": "Revoked listing"})
    assert response.status_code == 302
    approved_property.refresh_from_db()
    assert approved_property.approval_status == Property.ApprovalStatus.REJECTED
    assert approved_property.rejection_reason == "Revoked listing"


@pytest.mark.django_db
def test_filename_safe_sanitization():
    from properties.models import get_short_sanitized_filename
    long_name = "this_is_an_extremely_long_filename_that_has_a_lot_of_characters_and_goes_well_over_one_hundred_characters_to_simulate_a_broken_database_insert.jpg"
    short_name = get_short_sanitized_filename(long_name)
    assert len(short_name) <= 50
    assert short_name.endswith(".jpg")


@pytest.mark.django_db
def test_avatar_filename_safe_sanitization():
    import os
    from accounts.models import upload_avatar
    long_name = "user_avatar_that_has_a_lot_of_characters_and_goes_well_over_one_hundred_characters_to_simulate_a_broken_database_insert.png"
    result = upload_avatar(None, long_name)
    assert result.startswith(os.path.join("avatars", "")) or result.startswith("avatars/")
    filename = os.path.basename(result)
    assert len(filename) <= 50
    assert filename.endswith(".png")


@pytest.mark.django_db
def test_download_audit_logs(client):
    from analytics.models import AuditLog
    admin_user = User.objects.create_superuser(username="admin_test", password="Pass@12345", email="admin@example.com")
    AuditLog.objects.create(actor=admin_user, action="test_action", object_type="Property", object_id="123")
    client.force_login(admin_user)
    response = client.get(reverse("reports:download_audit_logs"))
    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv"
    assert b"test_action" in response.content


@pytest.mark.django_db
def test_property_image_size_validation(seller, category):
    from django.core.files.uploadedfile import SimpleUploadedFile
    from properties.forms import PropertyForm
    from PIL import Image
    from io import BytesIO
    
    def generate_image(size):
        f = BytesIO()
        img = Image.new('RGB', (1, 1))
        img.save(f, 'jpeg')
        f.write(b'\x00' * max(0, size - f.tell()))
        f.seek(0)
        return f.getvalue()

    form_data = {
        "title": "Bandra Sea View",
        "description": "Premium apartment",
        "price": 10000000,
        "property_type": Property.PropertyType.APARTMENT,
        "category": category.id,
        "bedrooms": 2,
        "bathrooms": 2,
        "area_sqft": 1100,
        "parking": 1,
        "status": "active",
        "address": "Bandra",
        "city": "Mumbai",
        "locality": "Bandra",
        "pincode": "400050",
    }
    
    # 1. 11MB cover image (Should be allowed)
    large_cover = SimpleUploadedFile("cover.jpg", generate_image(11 * 1024 * 1024), content_type="image/jpeg")
    form = PropertyForm(data=form_data, files={"cover_image": large_cover})
    assert form.is_valid()
    
    # 2. 9MB cover image (valid)
    valid_cover = SimpleUploadedFile("cover.jpg", generate_image(9 * 1024 * 1024), content_type="image/jpeg")
    form = PropertyForm(data=form_data, files={"cover_image": valid_cover})
    assert form.is_valid()


@pytest.mark.django_db
def test_registration_sends_emails(client):
    from django.core import mail
    mail.outbox.clear()
    
    response = client.post(
        reverse("accounts:register"),
        {
            "username": "newuseremail",
            "email": "newuser@example.com",
            "role": User.Role.BUYER,
            "password1": "Pass@12345",
            "password2": "Pass@12345",
        },
    )
    assert response.status_code == 302
    assert len(mail.outbox) == 2
    assert "Welcome" in mail.outbox[0].subject
    assert "Verify" in mail.outbox[1].subject


@pytest.mark.django_db
def test_password_reset_views_and_emails(client, buyer):
    from django.core import mail
    mail.outbox.clear()
    
    buyer.email = "buyer@example.com"
    buyer.save()
    
    response = client.post(reverse("accounts:password_reset"), {"email": buyer.email})
    assert response.status_code == 302
    assert len(mail.outbox) == 1
    assert "password reset" in mail.outbox[0].subject.lower()


@pytest.mark.django_db
def test_email_change_triggers_verification(client, buyer):
    from django.core import mail
    mail.outbox.clear()
    
    buyer.email = "buyer@example.com"
    buyer.save()
    
    client.force_login(buyer)
    response = client.post(
        reverse("accounts:profile"),
        {
            "first_name": "New",
            "last_name": "Buyer",
            "email": "changed_email@example.com",
            "phone": "9999999999",
            "city": "Mumbai",
            "locality": "Bandra",
            "bio": "New bio",
            "agency_name": "",
            "license_number": "",
        }
    )
    assert response.status_code == 302
    buyer.refresh_from_db()
    assert buyer.is_verified is False
    assert len(mail.outbox) == 1
    assert "Verify" in mail.outbox[0].subject


@pytest.mark.django_db
def test_verify_email_flow(client, buyer):
    from django.core import signing
    buyer.is_verified = False
    buyer.save()
    
    token = signing.dumps({"user_id": buyer.pk, "email": buyer.email})
    response = client.get(reverse("accounts:verify_email", args=[token]))
    assert response.status_code == 302
    buyer.refresh_from_db()
    assert buyer.is_verified is True


@pytest.mark.django_db
def test_seller_favorites_page_and_dashboard_integration(client, seller, approved_property, buyer):
    from favorites.models import Favorite
    Favorite.objects.create(user=buyer, property=approved_property)
    
    client.force_login(seller)
    response = client.get(reverse("favorites:seller_favorites"))
    assert response.status_code == 200
    assert approved_property.title.encode() in response.content
    assert buyer.username.encode() in response.content

    response = client.get(reverse("accounts:seller_dashboard"))
    assert response.status_code == 200
    assert approved_property.title.encode() in response.content


@pytest.mark.django_db
def test_access_control_route_restrictions(client, buyer, seller):
    for url in [
        reverse("accounts:buyer_dashboard"),
        reverse("accounts:seller_dashboard"),
        reverse("accounts:admin_dashboard"),
        reverse("reports:home"),
        reverse("notifications:list"),
        reverse("accounts:profile")
    ]:
        response = client.get(url)
        assert response.status_code == 302
        
    client.force_login(buyer)
    response = client.get(reverse("reports:home"))
    assert response.status_code == 403
    response = client.get(reverse("accounts:admin_dashboard"))
    assert response.status_code == 302
    assert response.url == reverse("accounts:buyer_dashboard")
    
    response = client.get(reverse("accounts:seller_dashboard"))
    assert response.status_code == 302
    assert response.url == reverse("accounts:buyer_dashboard")

    client.force_login(seller)
    response = client.get(reverse("accounts:admin_dashboard"))
    assert response.status_code == 302
    assert response.url == reverse("accounts:seller_dashboard")
    
    response = client.get(reverse("accounts:buyer_dashboard"))
    assert response.status_code == 302
    assert response.url == reverse("accounts:seller_dashboard")



@pytest.mark.django_db
def test_property_lifecycle_workflow(client, seller, category):
    admin_user = User.objects.create_superuser(username="adminy", password="Pass@12345", email="adminy@example.com")
    
    # 1. Create - Seller creates property
    client.force_login(seller)
    response = client.post(
        reverse("properties:create"),
        {
            "title": "Lifecycle Mansion",
            "description": "Premium test property for lifecycle workflow.",
            "price": 50000000,
            "property_type": Property.PropertyType.VILLA,
            "category": category.id,
            "bedrooms": 5,
            "bathrooms": 5,
            "area_sqft": 4500,
            "status": Property.Status.PENDING,
            "address": "Juhu",
            "city": "Mumbai",
            "locality": "Juhu",
            "pincode": "400049",
            "parking": 2,
        }
    )
    assert response.status_code == 302
    prop = Property.objects.get(title="Lifecycle Mansion")
    assert prop.status == Property.Status.PENDING
    assert prop.approval_status == Property.ApprovalStatus.PENDING
    
    # Verify not public
    response = client.get(reverse("properties:list"))
    assert prop not in response.context["properties"]

    # 2. Approve - Admin approves property
    client.force_login(admin_user)
    response = client.post(reverse("properties:approve", args=[prop.slug]))
    assert response.status_code == 302
    prop.refresh_from_db()
    assert prop.status == Property.Status.APPROVED
    assert prop.approval_status == Property.ApprovalStatus.APPROVED

    # Verify not public (since status is APPROVED, not yet ACTIVE)
    response = client.get(reverse("properties:list"))
    assert prop not in response.context["properties"]

    # 3. Active - Seller activates property
    client.force_login(seller)
    response = client.post(reverse("properties:activate", args=[prop.slug]))
    assert response.status_code == 302
    prop.refresh_from_db()
    assert prop.status == Property.Status.ACTIVE

    # Verify public in default search
    response = client.get(reverse("properties:list"))
    assert prop in response.context["properties"]

    # 4. Sold - Seller marks Active property as Sold
    response = client.post(reverse("properties:mark_sold", args=[prop.slug]))
    assert response.status_code == 302
    prop.refresh_from_db()
    assert prop.status == Property.Status.SOLD
    assert prop.sold_date is not None

    # Verify sold badge is shown
    response = client.get(reverse("properties:list"), {"status": "sold"})
    assert prop in response.context["properties"]
    assert b"SOLD" in response.content

    # 5. Closed - Seller marks Active property as Closed
    # Reopen to Active first
    prop.status = Property.Status.ACTIVE
    prop.save()
    response = client.post(reverse("properties:mark_closed", args=[prop.slug]))
    assert response.status_code == 302
    prop.refresh_from_db()
    assert prop.status == Property.Status.CLOSED

    # Verify hidden from public
    response = client.get(reverse("properties:list"))
    assert prop not in response.context["properties"]
    
    # 6. Reopen Closed property
    response = client.post(reverse("properties:reopen", args=[prop.slug]))
    assert response.status_code == 302
    prop.refresh_from_db()
    assert prop.status == Property.Status.ACTIVE

    # 7. Check reports View
    client.force_login(admin_user)
    response = client.get(reverse("reports:home"))
    assert response.status_code == 200
    assert b"Property Lifecycle Report" in response.content


@pytest.mark.django_db
def test_profile_phone_and_email_validation(client, buyer):
    from accounts.forms import UserForm
    client.force_login(buyer)

    # 1. Invalid phone number format (starts with 5)
    form_data = {
        "first_name": buyer.first_name,
        "last_name": buyer.last_name,
        "email": "valid_email@example.com",
        "phone": "5551234567"
    }
    form = UserForm(data=form_data, instance=buyer)
    assert not form.is_valid()
    assert "phone" in form.errors

    # 2. Valid phone number format (exactly 10 digits, starts with 9)
    form_data["phone"] = "9876543210"
    form = UserForm(data=form_data, instance=buyer)
    assert form.is_valid()

    # 3. Empty email address is prevented
    form_data_empty_email = form_data.copy()
    form_data_empty_email["email"] = ""
    form_empty = UserForm(data=form_data_empty_email, instance=buyer)
    assert not form_empty.is_valid()
    assert "email" in form_empty.errors


def test_ai_property_match_view(client, buyer, approved_property):
    from django.urls import reverse
    from properties.models import Property

    # 1. Unauthenticated gets redirected
    url = reverse("properties:ai_match")
    response = client.get(url)
    assert response.status_code == 302

    # 2. Authenticated GET renders form
    client.force_login(buyer)
    response = client.get(url)
    assert response.status_code == 200
    assert b"Find Your Perfect Property" in response.content

    # Create additional properties to verify score ranking differences
    # approved_property: price is probably 1.5 Cr or 15000000. Let's verify price.
    Property.objects.create(
        title="Premium Villa Pune",
        slug="premium-villa-pune",
        description="Luxury villa",
        price=18000000, # 1.8 Cr
        property_type="villa",
        category=approved_property.category,
        bedrooms=4,
        bathrooms=4,
        area_sqft=3200,
        city="Pune",
        locality="Kalyani Nagar",
        status=Property.Status.ACTIVE,
        approval_status=Property.ApprovalStatus.APPROVED,
        created_by=buyer,
        is_featured=True
    )
    Property.objects.create(
        title="Budget Apartment Pune",
        slug="budget-apartment-pune",
        description="Cozy apartment",
        price=8000000, # 80 Lakhs
        property_type="apartment",
        category=approved_property.category,
        bedrooms=2,
        bathrooms=2,
        area_sqft=1100,
        city="Pune",
        locality="Hinjewadi",
        status=Property.Status.ACTIVE,
        approval_status=Property.ApprovalStatus.APPROVED,
        created_by=buyer,
        is_featured=False
    )

    # 3. Authenticated POST returns matching cards JSON sorted by score
    post_data = {
        "budget": "2 Cr",
        "city": "Pune",
        "bedrooms": "2",
        "purpose": "family living"
    }
    response = client.post(url, post_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "html" in data
    # Both Pune properties are returned as they are under 2.2 Cr (1.1x of 2 Cr)
    assert "Premium Villa Pune" in data["html"]
    assert "Budget Apartment Pune" in data["html"]
    
    # 4. Strict maximum budget filtering test
    post_data_strict_budget = {
        "budget": "1 Cr", # 10000000
        "city": "Pune",
        "bedrooms": "2",
        "purpose": "investment"
    }
    response = client.post(url, post_data_strict_budget)
    assert response.status_code == 200
    data_strict = response.json()
    # p2 (1.8 Cr) is > 1.1x of 1 Cr budget limit, so it must NOT be recommended!
    assert "Budget Apartment Pune" in data_strict["html"]
    assert "Premium Villa Pune" not in data_strict["html"]

    # 5. Empty state when no properties exist/match
    post_data_no_match = {
        "budget": "1 Cr",
        "city": "NonExistentCityX",
        "bedrooms": "4",
        "purpose": "investment"
    }
    response = client.post(url, post_data_no_match)
    assert response.status_code == 200
    data_no_match = response.json()
    assert "No properties currently satisfy your requirements." in data_no_match["html"]
    assert "Browse All Properties" in data_no_match["html"]


def test_ai_property_insights_view(client, buyer, approved_property):
    from django.urls import reverse
    from properties.models import Property

    # 1. Redirect if unauthenticated
    url = reverse("properties:ai_insights", args=[approved_property.slug])
    response = client.post(url)
    assert response.status_code == 302

    client.force_login(buyer)

    # 2. Authenticated POST checks for detailed custom attributes
    response = client.post(url)
    assert response.status_code == 200
    data = response.json()
    
    assert "score" in data
    assert "market_position" in data
    assert "strengths" in data
    assert "outlook_short" in data
    assert "outlook_long" in data
    assert "suitability_best" in data
    assert "suitability_less" in data
    assert "considerations" in data

    # 3. Create properties in different cities to verify score differentials
    p_mumbai = Property.objects.create(
        title="Luxury Penthouse Mumbai",
        slug="luxury-penthouse-mumbai",
        description="Overlooking sea link",
        price=45000000, # 4.5 Cr
        property_type="apartment",
        category=approved_property.category,
        bedrooms=3,
        bathrooms=3,
        area_sqft=2200,
        city="Mumbai",
        locality="Worli",
        status=Property.Status.ACTIVE,
        approval_status=Property.ApprovalStatus.APPROVED,
        created_by=buyer,
        is_featured=True
    )
    p_nashik = Property.objects.create(
        title="Agro Villa Nashik",
        slug="agro-villa-nashik",
        description="Vineyard adjacent",
        price=9500000, # 95 Lakhs
        property_type="villa",
        category=approved_property.category,
        bedrooms=2,
        bathrooms=2,
        area_sqft=1100,
        city="Nashik",
        locality="Gangapur Road",
        status=Property.Status.ACTIVE,
        approval_status=Property.ApprovalStatus.APPROVED,
        created_by=buyer,
        is_featured=False
    )

    # Fetch insights for Mumbai (Premium location + featured)
    url_mumbai = reverse("properties:ai_insights", args=[p_mumbai.slug])
    res_mumbai = client.post(url_mumbai).json()
    
    # Fetch insights for Nashik (Affordable price + non-featured)
    url_nashik = reverse("properties:ai_insights", args=[p_nashik.slug])
    res_nashik = client.post(url_nashik).json()

    # Scores must reflect the pre-calculated attributes accurately
    assert res_mumbai["score"] > res_nashik["score"]
    assert res_mumbai["market_position"] in ["Prime", "Strong"]
    assert "Mumbai" in res_mumbai["outlook_short"] or "Mumbai" in res_mumbai["strengths"][0]
    assert "Nashik" in res_nashik["outlook_short"] or "Nashik" in res_nashik["strengths"][0]


@pytest.mark.django_db
def test_inquiry_owner_and_admin_restrictions(client, buyer, seller, approved_property):
    from django.contrib import messages
    
    # Test owner restriction: seller is the owner of approved_property
    client.force_login(seller)
    url = reverse("inquiries:create", args=[approved_property.slug])
    response = client.post(
        url,
        {"name": "Seller", "email": "seller@example.com", "phone": "8888888888", "message": "Can I buy my own house?"},
    )
    assert response.status_code == 302
    msgs = list(messages.get_messages(response.wsgi_request))
    assert any("You cannot inquire on your own listing." in msg.message for msg in msgs)

    # Test admin restriction
    admin_user = User.objects.create_superuser(username="admin_user", email="admin@example.com", password="password")
    client.force_login(admin_user)
    response = client.post(
        url,
        {"name": "Admin", "email": "admin@example.com", "phone": "7777777777", "message": "Admin inquiry"},
    )
    assert response.status_code == 302
    msgs = list(messages.get_messages(response.wsgi_request))
    assert any("Administrators cannot submit property inquiries." in msg.message for msg in msgs)






