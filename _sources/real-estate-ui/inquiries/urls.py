"""
URL configuration for inquiries app.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Inquiry URLs
    path('<slug:slug>/inquiry/', views.submit_inquiry, name='submit_inquiry'),
    path('my-inquiries/', views.my_inquiries, name='my_inquiries'),
    path('property-inquiries/', views.property_inquiries, name='property_inquiries'),
    path('<int:inquiry_id>/update-status/', views.update_inquiry_status, name='update_inquiry_status'),
    
    # Message URLs
    path('messages/', views.messages_list, name='messages'),
    path('conversation/<int:user_id>/', views.conversation, name='conversation'),
    path('send-message/<int:user_id>/', views.send_message, name='send_message'),
]
