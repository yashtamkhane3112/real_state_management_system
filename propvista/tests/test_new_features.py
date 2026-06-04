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
