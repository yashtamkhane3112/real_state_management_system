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

client = Client()
response = client.get(reverse("home"))

assert response.status_code == 200, f"Expected 200, got {response.status_code}"
html = response.content.decode("utf-8")

# 1. Verify Property Comparison card is removed
assert "Property Comparison" not in html, "Property Comparison card is still present!"
assert "Compare up to 4 properties" not in html, "Property Comparison description is still present!"

# 2. Verify Role access cards are removed
assert "cta-role-buyer" not in html, "Buyer role button is still present!"
assert "cta-role-seller" not in html, "Seller role button is still present!"
assert "cta-role-admin" not in html, "Admin role button is still present!"
assert "Wishlist, visits, inquiries" not in html, "Role button description is still present!"

# 3. Verify Story frames are present
assert "images/story-frames/property_000.jpg" in html, "property_000.jpg missing!"
assert "images/story-frames/property_050.jpg" in html, "property_050.jpg missing!"
assert "images/story-frames/property_099.jpg" in html, "property_099.jpg missing!"
assert "lp-story-wrapper" in html, "lp-story-wrapper missing!"
assert "lp-cinematic__vignette" in html, "lp-cinematic__vignette missing!"

print("ALL VERIFICATIONS COMPLETED SUCCESSFULLY!")
