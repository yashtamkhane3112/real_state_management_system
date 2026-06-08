
from django.conf import settings
from django.db import models
from django.utils import timezone


class SavedSearch(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saved_searches")
    name = models.CharField(max_length=120)
    query_params = models.JSONField(default=dict, blank=True)
    notify_on_new = models.BooleanField(default=True)
    last_notified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "Saved search"
        verbose_name_plural = "Saved searches"
        constraints = [
            models.UniqueConstraint(fields=["user", "name"], name="unique_saved_search_per_user"),
        ]

    def matches_count(self):
        from properties.models import Property

        return Property.objects.public().search(self.query_params).count()

    def __str__(self):
        return f"{self.user.username} - {self.name}"


class SearchHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="search_history", null=True, blank=True)
    session_key = models.CharField(max_length=64, blank=True, db_index=True)
    query_params = models.JSONField(default=dict, blank=True)
    keyword = models.CharField(max_length=200, blank=True, db_index=True)
    result_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "-created_at"])]

    def as_query_string(self):
        params = []
        for key, value in (self.query_params or {}).items():
            if isinstance(value, list):
                for item in value:
                    params.append(f"{key}={item}")
            else:
                params.append(f"{key}={value}")
        return "&".join(params)

    def __str__(self):
        return f"Search {self.keyword or self.query_params} ({self.result_count})"


class SearchAlert(models.Model):
    saved_search = models.ForeignKey(SavedSearch, on_delete=models.CASCADE, related_name="alerts")
    property = models.ForeignKey("properties.Property", on_delete=models.CASCADE, related_name="search_alerts")
    sent_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ["-sent_at"]
        unique_together = ("saved_search", "property")

    def __str__(self):
        return f"Alert: {self.saved_search.name} -> {self.property.title}"
