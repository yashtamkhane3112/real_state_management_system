from rest_framework import permissions, serializers, viewsets


from .models import Lead, LeadActivity


class LeadActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadActivity
        fields = ("id", "lead", "activity_type", "note", "created_at")
        read_only_fields = ("id", "lead", "created_at")


class LeadSerializer(serializers.ModelSerializer):
    activities = LeadActivitySerializer(many=True, read_only=True)

    class Meta:
        model = Lead
        fields = (
            "id",
            "owner",
            "property",
            "name",
            "phone",
            "email",
            "stage",
            "score",
            "notes",
            "follow_up_at",
            "created_at",
            "activities",
        )
        read_only_fields = ("id", "owner", "created_at")

    def validate_phone(self, value):
        if value:
            import re
            if not re.match(r'^[6-9]\d{9}$', value):
                raise serializers.ValidationError("Phone number must be exactly 10 digits and start with 6, 7, 8, or 9.")
        return value

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["owner"] = request.user
        return super().create(validated_data)


class LeadViewSet(viewsets.ModelViewSet):
    serializer_class = LeadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Lead.objects.none()
        user = self.request.user
        qs = Lead.objects.select_related("owner", "property").prefetch_related("activities")
        if user.is_admin_role:
            return qs
        if user.role == "seller":
            return qs.filter(owner=user)
        return qs.none()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
