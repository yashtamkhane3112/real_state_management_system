from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AIFeatureViewSet

router = DefaultRouter()
router.register("ai", AIFeatureViewSet, basename="api-ai")
urlpatterns = [path("", include(router.urls))]
