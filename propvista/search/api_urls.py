from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import GlobalSearchView, SavedSearchViewSet, SearchHistoryViewSet

router = DefaultRouter()
router.register("saved-searches", SavedSearchViewSet, basename="api-saved-searches")
router.register("search-history", SearchHistoryViewSet, basename="api-search-history")

urlpatterns = [
    path("", include(router.urls)),
    path("query/", GlobalSearchView.as_view({"get": "list"}), name="api-search"),
]
