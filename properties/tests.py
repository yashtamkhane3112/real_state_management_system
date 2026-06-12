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

    def test_property_visibility_flow(self):
        # 1. Create a new pending property
        pending_prop = Property.objects.create(
            title="Pending Penthouse",
            description="Pending penthouse details",
            price=20000000,
            property_type=Property.PropertyType.APARTMENT,
            category=self.category,
            bedrooms=3,
            bathrooms=3,
            area_sqft=2200,
            address="Juhu",
            city="Mumbai",
            locality="Juhu",
            pincode="400049",
            approval_status=Property.ApprovalStatus.PENDING,
            created_by=self.seller,
        )
        
        # Verify it does not appear in public listings
        response = self.client.get(reverse("properties:list"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Pending Penthouse")
        
        # 2. Approve the property
        pending_prop.status = Property.Status.APPROVED
        pending_prop.save()
        
        # 3. Activate the property
        pending_prop.status = Property.Status.ACTIVE
        pending_prop.save()
        
        # Verify it now appears in public listings
        response = self.client.get(reverse("properties:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pending Penthouse")

    def test_multi_image_upload(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        from properties.models import PropertyImage
        self.client.force_login(self.seller)
        
        # Test uploading 1 image
        img1 = SimpleUploadedFile("test_image1.jpg", b"file_content_1", content_type="image/jpeg")
        response = self.client.post(
            reverse("properties:create"),
            {
                "title": "One Image Villa",
                "description": "One image villa details",
                "price": 15000000,
                "property_type": Property.PropertyType.VILLA,
                "category": self.category.id,
                "bedrooms": 3,
                "bathrooms": 3,
                "area_sqft": 1800,
                "address": "Bandra",
                "city": "Mumbai",
                "locality": "Bandra",
                "pincode": "400050",
                "status": "pending",
                "parking": 1,
                "gallery_images": [img1]
            }
        )
        self.assertEqual(response.status_code, 302)
        prop1 = Property.objects.get(title="One Image Villa")
        self.assertEqual(PropertyImage.objects.filter(property=prop1).count(), 1)

        # Test uploading 3 images
        img1 = SimpleUploadedFile("test_image1.jpg", b"file_content_1", content_type="image/jpeg")
        img2 = SimpleUploadedFile("test_image2.jpg", b"file_content_2", content_type="image/jpeg")
        img3 = SimpleUploadedFile("test_image3.jpg", b"file_content_3", content_type="image/jpeg")
        response = self.client.post(
            reverse("properties:create"),
            {
                "title": "Three Image Villa",
                "description": "Three image villa details",
                "price": 15000000,
                "property_type": Property.PropertyType.VILLA,
                "category": self.category.id,
                "bedrooms": 3,
                "bathrooms": 3,
                "area_sqft": 1800,
                "address": "Bandra",
                "city": "Mumbai",
                "locality": "Bandra",
                "pincode": "400050",
                "status": "pending",
                "parking": 1,
                "gallery_images": [img1, img2, img3]
            }
        )
        self.assertEqual(response.status_code, 302)
        prop3 = Property.objects.get(title="Three Image Villa")
        self.assertEqual(PropertyImage.objects.filter(property=prop3).count(), 3)

        # Test uploading 5 images
        img1 = SimpleUploadedFile("test_image1.jpg", b"file_content_1", content_type="image/jpeg")
        img2 = SimpleUploadedFile("test_image2.jpg", b"file_content_2", content_type="image/jpeg")
        img3 = SimpleUploadedFile("test_image3.jpg", b"file_content_3", content_type="image/jpeg")
        img4 = SimpleUploadedFile("test_image4.jpg", b"file_content_4", content_type="image/jpeg")
        img5 = SimpleUploadedFile("test_image5.jpg", b"file_content_5", content_type="image/jpeg")
        response = self.client.post(
            reverse("properties:create"),
            {
                "title": "Five Image Villa",
                "description": "Five image villa details",
                "price": 15000000,
                "property_type": Property.PropertyType.VILLA,
                "category": self.category.id,
                "bedrooms": 3,
                "bathrooms": 3,
                "area_sqft": 1800,
                "address": "Bandra",
                "city": "Mumbai",
                "locality": "Bandra",
                "pincode": "400050",
                "status": "pending",
                "parking": 1,
                "gallery_images": [img1, img2, img3, img4, img5]
            }
        )
        self.assertEqual(response.status_code, 302)
        prop5 = Property.objects.get(title="Five Image Villa")
        self.assertEqual(PropertyImage.objects.filter(property=prop5).count(), 5)
