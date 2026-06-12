import os
import sys
import django
from django.test import Client
from django.urls import reverse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'propvista.settings')
django.setup()

from django.conf import settings
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

from accounts.models import User
from properties.models import Property, Category

def run_validation_checks():
    client = Client()
    print("--- STARTING VALIDATION TESTS ---")
    
    # 1. Phone number validations
    print("\n[Phone Validation Checks]")
    
    # Register invalid phone
    reg_url = reverse('accounts:register')
    bad_phones = ['123', 'abcd123456', '98765', '987654321012', '98-7654-3210', '98765 43210']
    for ph in bad_phones:
        User.objects.filter(username='temp_val_user').delete()
        resp = client.post(reg_url, {
            'username': 'temp_val_user',
            'email': 'temp_val@example.com',
            'password1': 'Pass@12345',
            'password2': 'Pass@12345',
            'phone': ph,
            'role': User.Role.BUYER
        })
        html = resp.content.decode('utf-8')
        if "Phone number must be exactly 10 digits and start with 6, 7, 8, or 9." in html:
            print(f"  Register with phone '{ph}': REJECTED (PASS)")
        else:
            print(f"  Register with phone '{ph}': ALLOWED (FAIL)")

    # 2. Property detail fields validation (price, beds, baths, area)
    print("\n[Property Field Validation Checks]")
    create_url = reverse('properties:create')
    seller_user = User.objects.filter(role=User.Role.SELLER).first()
    client.force_login(seller_user)
    cat = Category.objects.first()
    
    # Invalid Price <= 0
    resp = client.post(create_url, {
        'title': 'Test Invalid Property',
        'price': 0,
        'property_type': Property.PropertyType.APARTMENT,
        'category': cat.id,
        'bedrooms': 2,
        'bathrooms': 2,
        'area_sqft': 1000,
        'address': 'Test address',
        'city': 'Mumbai',
        'locality': 'Bandra',
        'pincode': '400050',
    })
    html = resp.content.decode('utf-8')
    print(f"  Price = 0: {'REJECTED (PASS)' if 'Price must be greater than 0.' in html else 'ALLOWED (FAIL)'}")

    # Invalid Bedrooms < 0
    resp = client.post(create_url, {
        'title': 'Test Invalid Property',
        'price': 100000,
        'property_type': Property.PropertyType.APARTMENT,
        'category': cat.id,
        'bedrooms': -1,
        'bathrooms': 2,
        'area_sqft': 1000,
        'address': 'Test address',
        'city': 'Mumbai',
        'locality': 'Bandra',
        'pincode': '400050',
    })
    html = resp.content.decode('utf-8')
    print(f"  Bedrooms = -1: {'REJECTED (PASS)' if 'Bedrooms cannot be negative.' in html else 'ALLOWED (FAIL)'}")

    # Invalid Bathrooms < 0
    resp = client.post(create_url, {
        'title': 'Test Invalid Property',
        'price': 100000,
        'property_type': Property.PropertyType.APARTMENT,
        'category': cat.id,
        'bedrooms': 2,
        'bathrooms': -2,
        'area_sqft': 1000,
        'address': 'Test address',
        'city': 'Mumbai',
        'locality': 'Bandra',
        'pincode': '400050',
    })
    html = resp.content.decode('utf-8')
    print(f"  Bathrooms = -2: {'REJECTED (PASS)' if 'Bathrooms cannot be negative.' in html else 'ALLOWED (FAIL)'}")

    # Invalid Area <= 0
    resp = client.post(create_url, {
        'title': 'Test Invalid Property',
        'price': 100000,
        'property_type': Property.PropertyType.APARTMENT,
        'category': cat.id,
        'bedrooms': 2,
        'bathrooms': 2,
        'area_sqft': 0,
        'address': 'Test address',
        'city': 'Mumbai',
        'locality': 'Bandra',
        'pincode': '400050',
    })
    html = resp.content.decode('utf-8')
    print(f"  Area = 0: {'REJECTED (PASS)' if 'Area must be at least 100 sqft.' in html else 'ALLOWED (FAIL)'}")

    print("\n--- VALIDATION TESTS COMPLETE ---")

if __name__ == '__main__':
    run_validation_checks()
