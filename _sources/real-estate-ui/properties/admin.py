"""
Django admin configuration for properties app.
"""
from django.contrib import admin
from .models import Property, PropertyImage, Favorite


class PropertyImageInline(admin.TabularInline):
    """Inline admin for property images."""
    model = PropertyImage
    extra = 1
    fields = ('image', 'alt_text', 'is_primary')


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    """Admin interface for Property model."""
    inlines = [PropertyImageInline]
    list_display = ('title', 'owner', 'city', 'price', 'bedrooms', 'bathrooms', 'status', 'created_at')
    list_filter = ('property_type', 'status', 'city', 'is_featured', 'created_at')
    search_fields = ('title', 'description', 'city', 'address')
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'owner')
        }),
        ('Property Details', {
            'fields': ('property_type', 'status', 'price', 'bedrooms', 'bathrooms', 'area')
        }),
        ('Location', {
            'fields': ('address', 'city', 'state', 'country', 'pincode', 'latitude', 'longitude')
        }),
        ('Amenities & Features', {
            'fields': ('amenities', 'parking', 'balcony', 'garden', 'gym', 'swimming_pool', 'security')
        }),
        ('Metadata', {
            'fields': ('thumbnail', 'is_featured', 'views'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('views', 'created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    """Admin interface for PropertyImage model."""
    list_display = ('property', 'is_primary', 'uploaded_at')
    list_filter = ('is_primary', 'uploaded_at')
    search_fields = ('property__title', 'alt_text')
    readonly_fields = ('uploaded_at',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Admin interface for Favorite model."""
    list_display = ('user', 'property', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'property__title')
    readonly_fields = ('created_at',)
