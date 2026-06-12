from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AmenityViewSet, CategoryViewSet, PropertyViewSet

router = DefaultRouter()
router.register("properties", PropertyViewSet, basename="api-properties")
router.register("categories", CategoryViewSet, basename="api-categories")
router.register("amenities", AmenityViewSet, basename="api-amenities")

urlpatterns = [path("", include(router.urls))]

