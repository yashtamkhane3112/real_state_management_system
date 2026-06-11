from django.conf import settings
from django.db import models


class Notification(models.Model):
    class Level(models.TextChoices):
        INFO = "info", "Info"
        SUCCESS = "success", "Success"
        WARNING = "warning", "Warning"
        DANGER = "danger", "Danger"

    class Category(models.TextChoices):
        SYSTEM = "system", "System"
        INQUIRY = "inquiry", "Inquiry"
        VISIT = "visit", "Visit"
        FAVORITE = "favorite", "Favorite"
        LEAD = "lead", "Lead"
        APPROVAL = "approval", "Approval"
        SEARCH = "search", "Search"
        PROFILE = "profile", "Profile"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=180)
    body = models.TextField(blank=True)
    link = models.CharField(max_length=300, blank=True)
    level = models.CharField(max_length=20, choices=Level.choices, default=Level.INFO, db_index=True)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.SYSTEM, db_index=True)
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "is_read", "-created_at"])]

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    def mark_read(self):
        if self.is_read:
            return
        from django.utils import timezone

        self.is_read = True
        self.read_at = timezone.now()
        self.save(update_fields=["is_read", "read_at"])
