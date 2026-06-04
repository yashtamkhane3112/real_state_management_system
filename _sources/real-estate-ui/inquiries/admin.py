"""
Django admin configuration for inquiries app.
"""
from django.contrib import admin
from .models import Inquiry, Message, Transaction


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    """Admin interface for Inquiry model."""
    list_display = ('buyer', 'property', 'status', 'email', 'created_at')
    list_filter = ('status', 'created_at', 'property__city')
    search_fields = ('buyer__username', 'property__title', 'email', 'subject')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Inquiry Details', {
            'fields': ('property', 'buyer', 'subject', 'message')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    ordering = ('-created_at',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin interface for Message model."""
    list_display = ('sender', 'receiver', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__username', 'receiver__username', 'subject', 'message')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Admin interface for Transaction model."""
    list_display = ('id', 'property', 'buyer', 'seller', 'amount', 'status', 'created_at')
    list_filter = ('transaction_type', 'status', 'created_at')
    search_fields = ('property__title', 'buyer__username', 'seller__username')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Transaction Details', {
            'fields': ('property', 'buyer', 'seller', 'transaction_type', 'amount')
        }),
        ('Status', {
            'fields': ('status', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    ordering = ('-created_at',)
