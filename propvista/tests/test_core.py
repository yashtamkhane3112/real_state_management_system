import pytest
from django.urls import reverse

from accounts.models import User
from properties.models import Category, Property


@pytest.fixture
def category(db):
    return Category.objects.create(name="Residential", slug="residential")


@pytest.fixture
def seller(db):
    return User.objects.create_user(username="sellerx", password="Pass@12345", role=User.Role.SELLER)


@pytest.mark.django_db
def test_registration_page(client):
    response = client.post(
        reverse("accounts:register"),
        {
            "username": "buyerx",
            "email": "buyerx@example.com",
            "role": User.Role.BUYER,
            "password1": "Pass@12345",
            "password2": "Pass@12345",
        },
    )
    assert response.status_code == 302
    assert User.objects.filter(username="buyerx").exists()


@pytest.mark.django_db
def test_login(client):
    User.objects.create_user(username="buyerx", password="Pass@12345", role=User.Role.BUYER)
    response = client.post(reverse("accounts:login"), {"username": "buyerx", "password": "Pass@12345"})
    assert response.status_code == 302


@pytest.mark.django_db
def test_property_search(client, seller, category):
    Property.objects.create(
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
        created_by=seller,
    )
    response = client.get(reverse("properties:list"), {"city": "Mumbai", "min_price": "5000000"})
    assert response.status_code == 200
    assert b"Bandra Sea View" in response.content


@pytest.mark.django_db
def test_dashboard_requires_login(client):
    response = client.get(reverse("accounts:buyer_dashboard"))
    assert response.status_code == 302

