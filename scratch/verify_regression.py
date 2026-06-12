import os
import sys
import sys
import django
from django.test import Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'propvista.settings')
django.setup()

from django.conf import settings
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

from accounts.models import User, Profile
from properties.models import Property, Category, Amenity, PropertyImage
from inquiries.models import Inquiry
from favorites.models import Favorite
from notifications.models import Notification

def run_regression_checks():
    client = Client()
    print("--- STARTING REGRESSION TESTING ---")
    
    # 1. BUYER REGISTRATION AND LOGIN
    print("\n--- Testing Buyer Register & Login ---")
    # Registration
    register_url = reverse('accounts:register')
    reg_data = {
        'username': 'temp_buyer_123',
        'email': 'temp_buyer@example.com',
        'password': 'Pass@12345',
        'confirm_password': 'Pass@12345',
        'role': User.Role.BUYER
    }
    # Clean up if already exists
    User.objects.filter(username=reg_data['username']).delete()
    
    response = client.post(register_url, reg_data)
    if response.status_code in (302, 200):
        print("Buyer Registration: PASS")
    else:
        print(f"Buyer Registration: FAIL (Status {response.status_code})")
        
    # Login as seeded buyer
    login_url = reverse('accounts:login')
    login_response = client.post(login_url, {'username': 'buyer', 'password': 'Pass@12345'})
    if login_response.status_code in (302, 200):
        print("Buyer Login: PASS")
    else:
        print("Buyer Login: FAIL")
        
    # 2. BUYER SEARCH PROPERTY
    print("\n--- Testing Search Filters ---")
    list_url = reverse('properties:list')
    search_params = {
        'q': 'Seaside',
        'city': 'Mumbai',
        'locality': 'Bandra',
        'property_type': 'apartment',
        'min_price': '1000000',
        'max_price': '50000000',
        'bedrooms': '2',
        'bathrooms': '2'
    }
    search_resp = client.get(list_url, search_params)
    if search_resp.status_code == 200:
        print("Property Search: PASS")
    else:
        print(f"Property Search: FAIL (Status {search_resp.status_code})")
        
    # 3. BUYER VIEW PROPERTY & DETAIL COMPONENTS
    print("\n--- Testing View Property & Components ---")
    # Find any approved public property
    test_prop = Property.objects.filter(approval_status=Property.ApprovalStatus.APPROVED, status=Property.Status.ACTIVE).first()
    if not test_prop:
        # Create one if none exists
        cat, _ = Category.objects.get_or_create(name="Residential", slug="residential")
        seller_user = User.objects.filter(role=User.Role.SELLER).first()
        test_prop = Property.objects.create(
            title="Temp Seaside Apartment",
            slug="temp-seaside-apartment",
            price=15000000,
            property_type=Property.PropertyType.APARTMENT,
            category=cat,
            bedrooms=2,
            bathrooms=2,
            area_sqft=1200,
            city="Mumbai",
            locality="Bandra",
            approval_status=Property.ApprovalStatus.APPROVED,
            status=Property.Status.ACTIVE,
            created_by=seller_user
        )
    
    # Programmatically add cover image and gallery images if not present
    from django.core.files.base import ContentFile
    small_gif = (
        b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00'
        b'\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00'
        b'\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b'
    )
    if not test_prop.cover_image:
        test_prop.cover_image.save('cover.gif', ContentFile(small_gif))
    if test_prop.images.count() == 0:
        PropertyImage.objects.create(property=test_prop, image=SimpleUploadedFile('gal1.gif', small_gif, content_type='image/gif'))
        PropertyImage.objects.create(property=test_prop, image=SimpleUploadedFile('gal2.gif', small_gif, content_type='image/gif'))
    
    detail_url = reverse('properties:detail', args=[test_prop.slug])
    detail_resp = client.get(detail_url)
    if detail_resp.status_code == 200:
        html = detail_resp.content.decode('utf-8')
        # Check components
        has_cover = 'cover_image' in html or 'carousel-item' in html
        has_gallery = 'propertyGalleryCarousel' in html
        has_timeline = 'Listing Lifecycle' in html
        has_share = 'shareProperty()' in html
        has_calculator = 'Finance Calculator' in html
        
        print(f"Property Detail Page: PASS")
        print(f"  - Cover Image: {'PASS' if has_cover else 'FAIL'}")
        print(f"  - Gallery Carousel: {'PASS' if has_gallery else 'FAIL'}")
        print(f"  - Lifecycle Timeline: {'PASS' if has_timeline else 'FAIL'}")
        print(f"  - Share Button: {'PASS' if has_share else 'FAIL'}")
        print(f"  - Finance Calculator: {'PASS' if has_calculator else 'FAIL'}")
    else:
        print(f"Property Detail Page: FAIL (Status {detail_resp.status_code})")
        
    # 4. BUYER FAVORITE & REMOVE FAVORITE
    print("\n--- Testing Favorites ---")
    fav_url = reverse('favorites:toggle', args=[test_prop.slug])
    
    # Check current favorite status
    buyer_user = User.objects.get(username='buyer')
    Favorite.objects.filter(user=buyer_user, property=test_prop).delete()
    print(f"  Current Favorite count after reset: {Favorite.objects.filter(user=buyer_user, property=test_prop).count()}")
    
    fav_resp = client.get(fav_url)
    if fav_resp.status_code == 302:
        is_fav = Favorite.objects.filter(user=buyer_user, property=test_prop).exists()
        print(f"Add Favorite: {'PASS' if is_fav else 'FAIL'}")
    else:
        print(f"Add Favorite: FAIL (Status {fav_resp.status_code})")
        
    # Remove favorite
    unfav_resp = client.get(fav_url)
    if unfav_resp.status_code == 302:
        is_fav = Favorite.objects.filter(user=buyer_user, property=test_prop).exists()
        print(f"Remove Favorite: {'PASS' if not is_fav else 'FAIL'}")
    else:
        print(f"Remove Favorite: FAIL (Status {unfav_resp.status_code})")
        
    # 5. BUYER INQUIRY SUBMISSION
    print("\n--- Testing Inquiry Submission ---")
    inq_url = reverse('inquiries:create', args=[test_prop.slug])
    inq_data = {
        'name': 'Buyer User',
        'email': 'buyer@example.com',
        'phone': '9876543210',
        'message': 'Interested in viewing this property.'
    }
    inq_resp = client.post(inq_url, inq_data)
    if inq_resp.status_code == 302:
        # Check database
        inq_exists = Inquiry.objects.filter(property=test_prop, email=inq_data['email']).exists()
        print(f"Submit Inquiry: {'PASS' if inq_exists else 'FAIL'}")
    else:
        print(f"Submit Inquiry: FAIL (Status {inq_resp.status_code})")
        
    # 6. BUYER NOTIFICATIONS
    print("\n--- Testing Buyer Notifications ---")
    noti_url = reverse('notifications:list')
    noti_resp = client.get(noti_url)
    if noti_resp.status_code == 200:
        print("Buyer View Notifications: PASS")
    else:
        print(f"Buyer View Notifications: FAIL (Status {noti_resp.status_code})")
        
    # Logout buyer
    client.logout()
    
    # 7. SELLER LOGIN
    print("\n--- Testing Seller Login & Dashboard ---")
    seller_login_resp = client.post(login_url, {'username': 'seller', 'password': 'Pass@12345'})
    if seller_login_resp.status_code in (302, 200):
        print("Seller Login: PASS")
    else:
        print("Seller Login: FAIL")
        
    seller_dash_url = reverse('accounts:seller_dashboard')
    seller_dash_resp = client.get(seller_dash_url)
    if seller_dash_resp.status_code == 200:
        html = seller_dash_resp.content.decode('utf-8')
        has_perf = 'Property Performance' in html
        has_views = 'Recent Viewers' in html or 'Views — last 7 days' in html
        has_my_props = 'My Properties' in html
        has_pipeline = 'Inquiry Pipeline' in html
        
        print("Seller Dashboard Page: PASS")
        print(f"  - Property Performance Section: {'PASS' if has_perf else 'FAIL'}")
        print(f"  - Recent Viewers Section: {'PASS' if has_views else 'FAIL'}")
        print(f"  - My Properties Section: {'PASS' if has_my_props else 'FAIL'}")
        print(f"  - Inquiry Pipeline Section: {'PASS' if has_pipeline else 'FAIL'}")
    else:
        print(f"Seller Dashboard Page: FAIL (Status {seller_dash_resp.status_code})")
        
    # 8. SELLER PROPERTY CREATION & IMAGES
    print("\n--- Testing Seller Property Create ---")
    create_url = reverse('properties:create')
    # Let's create dummy category if not exists
    cat, _ = Category.objects.get_or_create(name="Residential", slug="residential")
    create_data = {
        'title': 'New Luxury Villa',
        'description': 'Beautiful villa near beach',
        'price': 45000000,
        'property_type': Property.PropertyType.VILLA,
        'category': cat.id,
        'bedrooms': 4,
        'bathrooms': 4,
        'area_sqft': 4000,
        'furnishing': 'fully_furnished',
        'year_built': 2022,
        'parking': 2,
        'latitude': '19.0760',
        'longitude': '72.8777',
        'address': 'Marine Drive',
        'city': 'Mumbai',
        'locality': 'Marine Drive',
        'pincode': '400020',
        'status': Property.Status.PENDING
    }
    
    # We will upload a cover image and 4 gallery images (5 images total)
    create_data['cover_image'] = SimpleUploadedFile('cover.gif', small_gif, content_type='image/gif')
    create_data['gallery_images'] = [
        SimpleUploadedFile('gal1.gif', small_gif, content_type='image/gif'),
        SimpleUploadedFile('gal2.gif', small_gif, content_type='image/gif'),
        SimpleUploadedFile('gal3.gif', small_gif, content_type='image/gif'),
        SimpleUploadedFile('gal4.gif', small_gif, content_type='image/gif'),
    ]
    
    create_resp = client.post(create_url, create_data)
    if create_resp.status_code == 302:
        new_prop = Property.objects.filter(title='New Luxury Villa').first()
        if new_prop:
            img_count = PropertyImage.objects.filter(property=new_prop).count() + (1 if new_prop.cover_image else 0)
            print(f"Seller Create Property: PASS")
            print(f"  - Total Uploaded Images: {img_count} (Expected: 5) -> {'PASS' if img_count == 5 else 'FAIL'}")
        else:
            print("Seller Create Property: FAIL (Property not in database)")
    else:
        print(f"Seller Create Property: FAIL (Status {create_resp.status_code})")
        if hasattr(create_resp, 'context') and create_resp.context and 'form' in create_resp.context:
            print("Form errors:", create_resp.context['form'].errors)
        
    # 9. SELLER PROPERTY EDIT
    print("\n--- Testing Seller Property Edit ---")
    edit_prop = Property.objects.filter(created_by__username='seller').first()
    if edit_prop:
        edit_url = reverse('properties:update', args=[edit_prop.slug])
        edit_data = {
            'title': edit_prop.title + " (Updated)",
            'description': edit_prop.description,
            'price': edit_prop.price + 100000,
            'property_type': edit_prop.property_type,
            'category': edit_prop.category.id,
            'bedrooms': edit_prop.bedrooms,
            'bathrooms': edit_prop.bathrooms,
            'area_sqft': edit_prop.area_sqft,
            'furnishing': edit_prop.furnishing,
            'year_built': edit_prop.year_built,
            'parking': edit_prop.parking,
            'address': edit_prop.address,
            'city': edit_prop.city,
            'locality': edit_prop.locality,
            'pincode': edit_prop.pincode,
            'status': Property.Status.PENDING
        }
        edit_resp = client.post(edit_url, edit_data)
        if edit_resp.status_code == 302:
            edit_prop.refresh_from_db()
            print(f"Seller Edit Property: PASS (New Title: {edit_prop.title})")
        else:
            print(f"Seller Edit Property: FAIL (Status {edit_resp.status_code})")
    else:
        print("Seller Edit Property: FAIL (No property found to edit)")
        
    # 10. SELLER INQUIRY PIPELINE
    print("\n--- Testing Seller Inquiry Pipeline ---")
    pipeline_url = reverse('leads:list')
    pipeline_resp = client.get(pipeline_url)
    if pipeline_resp.status_code == 200:
        print("Seller Inquiry Pipeline: PASS")
    else:
        print(f"Seller Inquiry Pipeline: FAIL (Status {pipeline_resp.status_code})")
        
    # 11. SELLER PROFILE & AVATAR CONSISTENCY
    print("\n--- Testing Profile & Avatar ---")
    profile_url = reverse('accounts:profile')
    profile_resp = client.get(profile_url)
    if profile_resp.status_code == 200:
        html = profile_resp.content.decode('utf-8')
        # Check navbar, sidebar, profile page avatar
        has_navbar_avatar = 'pv-avatar' in html or 'avatar' in html
        print(f"Seller Profile Page: PASS")
        print(f"  - Avatar in HTML: {'PASS' if has_navbar_avatar else 'FAIL'}")
    else:
        print(f"Seller Profile Page: FAIL (Status {profile_resp.status_code})")
        
    client.logout()
    
    # 12. ADMIN LOGIN & DASHBOARD & APPROVALS
    print("\n--- Testing Admin Login & Dashboard & Moderation ---")
    admin_login_resp = client.post(login_url, {'username': 'admin', 'password': 'Pass@12345'})
    if admin_login_resp.status_code in (302, 200):
        print("Admin Login: PASS")
    else:
        print("Admin Login: FAIL")
        
    admin_dash_url = reverse('accounts:admin_dashboard')
    admin_dash_resp = client.get(admin_dash_url)
    if admin_dash_resp.status_code == 200:
        print("Admin Dashboard: PASS")
        admin_html = admin_dash_resp.content.decode('utf-8')
        # Let's check for the GET approval button bug we noticed!
        # Search for: href="/properties/.../approve/"
        import re
        approve_hrefs = re.findall(r'href=["\']/properties/[^/]+/approve/["\']', admin_html)
        if approve_hrefs:
            print("  - Approval Queue Action Check: BUG DETECTED! Admin Dashboard lists GET-based approval links.")
        else:
            # Check if there is a POST form
            if 'method="post"' in admin_html or 'method="POST"' in admin_html:
                print("  - Approval Queue Action Check: PASS (uses POST form)")
            else:
                print("  - Approval Queue Action Check: FAIL (no POST form found)")
    else:
        print(f"Admin Dashboard: FAIL (Status {admin_dash_resp.status_code})")
        
    # Test Approve Property (POST only)
    pending_prop = Property.objects.filter(approval_status=Property.ApprovalStatus.PENDING).first()
    if not pending_prop:
        # Let's create a pending property
        cat, _ = Category.objects.get_or_create(name="Residential", slug="residential")
        seller_user = User.objects.filter(role=User.Role.SELLER).first()
        pending_prop = Property.objects.create(
            title="Pending Property 123",
            slug="pending-property-123",
            price=20000000,
            property_type=Property.PropertyType.APARTMENT,
            category=cat,
            bedrooms=3,
            bathrooms=3,
            area_sqft=1500,
            city="Mumbai",
            locality="Bandra",
            approval_status=Property.ApprovalStatus.PENDING,
            created_by=seller_user
        )
        
    approve_url = reverse('properties:approve', args=[pending_prop.slug])
    # Attempt GET (should fail/redirect/be blocked by require_POST)
    approve_get = client.get(approve_url)
    print(f"  - GET Approve Security Block: {'PASS' if approve_get.status_code == 405 else 'FAIL'} (Status {approve_get.status_code})")
    
    # Attempt POST (should succeed)
    approve_post = client.post(approve_url)
    if approve_post.status_code == 302:
        pending_prop.refresh_from_db()
        print(f"  - POST Approve Action: {'PASS' if pending_prop.approval_status == Property.ApprovalStatus.APPROVED else 'FAIL'}")
    else:
        print(f"  - POST Approve Action: FAIL (Status {approve_post.status_code})")
        
    # Test Reject Property (POST only)
    # Turn it to pending again
    pending_prop.approval_status = Property.ApprovalStatus.PENDING
    pending_prop.save()
    
    reject_url = reverse('properties:reject', args=[pending_prop.slug])
    # Attempt GET (should fail/redirect/be blocked by require_POST)
    reject_get = client.get(reject_url)
    print(f"  - GET Reject Security Block: {'PASS' if reject_get.status_code == 405 else 'FAIL'} (Status {reject_get.status_code})")
    
    # Attempt POST (should succeed)
    reject_post = client.post(reject_url, {'reason': 'Incorrect pricing details.'})
    if reject_post.status_code == 302:
        pending_prop.refresh_from_db()
        is_rejected = pending_prop.approval_status == Property.ApprovalStatus.REJECTED
        reason_correct = pending_prop.rejection_reason == 'Incorrect pricing details.'
        print(f"  - POST Reject Action: {'PASS' if (is_rejected and reason_correct) else 'FAIL'}")
    else:
        print(f"  - POST Reject Action: FAIL (Status {reject_post.status_code})")
        
    # Reports Page
    reports_url = reverse('reports:home')
    reports_resp = client.get(reports_url)
    if reports_resp.status_code == 200:
        print("Admin Reports: PASS")
    else:
        print(f"Admin Reports: FAIL (Status {reports_resp.status_code})")
        
    client.logout()
    print("\n--- REGRESSION TESTING COMPLETE ---")

if __name__ == '__main__':
    run_regression_checks()
