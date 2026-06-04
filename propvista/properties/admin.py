from django.contrib import admin

from .models import Amenity, Category, Property, PropertyImage

admin.site.register([Category, Amenity, Property, PropertyImage])
