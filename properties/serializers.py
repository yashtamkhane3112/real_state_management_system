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

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0.")
        return value

    def validate_year_built(self, value):
        import datetime
        current_year = datetime.datetime.now().year
        if value < 1900 or value > current_year:
            raise serializers.ValidationError(f"Year Built must be between 1900 and {current_year}.")
        return value

    def validate_bedrooms(self, value):
        if value < 1 or value > 20:
            raise serializers.ValidationError("Bedrooms must be between 1 and 20.")
        return value

    def validate_bathrooms(self, value):
        if value < 1 or value > 20:
            raise serializers.ValidationError("Bathrooms must be between 1 and 20.")
        return value

    def validate_area_sqft(self, value):
        if value < 100:
            raise serializers.ValidationError("Area must be at least 100 sqft.")
        return value

