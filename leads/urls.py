from django.urls import path

from . import views

app_name = "leads"

urlpatterns = [
    path("", views.lead_list, name="list"),
    path("new/", views.lead_create, name="create"),
    path("<int:pk>/edit/", views.lead_update, name="update"),
]

