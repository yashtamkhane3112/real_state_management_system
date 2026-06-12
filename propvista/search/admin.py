from django.contrib import admin

from .models import SavedSearch, SearchAlert, SearchHistory


@admin.register(SavedSearch)
class SavedSearchAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "notify_on_new", "last_notified_at", "updated_at")
    list_filter = ("notify_on_new",)
    search_fields = ("name", "user__username")


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ("keyword", "user", "result_count", "created_at")
    list_filter = ("created_at",)
    search_fields = ("keyword", "user__username")


@admin.register(SearchAlert)
class SearchAlertAdmin(admin.ModelAdmin):
    list_display = ("saved_search", "property", "sent_at")
    search_fields = ("saved_search__name", "property__title")
