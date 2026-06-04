from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard_redirect, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),

    path('properties/', views.property_list, name='property_list'),
    path('properties/<int:pk>/', views.property_detail, name='property_detail'),
    path('properties/<int:pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('properties/<int:pk>/inquiry/', views.create_inquiry, name='create_inquiry'),

    path('buyer/dashboard/', views.buyer_dashboard, name='buyer_dashboard'),
    path('buyer/favorites/', views.favorite_list, name='favorite_list'),
    path('buyer/inquiries/', views.buyer_inquiries, name='buyer_inquiries'),

    path('seller/dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('seller/properties/', views.seller_properties, name='seller_properties'),
    path('seller/properties/add/', views.add_property, name='add_property'),
    path('seller/properties/<int:pk>/edit/', views.edit_property, name='edit_property'),
    path('seller/properties/<int:pk>/delete/', views.delete_property, name='delete_property'),
    path('seller/inquiries/', views.seller_inquiries, name='seller_inquiries'),
    path('seller/inquiries/<int:pk>/responded/', views.mark_inquiry_responded, name='mark_inquiry_responded'),

    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/properties/', views.admin_properties, name='admin_properties'),
    path('admin-panel/properties/<int:pk>/approve/', views.approve_property, name='approve_property'),
    path('admin-panel/properties/<int:pk>/reject/', views.reject_property, name='reject_property'),
    path('admin-panel/buyers/', views.admin_buyers, name='admin_buyers'),
    path('admin-panel/sellers/', views.admin_sellers, name='admin_sellers'),
    path('admin-panel/inquiries/', views.admin_inquiries, name='admin_inquiries'),
    path('admin-panel/transactions/', views.transactions, name='transactions'),
    path('admin-panel/reports/', views.reports, name='reports'),
    path('admin-panel/reports/export/', views.export_report_pdf, name='export_report_pdf'),
]
