from django.urls import path

from . import views

app_name = "inquiries"

urlpatterns = [path("properties/<slug:slug>/", views.create_inquiry, name="create")]

