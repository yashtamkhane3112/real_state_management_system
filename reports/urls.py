from django.urls import path

from . import views

app_name = "reports"

urlpatterns = [
    path("", views.reports_home, name="home"),
    path("download/", views.download_audit_logs, name="download_audit_logs"),
]

