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
def test_download_audit_logs(client, seller):
    from analytics.models import AuditLog
    AuditLog.objects.create(actor=seller, action="test_action", object_type="Property", object_id="123")
    client.force_login(seller)
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
    
    # 1. 11MB cover image
    large_cover = SimpleUploadedFile("cover.jpg", generate_image(11 * 1024 * 1024), content_type="image/jpeg")
    form = PropertyForm(data=form_data, files={"cover_image": large_cover})
    assert not form.is_valid()
    assert "cover_image" in form.errors
    
    # 2. 9MB cover image (valid)
    valid_cover = SimpleUploadedFile("cover.jpg", generate_image(9 * 1024 * 1024), content_type="image/jpeg")
    form = PropertyForm(data=form_data, files={"cover_image": valid_cover})
    assert form.is_valid()
    
    # 3. 11MB gallery image
    large_gallery = SimpleUploadedFile("gallery.jpg", generate_image(11 * 1024 * 1024), content_type="image/jpeg")
    form = PropertyForm(data=form_data, files={"gallery_images": large_gallery})
    assert not form.is_valid()


