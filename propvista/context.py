from django.conf import settings


def site_settings(request):
    user = getattr(request, "user", None)
    unread = 0
    if user and getattr(user, "is_authenticated", False):
        from notifications.services import unread_count_for

        unread = unread_count_for(user)
    return {
        "GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY,
        "GEMINI_API_KEY": bool(settings.GEMINI_API_KEY),
        "unread_notifications": unread,
    }

