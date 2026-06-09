from django.urls import path

from . import views

app_name = "properties"

urlpatterns = [
    path("", views.property_list, name="list"),
    path("new/", views.property_create, name="create"),
    path("approvals/", views.approvals_list, name="approvals_list"),
    path("city/<str:city>/", views.city_page, name="city"),
    path("<slug:slug>/", views.property_detail, name="detail"),
    path("<slug:slug>/edit/", views.property_update, name="update"),
    path("<slug:slug>/delete/", views.property_delete, name="delete"),
    path("<slug:slug>/approve/", views.approve_property, name="approve"),
    path("<slug:slug>/reject/", views.reject_property, name="reject"),
]

