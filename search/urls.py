from django.urls import path

from .views import GlobalSearchView
from .web_views import saved_search_create, saved_search_delete, saved_search_list, saved_search_run

app_name = "search"
urlpatterns = [
    path("", saved_search_list, name="saved_list"),
    path("saved/create/", saved_search_create, name="saved_create"),
    path("saved/<int:pk>/run/", saved_search_run, name="saved_run"),
    path("saved/<int:pk>/delete/", saved_search_delete, name="saved_delete"),
    path("query/", GlobalSearchView.as_view({"get": "list"}), name="api-search"),
]

