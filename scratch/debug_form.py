import os
import django
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "propvista.settings")
django.setup()

from properties.forms import PropertyForm
from properties.models import Category, Property

def generate_valid_image(size_bytes):
    file = BytesIO()
    img = Image.new('RGB', (1, 1))
    img.save(file, 'jpeg')
    file.write(b'\x00' * max(0, size_bytes - file.tell()))
    file.seek(0)
    return file.getvalue()

category = Category.objects.first() or Category.objects.create(name="Residential", slug="residential")
form_data = {
    "title": "Bandra Sea View",
    "description": "Premium apartment",
    "price": 10000000,
    "property_type": Property.PropertyType.APARTMENT,
    "category": category.id,
    "bedrooms": -1,
    "bathrooms": -2,
    "area_sqft": 0,
    "price": 0,
    "parking": 1,
    "status": "active",
    "address": "Bandra",
    "city": "Mumbai",
    "locality": "Bandra",
    "pincode": "400050",
}
img_data = generate_valid_image(9 * 1024 * 1024)
valid_cover = SimpleUploadedFile("cover.jpg", img_data, content_type="image/jpeg")
form = PropertyForm(data=form_data, files={"cover_image": valid_cover})
print("Is valid?", form.is_valid())
print("Errors:", form.errors)


