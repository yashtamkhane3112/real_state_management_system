from rest_framework import serializers

from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "first_name", "last_name", "phone", "role")

    def validate_role(self, value):
        if value not in [User.Role.BUYER, User.Role.SELLER]:
            raise serializers.ValidationError("Public registration only allows Buyer or Seller roles.")
        return value

    def validate_phone(self, value):
        if value:
            import re
            if not re.match(r'^[6-9]\d{9}$', value):
                raise serializers.ValidationError("Phone number must be exactly 10 digits and start with 6, 7, 8, or 9.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create_user(password=password, **validated_data)
        from .models import Profile

        Profile.objects.get_or_create(user=user)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "phone", "role", "is_verified")

    def validate_phone(self, value):
        if value:
            import re
            if not re.match(r'^[6-9]\d{9}$', value):
                raise serializers.ValidationError("Phone number must be exactly 10 digits and start with 6, 7, 8, or 9.")
        return value

