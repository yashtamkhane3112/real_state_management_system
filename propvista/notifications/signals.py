from django.db.models.signals import post_save
from django.dispatch import receiver

from .services import create_notification


@receiver(post_save, sender="inquiries.Inquiry")
def notify_on_inquiry(sender, instance, created, **kwargs):
    if not created:
        return
    owner = instance.property.created_by
    if owner and owner != instance.buyer:
        create_notification(
            user=owner,
            title=f"New inquiry on {instance.property.title}",
            body=f"{instance.name} ({instance.email}) is interested in your listing.",
            link=f"/properties/{instance.property.slug}/",
            category="inquiry",
            level="info",
        )
    if instance.buyer and instance.buyer != owner:
        create_notification(
            user=instance.buyer,
            title="Inquiry sent",
            body="The seller has been notified. They will reach out shortly.",
            link=f"/properties/{instance.property.slug}/",
            category="inquiry",
            level="success",
        )


@receiver(post_save, sender="visits.Visit")
def notify_on_visit(sender, instance, created, **kwargs):
    if not created:
        return
    owner = instance.property.created_by
    if owner and owner != instance.buyer:
        create_notification(
            user=owner,
            title=f"Visit requested for {instance.property.title}",
            body=f"{instance.buyer.get_full_name() or instance.buyer.username} requested a visit on {instance.scheduled_at:%b %d, %Y %H:%M}.",
            link=f"/properties/{instance.property.slug}/",
            category="visit",
            level="info",
        )
    if instance.buyer and instance.buyer != owner:
        create_notification(
            user=instance.buyer,
            title="Visit request received",
            body="Your visit request has been sent to the listing owner.",
            link=f"/properties/{instance.property.slug}/",
            category="visit",
            level="success",
        )


@receiver(post_save, sender="favorites.Favorite")
def notify_on_favorite(sender, instance, created, **kwargs):
    if not created:
        return
    owner = instance.property.created_by
    if owner and owner != instance.user:
        create_notification(
            user=owner,
            title=f"{instance.property.title} was saved",
            body=f"{instance.user.username} added your listing to their wishlist.",
            link=f"/properties/{instance.property.slug}/",
            category="favorite",
            level="info",
        )


@receiver(post_save, sender="leads.Lead")
def notify_on_lead(sender, instance, created, **kwargs):
    if not created:
        return
    if instance.owner:
        create_notification(
            user=instance.owner,
            title=f"New lead: {instance.name}",
            body=f"Lead scored {instance.score}. Stage: {instance.get_stage_display()}.",
            link="/leads/",
            category="lead",
            level="info",
        )


@receiver(post_save, sender="properties.Property")
def notify_on_approval(sender, instance, created, **kwargs):
    if created:
        if instance.approval_status == "approved":
            create_notification(
                user=instance.created_by,
                title=f"Listing approved: {instance.title}",
                body="Your property is now visible to buyers.",
                link=f"/properties/{instance.slug}/",
                category="approval",
                level="success",
            )
        return
    if instance.approval_status == "approved":
        create_notification(
            user=instance.created_by,
            title=f"Listing approved: {instance.title}",
            body="Your property is now visible to buyers.",
            link=f"/properties/{instance.slug}/",
            category="approval",
            level="success",
        )
    elif instance.approval_status == "rejected":
        create_notification(
            user=instance.created_by,
            title=f"Listing needs changes: {instance.title}",
            body=instance.rejection_reason or "Please review and resubmit your listing.",
            link=f"/properties/{instance.slug}/edit/",
            category="approval",
            level="warning",
        )
