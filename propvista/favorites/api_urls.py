from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api_views import FavoriteViewSet

router = DefaultRouter()
router.register("favorites", FavoriteViewSet, basename="api-favorites")

urlpatterns = [path("", include(router.urls))]
