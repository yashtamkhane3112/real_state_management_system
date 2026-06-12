from rest_framework import serializers

from .models import Amenity, Category, Property


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = "__all__"


class PropertySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    amenities_names = serializers.StringRelatedField(source="amenities", many=True, read_only=True)

    class Meta:
        model = Property
        fields = "__all__"
        read_only_fields = ("created_by", "slug", "view_count", "created_at", "updated_at")

