"""
Django admin configuration for users app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin interface for CustomUser model."""
    fieldsets = UserAdmin.fieldsets + (
        ('Real Estate Fields', {'fields': ('role', 'phone', 'bio', 'address', 'city', 'state', 'pincode', 'is_verified', 'profile_picture')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_verified', 'created_at')
    list_filter = ('role', 'is_verified', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-created_at',)
