from django.urls import path

from . import views

app_name = "inquiries"

urlpatterns = [
    path("", views.inquiry_list, name="list"),
    path("<int:pk>/update-status/", views.update_inquiry_status, name="update_status"),
    path("properties/<slug:slug>/", views.create_inquiry, name="create"),
]

