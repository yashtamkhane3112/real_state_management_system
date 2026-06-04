
from .models import Notification


def create_notification(*, user, title, body="", link="", level=Notification.Level.INFO, category=Notification.Category.SYSTEM):
    if user is None:
        return None
    return Notification.objects.create(user=user, title=title, body=body, link=link, level=level, category=category)


def bulk_notify(*, users, title, body="", link="", level=Notification.Level.INFO, category=Notification.Category.SYSTEM):
    notifications = [
        Notification(user=u, title=title, body=body, link=link, level=level, category=category)
        for u in users
        if u is not None
    ]
    if not notifications:
        return []
    Notification.objects.bulk_create(notifications)
    return notifications


def unread_count_for(user):
    if not user or not getattr(user, "is_authenticated", False):
        return 0
    return Notification.objects.filter(user=user, is_read=False).count()
