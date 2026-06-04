from django.urls import path

from . import views

app_name = "ai_features"

urlpatterns = [
    path("", views.ai_tools, name="tools"),
    path("generate/<str:feature>/", views.generate, name="generate"),
]

