from django.db.models.signals import post_save
from django.dispatch import receiver

from .services import create_notification
from analytics.models import AuditLog


@receiver(post_save, sender="inquiries.Inquiry")
def notify_on_inquiry(sender, instance, created, **kwargs):
    if not created:
        return
    
    # Create Audit Log
    AuditLog.objects.create(
        actor=instance.buyer if instance.buyer else None,
        action=f"Inquiry received for {instance.property.title if instance.property else 'property'}",
        object_type="inquiry",
        object_id=str(instance.id)
    )

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
        
        # Trigger email to seller
        from propvista.mail import send_inquiry_received_email
        send_inquiry_received_email(instance)
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

    # Create Audit Log
    AuditLog.objects.create(
        actor=instance.buyer if instance.buyer else None,
        action=f"Visit scheduled for {instance.property.title if instance.property else 'property'}",
        object_type="visit",
        object_id=str(instance.id)
    )

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

    # Create Audit Log
    AuditLog.objects.create(
        actor=instance.user,
        action=f"Favorite added: {instance.property.title if instance.property else 'property'}",
        object_type="favorite",
        object_id=str(instance.id)
    )

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
        
        # Trigger email to seller
        from propvista.mail import send_property_favorited_email
        send_property_favorited_email(instance)


@receiver(post_save, sender="leads.Lead")
def notify_on_lead(sender, instance, created, **kwargs):
    if not created:
        return

    # Create Audit Log
    AuditLog.objects.create(
        actor=instance.owner if instance.owner else None,
        action=f"Lead created: {instance.name}",
        object_type="lead",
        object_id=str(instance.id)
    )

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
        # Create Audit Log
        AuditLog.objects.create(
            actor=instance.created_by,
            action=f"Property created: {instance.title}",
            object_type="property",
            object_id=str(instance.id)
        )

        if instance.approval_status == "approved":
            create_notification(
                user=instance.created_by,
                title=f"Listing approved: {instance.title}",
                body="Your property is now visible to buyers.",
                link=f"/properties/{instance.slug}/",
                category="approval",
                level="success",
            )
            # Trigger approval email
            from propvista.mail import send_property_approved_email
            send_property_approved_email(instance)
        return

    # Not created (modified or approved/rejected)
    if instance.approval_status == "approved":
        AuditLog.objects.create(
            actor=None,
            action=f"Property approved by Admin: {instance.title}",
            object_type="property",
            object_id=str(instance.id)
        )
        create_notification(
            user=instance.created_by,
            title=f"Listing approved: {instance.title}",
            body="Your property is now visible to buyers.",
            link=f"/properties/{instance.slug}/",
            category="approval",
            level="success",
        )
        # Trigger approval email
        from propvista.mail import send_property_approved_email
        send_property_approved_email(instance)
    elif instance.approval_status == "rejected":
        AuditLog.objects.create(
            actor=None,
            action=f"Property rejected by Admin: {instance.title}",
            object_type="property",
            object_id=str(instance.id)
        )
        create_notification(
            user=instance.created_by,
            title=f"Listing needs changes: {instance.title}",
            body=instance.rejection_reason or "Please review and resubmit your listing.",
            link=f"/properties/{instance.slug}/edit/",
            category="approval",
            level="warning",
        )
        # Trigger rejection email
        from propvista.mail import send_property_rejected_email
        send_property_rejected_email(instance)
