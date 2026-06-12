from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import SavedSearch, SearchHistory


class SavedSearchSerializer(serializers.ModelSerializer):
    matches_count = serializers.SerializerMethodField()

    class Meta:
        model = SavedSearch
        fields = ("id", "name", "query_params", "notify_on_new", "last_notified_at", "created_at", "updated_at", "matches_count")
        read_only_fields = ("id", "user", "last_notified_at", "created_at", "updated_at", "matches_count")

    @extend_schema_field(serializers.IntegerField())
    def get_matches_count(self, obj):
        return obj.matches_count()


class SearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchHistory
        fields = ("id", "keyword", "query_params", "result_count", "created_at")
        read_only_fields = fields
