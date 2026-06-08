from django.utils import timezone
from rest_framework import permissions, serializers, viewsets
from rest_framework.exceptions import ValidationError

from properties.models import Property

from .models import Visit


class VisitSerializer(serializers.ModelSerializer):
    property_title = serializers.CharField(source="property.title", read_only=True)
    property_slug = serializers.CharField(source="property.slug", read_only=True)

    class Meta:
        model = Visit
        fields = ("id", "property", "property_title", "property_slug", "scheduled_at", "status", "notes", "created_at")
        read_only_fields = ("id", "status", "created_at", "buyer")

    def validate_scheduled_at(self, value):
        if value < timezone.now():
            raise ValidationError("Scheduled time must be in the future.")
        return value


class VisitViewSet(viewsets.ModelViewSet):
    serializer_class = VisitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Visit.objects.none()
        user = self.request.user
        qs = Visit.objects.select_related("property", "buyer")
        if user.is_admin_role:
            return qs
        if user.role in {"seller", "agent"}:
            return qs.filter(property__created_by=user)
        return qs.filter(buyer=user)

    def perform_create(self, serializer):
        prop_id = self.request.data.get("property")
        prop = Property.objects.public().filter(pk=prop_id).first() if prop_id else None
        if not prop:
            prop_slug = self.request.data.get("property_slug")
            if prop_slug:
                prop = Property.objects.public().filter(slug=prop_slug).first()
        if not prop:
            raise ValidationError({"property": "Property is required and must be public."})
        serializer.save(buyer=self.request.user, property=prop)
