from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "category", "level", "is_read", "created_at")
    list_filter = ("category", "level", "is_read", "created_at")
    search_fields = ("title", "body", "user__username")
    readonly_fields = ("read_at",)
