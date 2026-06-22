from django.conf import settings


def site_settings(request):
    user = getattr(request, "user", None)
    unread = 0
    saved_ids = []
    latest = []
    if user and getattr(user, "is_authenticated", False):
        from notifications.services import unread_count_for
        from notifications.models import Notification

        unread = unread_count_for(user)
        saved_ids = list(user.favorites.values_list("property_id", flat=True))
        latest = Notification.objects.filter(user=user).select_related("user").order_by("-created_at")[:5]
    return {
        "GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY,
        "GEMINI_API_KEY": bool(settings.GEMINI_API_KEY),
        "unread_notifications": unread,
        "saved_property_ids": saved_ids,
        "latest_notifications": latest,
        "LANDING_MEDIA_MODE": settings.LANDING_MEDIA_MODE,
    }


