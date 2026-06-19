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

# 1. Verify new video asset is loaded
assert "videoplayback.mp4" in html, "New videoplayback.mp4 video file not found in home page!"
assert "pv-hero-canvas" in html, "pv-hero-canvas video class not found in home page!"
assert "autoplay" in html and "loop" in html and "muted" in html and "playsinline" in html, "Video attributes missing!"

# 2. Verify hero copies are intact
assert "INTELLIGENT PROPERTY PLATFORM" in html, "Hero copy 'INTELLIGENT PROPERTY PLATFORM' not found!"
assert "Real Estate Operations" in html, "Hero copy 'Real Estate Operations' not found!"
assert "Unified." in html, "Hero copy 'Unified.' not found!"

# 3. Verify search form is intact
assert "pm-command-search" in html, "Search panel 'pm-command-search' not found!"
assert "Asset type" in html, "Search panel 'Asset type' not found!"
assert "Budget" in html, "Search panel 'Budget' not found!"

# 4. Verify story experience is removed
assert "lp-story-wrapper" not in html, "lp-story-wrapper still present in home page!"
assert "images/story-frames" not in html, "Story frames still present in home page!"

# 5. Verify that comparison and role button sections are still removed
assert "Property Comparison" not in html, "Property Comparison card is still present!"
assert "cta-role-buyer" not in html, "Buyer role button is still present!"

print("V9 HERO VIDEO AND SPACING VALIDATION COMPLETED SUCCESSFULLY!")
