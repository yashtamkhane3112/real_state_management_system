"""
URL configuration for properties app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.property_list, name='properties'),
    path('<slug:slug>/', views.property_detail, name='property_detail'),
    path('create/', views.create_property, name='create_property'),
    path('<slug:slug>/edit/', views.edit_property, name='edit_property'),
    path('<slug:slug>/delete/', views.delete_property, name='delete_property'),
    path('<slug:slug>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('my-properties/', views.my_properties, name='my_properties'),
    path('favorites/', views.favorites, name='favorites'),
]
