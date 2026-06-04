from django.contrib import admin
from .models import Property, PropertyImage, Inquiry, Favorite


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'city', 'price', 'property_type', 'status', 'is_featured', 'created_at')
    list_filter = ('status', 'property_type', 'listing_type', 'is_featured', 'city')
    search_fields = ('title', 'city', 'address', 'seller__username')
    list_editable = ('status', 'is_featured')
    inlines = [PropertyImageInline]


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'property', 'buyer', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('name', 'email', 'property__title')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'property', 'created_at')


admin.site.register(PropertyImage)
