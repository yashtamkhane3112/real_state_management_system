from django.urls import path

from . import views

app_name = "visits"

urlpatterns = [path("book/<slug:slug>/", views.book_visit, name="book")]

