from django.urls import path
from . import views

app_name = 'properties'

urlpatterns = [
    path('', views.landing, name='landing'),
    path('properties/', views.property_list, name='list'),
    path('properties/<int:pk>/', views.property_detail, name='detail'),
    path('properties/<int:pk>/inquire/', views.send_inquiry, name='inquire'),
    path('properties/<int:pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),

    # Seller
    path('seller/properties/add/', views.add_property, name='add'),
    path('seller/properties/<int:pk>/edit/', views.edit_property, name='edit'),
    path('seller/properties/<int:pk>/delete/', views.delete_property, name='delete'),
    path('seller/properties/<int:pk>/sold/', views.mark_sold, name='mark_sold'),
    path('seller/my-properties/', views.my_properties, name='my_properties'),
    path('seller/inquiries/', views.inquiry_management, name='inquiries'),
    path('seller/inquiries/<int:pk>/reply/', views.reply_inquiry, name='reply_inquiry'),

    # Buyer
    path('buyer/favorites/', views.my_favorites, name='favorites'),
    path('buyer/inquiries/', views.my_inquiries, name='my_inquiries'),
]
