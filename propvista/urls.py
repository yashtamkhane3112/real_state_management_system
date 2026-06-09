from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from properties.views import home

urlpatterns = [
    path("favicon.ico", RedirectView.as_view(url="/static/images/favicon.svg", permanent=True)),
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("accounts/", include("accounts.urls")),
    path("properties/", include("properties.urls")),
    path("inquiries/", include("inquiries.urls")),
    path("favorites/", include("favorites.urls")),
    path("visits/", include("visits.urls")),
    path("leads/", include("leads.urls")),
    path("reports/", include("reports.urls")),
    path("notifications/", include("notifications.urls", namespace="notifications")),
    path("search/", include("search.urls", namespace="search")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/v1/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/v1/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/", include("properties.api_urls")),
    path("api/v1/", include("accounts.api_urls")),
    path("api/v1/", include("inquiries.api_urls")),
    path("api/v1/", include("favorites.api_urls")),
    path("api/v1/", include("visits.api_urls")),
    path("api/v1/", include("leads.api_urls")),
    path("api/v1/", include("notifications.api_urls")),
    path("api/v1/", include("search.api_urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
