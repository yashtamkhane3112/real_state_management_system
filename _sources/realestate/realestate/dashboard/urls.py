from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.redirect_dashboard, name='redirect'),
    path('buyer/', views.buyer_dashboard, name='buyer'),
    path('seller/', views.seller_dashboard, name='seller'),
    path('admin/', views.admin_dashboard, name='admin'),
    path('admin/approvals/', views.admin_approvals, name='approvals'),
    path('admin/approvals/<int:pk>/approve/', views.approve_property, name='approve'),
    path('admin/approvals/<int:pk>/reject/', views.reject_property, name='reject'),
    path('admin/users/', views.manage_users, name='users'),
    path('admin/users/<int:pk>/toggle/', views.toggle_user_active, name='toggle_user'),
    path('admin/properties/', views.manage_properties, name='properties'),
]
