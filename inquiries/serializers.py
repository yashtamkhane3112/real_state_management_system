from rest_framework import serializers

from .models import Inquiry


class InquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inquiry
        fields = "__all__"
        read_only_fields = ("buyer", "created_at")

    def validate_phone(self, value):
        if value:
            import re
            if not re.match(r'^[6-9]\d{9}$', value):
                raise serializers.ValidationError("Phone number must be exactly 10 digits and start with 6, 7, 8, or 9.")
        return value

