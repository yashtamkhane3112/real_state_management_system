import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "propvista.settings")
django.setup()

from django.conf import settings
settings.ALLOWED_HOSTS.append("testserver")

from django.test import Client
from django.urls import reverse
from accounts.models import User

client = Client()

print("Anonymous user dashboard requests:")
for path in ["buyer_dashboard", "seller_dashboard", "admin_dashboard"]:
    url = reverse(f"accounts:{path}")
    response = client.get(url)
    print(f"GET {url} -> {response.status_code} (Location: {response.get('Location', 'None')})")

print("\nBuyer user dashboard requests:")
buyer = User.objects.filter(role=User.Role.BUYER).first()
if not buyer:
    buyer = User.objects.create_user(username="test_buyer_tmp", password="Password123", role=User.Role.BUYER)
client.force_login(buyer)
for path in ["buyer_dashboard", "seller_dashboard", "admin_dashboard"]:
    url = reverse(f"accounts:{path}")
    response = client.get(url)
    print(f"GET {url} -> {response.status_code} (Location: {response.get('Location', 'None')})")
client.logout()

print("\nSeller user dashboard requests:")
seller = User.objects.filter(role=User.Role.SELLER).first()
if not seller:
    seller = User.objects.create_user(username="test_seller_tmp", password="Password123", role=User.Role.SELLER)
client.force_login(seller)
for path in ["buyer_dashboard", "seller_dashboard", "admin_dashboard"]:
    url = reverse(f"accounts:{path}")
    response = client.get(url)
    print(f"GET {url} -> {response.status_code} (Location: {response.get('Location', 'None')})")
client.logout()

print("\nAdmin user dashboard requests:")
admin = User.objects.filter(role=User.Role.ADMIN).first()
if not admin:
    admin = User.objects.create_user(username="test_admin_tmp", password="Password123", role=User.Role.ADMIN)
client.force_login(admin)
for path in ["buyer_dashboard", "seller_dashboard", "admin_dashboard"]:
    url = reverse(f"accounts:{path}")
    response = client.get(url)
    print(f"GET {url} -> {response.status_code} (Location: {response.get('Location', 'None')})")
client.logout()

# Clean up temp users if created
User.objects.filter(username__in=["test_buyer_tmp", "test_seller_tmp", "test_admin_tmp"]).delete()
