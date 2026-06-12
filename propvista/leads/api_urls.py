from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api_views import LeadViewSet

router = DefaultRouter()
router.register("leads", LeadViewSet, basename="api-leads")

urlpatterns = [path("", include(router.urls))]
