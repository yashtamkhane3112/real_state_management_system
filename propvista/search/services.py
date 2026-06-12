
from django.utils import timezone

from notifications.services import create_notification

from .models import SavedSearch, SearchAlert


def run_saved_search_alerts(property_obj=None):
    """For each saved search, find newly listed properties and notify the user.

    Call this from a management command or signal so saved-search subscribers
    get alerts when matching inventory is published.
    """
    if property_obj is not None:
        properties = [property_obj]
    else:
        from properties.models import Property

        properties = list(Property.objects.public().order_by("-created_at")[:20])

    for saved in SavedSearch.objects.filter(notify_on_new=True).select_related("user"):
        matched = []
        for prop in properties:
            qs = prop.__class__.objects.public().filter(pk=prop.pk).search(saved.query_params)
            if qs.exists():
                if SearchAlert.objects.filter(saved_search=saved, property=prop).exists():
                    continue
                matched.append(prop)
        if not matched:
            continue
        for prop in matched:
            SearchAlert.objects.create(saved_search=saved, property=prop)
            create_notification(
                user=saved.user,
                title=f"New match: {prop.title}",
                body=f"A new property matches your saved search '{saved.name}' in {prop.city}.",
                link=f"/properties/{prop.slug}/",
            )
        saved.last_notified_at = timezone.now()
        saved.save(update_fields=["last_notified_at"])
