from django.conf import settings
from django.db import models


class Inquiry(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "New"
        CONTACTED = "contacted", "Contacted"
        QUALIFIED = "qualified", "Qualified"
        CLOSED = "closed", "Closed"

    property = models.ForeignKey("properties.Property", on_delete=models.CASCADE, related_name="inquiries")
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="inquiries")
    name = models.CharField(max_length=140)
    email = models.EmailField()
    phone = models.CharField(max_length=24, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.property.title}"

