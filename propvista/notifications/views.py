from django.utils import timezone
from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Notification
from .serializers import NotificationSerializer
from .services import unread_count_for


class NotificationViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Notification.objects.none()
        return Notification.objects.filter(user=self.request.user).order_by("-created_at")

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data = {
            "unread_count": unread_count_for(request.user),
            "results": response.data,
        }
        return response

    @action(detail=True, methods=["post"])
    def read(self, request, pk=None):
        notif = self.get_object()
        notif.mark_read()
        return Response(NotificationSerializer(notif).data)

    @action(detail=False, methods=["post"])
    def read_all(self, request):
        updated = Notification.objects.filter(user=request.user, is_read=False).update(is_read=True, read_at=timezone.now())
        return Response({"updated": updated, "unread_count": 0})

    @action(detail=False, methods=["get"])
    def unread(self, request):
        return Response({"unread_count": unread_count_for(request.user)})
