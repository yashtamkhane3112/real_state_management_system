from decimal import Decimal
from random import choice, randint

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Profile, User
from favorites.models import Favorite
from inquiries.models import Inquiry
from leads.models import Lead
from properties.models import Amenity, Category, Property
from visits.models import Visit


class Command(BaseCommand):
    help = "Create demo users, properties, inquiries, visits, leads, categories, and amenities."

    def handle(self, *args, **options):
        users = {
            "buyer": self.user("buyer", User.Role.BUYER, "buyer@propvista.local"),
            "seller": self.user("seller", User.Role.SELLER, "seller@propvista.local"),
            "admin": self.user("admin", User.Role.ADMIN, "admin@propvista.local", is_staff=True),
            "superadmin": self.user("superadmin", User.Role.ADMIN, "superadmin@propvista.local", is_staff=True, is_superuser=True),
        }
        categories = [Category.objects.get_or_create(name=name, defaults={"slug": name.lower().replace(" ", "-")})[0] for name in ["Residential", "Luxury", "Commercial", "Land"]]
        amenities = [Amenity.objects.get_or_create(name=name)[0] for name in ["Gym", "Pool", "Security", "Parking", "Garden", "Clubhouse", "Metro Nearby", "Power Backup"]]
        cities = [("Mumbai", "Bandra", Decimal("19.0544"), Decimal("72.8406")), ("Bengaluru", "Whitefield", Decimal("12.9698"), Decimal("77.7500")), ("Pune", "Hinjewadi", Decimal("18.5913"), Decimal("73.7389"))]
        for i in range(1, 21):
            city, locality, lat, lng = choice(cities)
            owner = users["seller"]
            prop, _ = Property.objects.get_or_create(
                title=f"{locality} Signature Residence {i}",
                city=city,
                locality=locality,
                defaults={
                    "description": "A premium, well-connected property with modern amenities, natural light, and strong investment potential.",
                    "price": Decimal(randint(75, 450)) * Decimal("100000"),
                    "property_type": choice([v for v, _ in Property.PropertyType.choices]),
                    "category": choice(categories),
                    "bedrooms": randint(1, 5),
                    "bathrooms": randint(1, 4),
                    "area_sqft": randint(650, 4200),
                    "furnishing": choice(["Unfurnished", "Semi-furnished", "Fully furnished"]),
                    "year_built": randint(2012, 2026),
                    "parking": randint(0, 3),
                    "latitude": lat + Decimal(randint(-30, 30)) / Decimal("10000"),
                    "longitude": lng + Decimal(randint(-30, 30)) / Decimal("10000"),
                    "address": f"Tower {i}, {locality}, {city}",
                    "pincode": str(randint(400001, 560999)),
                    "status": Property.Status.ACTIVE,
                    "approval_status": Property.ApprovalStatus.APPROVED if i != 20 else Property.ApprovalStatus.PENDING,
                    "is_featured": i <= 6,
                    "view_count": randint(30, 900),
                    "created_by": owner,
                },
            )
            prop.amenities.set(amenities[: randint(3, len(amenities))])
        first_props = list(Property.objects.all()[:6])
        for prop in first_props:
            Favorite.objects.get_or_create(user=users["buyer"], property=prop)
            Inquiry.objects.get_or_create(
                property=prop,
                buyer=users["buyer"],
                name="Demo Buyer",
                email="buyer@propvista.local",
                phone="9999999999",
                message="I would like to schedule a visit.",
            )
            Visit.objects.get_or_create(property=prop, buyer=users["buyer"], scheduled_at=timezone.now() + timezone.timedelta(days=3))
            Lead.objects.get_or_create(owner=users["seller"], property=prop, name="Investor Lead", phone="9888888888", email="lead@propvista.local")
        self.stdout.write(self.style.SUCCESS("Seed complete. Demo password for all users: Pass@12345"))

    def user(self, username, role, email, **flags):
        user, created = User.objects.get_or_create(username=username, defaults={"email": email, "role": role, **flags})
        if created:
            user.set_password("Pass@12345")
            user.first_name = username.title()
            user.save()
        Profile.objects.get_or_create(user=user, defaults={"city": "Mumbai"})
        return user

