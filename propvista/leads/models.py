from django.conf import settings
from django.db import models


class Lead(models.Model):
    class Stage(models.TextChoices):
        NEW = "new", "New"
        CONTACTED = "contacted", "Contacted"
        VISIT = "visit", "Visit"
        NEGOTIATION = "negotiation", "Negotiation"
        WON = "won", "Won"
        LOST = "lost", "Lost"

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="leads")
    property = models.ForeignKey("properties.Property", on_delete=models.SET_NULL, null=True, blank=True, related_name="leads")
    name = models.CharField(max_length=160)
    phone = models.CharField(max_length=24, blank=True)
    email = models.EmailField(blank=True)
    stage = models.CharField(max_length=30, choices=Stage.choices, default=Stage.NEW, db_index=True)
    score = models.PositiveSmallIntegerField(default=50, db_index=True)
    notes = models.TextField(blank=True)
    follow_up_at = models.DateTimeField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)


class LeadActivity(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="activities")
    note = models.TextField()
    activity_type = models.CharField(max_length=80, default="note", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

