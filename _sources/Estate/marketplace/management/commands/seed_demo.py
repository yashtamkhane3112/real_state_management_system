from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from marketplace.models import BuyerProfile, Inquiry, Profile, Property, PropertyImage, SellerProfile, Transaction


class Command(BaseCommand):
    help = 'Create demo users and sample properties for the sales/purchase mini-project.'

    def handle(self, *args, **options):
        admin, _ = User.objects.get_or_create(username='admin', defaults={'email': 'admin@example.com', 'first_name': 'Super', 'last_name': 'Admin'})
        if not admin.is_superuser:
            admin.is_staff = True
            admin.is_superuser = True
            admin.set_password('admin12345')
            admin.save()
        admin.profile.role = Profile.Role.ADMIN
        admin.profile.city = 'Nashik'
        admin.profile.phone = '9000000001'
        admin.profile.save()

        seller, created = User.objects.get_or_create(username='seller', defaults={'email': 'seller@example.com', 'first_name': 'Arjun', 'last_name': 'Seller'})
        if created:
            seller.set_password('seller12345')
            seller.save()
        seller.profile.role = Profile.Role.SELLER
        seller.profile.city = 'Nashik'
        seller.profile.phone = '9000000002'
        seller.profile.save()
        SellerProfile.objects.get_or_create(user=seller, defaults={'agency_name': 'GreenKey Properties', 'verified': True})

        buyer, created = User.objects.get_or_create(username='buyer', defaults={'email': 'buyer@example.com', 'first_name': 'Pratik', 'last_name': 'Buyer'})
        if created:
            buyer.set_password('buyer12345')
            buyer.save()
        buyer.profile.role = Profile.Role.BUYER
        buyer.profile.city = 'Nashik'
        buyer.profile.phone = '9000000003'
        buyer.profile.save()
        BuyerProfile.objects.update_or_create(user=buyer, defaults={'preferred_city': 'Nashik', 'min_budget': Decimal('3000000'), 'max_budget': Decimal('9000000')})

        samples = [
            {
                'title': '2BHK Premium Flat in Indira Nagar', 'property_type': Property.PropertyType.FLAT, 'city': 'Nashik',
                'price': Decimal('5200000'), 'area_sqft': 960, 'bedrooms': 2, 'bathrooms': 2, 'status': Property.Status.APPROVED,
                'address': 'Indira Nagar, Nashik, Maharashtra',
                'cover_image_url': 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80',
            },
            {
                'title': 'Modern Bungalow near Gangapur Road', 'property_type': Property.PropertyType.BUNGALOW, 'city': 'Nashik',
                'price': Decimal('14500000'), 'area_sqft': 2400, 'bedrooms': 4, 'bathrooms': 4, 'status': Property.Status.APPROVED,
                'address': 'Gangapur Road, Nashik, Maharashtra',
                'cover_image_url': 'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=1200&q=80',
            },
            {
                'title': 'Commercial Shop in College Road', 'property_type': Property.PropertyType.SHOP, 'city': 'Nashik',
                'price': Decimal('6800000'), 'area_sqft': 520, 'bedrooms': 0, 'bathrooms': 1, 'status': Property.Status.PENDING,
                'address': 'College Road, Nashik, Maharashtra',
                'cover_image_url': 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1200&q=80',
            },
            {
                'title': 'Open Plot in Pune Growth Zone', 'property_type': Property.PropertyType.PLOT, 'city': 'Pune',
                'price': Decimal('7500000'), 'area_sqft': 1800, 'bedrooms': 0, 'bathrooms': 0, 'status': Property.Status.APPROVED,
                'address': 'Wagholi, Pune, Maharashtra',
                'cover_image_url': 'https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1200&q=80',
            },
            {
                'title': 'Office Space in Mumbai Business District', 'property_type': Property.PropertyType.OFFICE, 'city': 'Mumbai',
                'price': Decimal('22500000'), 'area_sqft': 1400, 'bedrooms': 0, 'bathrooms': 2, 'status': Property.Status.SOLD,
                'address': 'Andheri East, Mumbai, Maharashtra',
                'cover_image_url': 'https://images.unsplash.com/photo-1497366754035-f200968a6e72?auto=format&fit=crop&w=1200&q=80',
            },
        ]
        for item in samples:
            prop, _ = Property.objects.get_or_create(title=item['title'], seller=seller, defaults={**item, 'description': 'A clean and verified property listing suitable for buyer inquiry and sale/purchase record management.'})
            gallery_urls = [
                'https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1600210492493-0946911123ea?auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1600607688969-a5bfcd646154?auto=format&fit=crop&w=1200&q=80',
            ]
            if not prop.gallery_images.exists():
                for i, url in enumerate(gallery_urls, start=1):
                    PropertyImage.objects.create(property=prop, image_url=url, caption=f'Gallery view {i}')

        first_property = Property.objects.filter(status=Property.Status.APPROVED).first()
        if first_property:
            Inquiry.objects.get_or_create(
                property=first_property,
                buyer=buyer,
                seller=seller,
                defaults={'buyer_name': 'Pratik Buyer', 'email': 'buyer@example.com', 'phone': '9000000003', 'message': 'I am interested in this property. Please share more details.'},
            )
        sold_property = Property.objects.filter(status=Property.Status.SOLD).first()
        if sold_property:
            Transaction.objects.get_or_create(
                property=sold_property,
                buyer=buyer,
                seller=seller,
                defaults={'final_price': sold_property.price, 'transaction_date': date.today(), 'status': Transaction.Status.COMPLETED, 'notes': 'Demo completed sale and purchase record.'},
            )
        self.stdout.write(self.style.SUCCESS('Demo data created successfully.'))
