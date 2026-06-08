from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from inquiries.models import Inquiry
from properties.models import Category, Property


class CoreFlowTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Residential", slug="residential")
        self.seller = User.objects.create_user(username="sellerx", password="Pass@12345", role=User.Role.SELLER)
        self.buyer = User.objects.create_user(username="buyerx", password="Pass@12345", role=User.Role.BUYER)
        self.property = Property.objects.create(
            title="Bandra Sea View",
            description="Premium apartment",
            price=10000000,
            property_type=Property.PropertyType.APARTMENT,
            category=self.category,
            bedrooms=2,
            bathrooms=2,
            area_sqft=1100,
            address="Bandra",
            city="Mumbai",
            locality="Bandra",
            pincode="400050",
            approval_status=Property.ApprovalStatus.APPROVED,
            created_by=self.seller,
        )

    def test_registration(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newbuyer",
                "email": "newbuyer@example.com",
                "role": User.Role.BUYER,
                "password1": "Pass@12345",
                "password2": "Pass@12345",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="newbuyer").exists())

    def test_login(self):
        response = self.client.post(reverse("accounts:login"), {"username": "buyerx", "password": "Pass@12345"})
        self.assertEqual(response.status_code, 302)

    def test_property_search_filters(self):
        response = self.client.get(reverse("properties:list"), {"city": "Mumbai", "min_price": "5000000"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bandra Sea View")

    def test_inquiry_creation(self):
        self.client.force_login(self.buyer)
        response = self.client.post(
            reverse("inquiries:create", args=[self.property.slug]),
            {"name": "Buyer X", "email": "buyer@example.com", "phone": "9999999999", "message": "Interested"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Inquiry.objects.count(), 1)

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("accounts:buyer_dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_seller_can_open_create_form(self):
        self.client.force_login(self.seller)
        response = self.client.get(reverse("properties:create"))
        self.assertEqual(response.status_code, 200)
