from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import InquiryViewSet

router = DefaultRouter()
router.register("inquiries", InquiryViewSet, basename="api-inquiries")
urlpatterns = [path("", include(router.urls))]

