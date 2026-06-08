from django.db.models.signals import post_save
from django.dispatch import receiver

from .services import run_saved_search_alerts


@receiver(post_save, sender="properties.Property")
def trigger_saved_search_alerts(sender, instance, created, **kwargs):
    if not created:
        return
    if instance.approval_status != "approved" or instance.status != "active":
        return
    run_saved_search_alerts(property_obj=instance)
