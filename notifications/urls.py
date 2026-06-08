from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import NotificationViewSet
from .web_views import mark_all_read, mark_read, notification_list, unread_badge

app_name = "notifications"

urlpatterns = [
    path("", notification_list, name="list"),
    path("<int:pk>/read/", mark_read, name="mark_read"),
    path("read-all/", mark_all_read, name="mark_all_read"),
    path("unread/", unread_badge, name="unread_badge"),
]

