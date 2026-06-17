import json

from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from properties.models import Property
from properties.serializers import PropertySerializer

from .models import SavedSearch, SearchHistory
from .serializers import SavedSearchSerializer, SearchHistorySerializer


def _params_to_dict(params):
    data = {}
    for key in params:
        values = params.getlist(key) if hasattr(params, "getlist") else [params.get(key)]
        if len(values) == 1 and values[0] not in (None, ""):
            data[key] = values[0]
        elif values and any(v not in (None, "") for v in values):
            data[key] = values
    return data


class SavedSearchViewSet(viewsets.ModelViewSet):
    serializer_class = SavedSearchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return SavedSearch.objects.none()
        return SavedSearch.objects.filter(user=self.request.user).order_by("-updated_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, query_params=_params_to_dict(self.request.data.get("query_params") or {}))

    def perform_update(self, serializer):
        instance = serializer.save()
        raw = self.request.data.get("query_params")
        if raw is not None:
            if isinstance(raw, str):
                try:
                    raw = json.loads(raw)
                except json.JSONDecodeError:
                    raw = {}
            instance.query_params = raw or {}
            instance.save(update_fields=["query_params", "updated_at"])

    @action(detail=True, methods=["post"])
    def run(self, request, pk=None):
        saved = self.get_object()
        results = Property.objects.public().select_related("category").prefetch_related("amenities").search(saved.query_params)
        page = self.paginate_queryset(results)
        if page is not None:
            return self.get_paginated_response(PropertySerializer(page, many=True, context={"request": request}).data)
        return Response(PropertySerializer(results, many=True, context={"request": request}).data)


class SearchHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SearchHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return SearchHistory.objects.none()
        return SearchHistory.objects.filter(user=self.request.user)[:50]


class GlobalSearchView(viewsets.GenericViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = PropertySerializer
    queryset = Property.objects.none()

    def list(self, request):
        params = _params_to_dict(request.query_params)
        keyword = (params.get("q") or "").strip()
        results = Property.objects.public().select_related("category").prefetch_related("amenities").search(request.query_params)
        count = results.count()
        if request.user.is_authenticated or True:
            if not request.session.session_key:
                request.session.save()
            SearchHistory.objects.create(
                user=request.user if request.user.is_authenticated else None,
                session_key=request.session.session_key or "",
                query_params=params,
                keyword=keyword,
                result_count=count,
            )
        page = self.paginate_queryset(results)
        if page is not None:
            data = PropertySerializer(page, many=True, context={"request": request}).data
            response = self.get_paginated_response(data)
            response.data = {"keyword": keyword, "total": count, **response.data}
            return response
        return Response(
            {
                "keyword": keyword,
                "total": count,
                "results": PropertySerializer(results, many=True, context={"request": request}).data,
            }
        )
