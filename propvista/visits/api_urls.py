from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api_views import VisitViewSet

router = DefaultRouter()
router.register("visits", VisitViewSet, basename="api-visits")

urlpatterns = [path("", include(router.urls))]
