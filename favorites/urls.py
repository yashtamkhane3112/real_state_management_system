from django.urls import path

from . import views

app_name = "favorites"

urlpatterns = [
    path("", views.wishlist, name="wishlist"),
    path("toggle/<slug:slug>/", views.toggle, name="toggle"),
    path("seller/", views.seller_favorites, name="seller_favorites"),
]

