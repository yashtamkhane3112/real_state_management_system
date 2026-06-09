from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", views.UserLogoutView.as_view(), name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.profile, name="profile"),
    path("dashboard/buyer/", views.buyer_dashboard, name="buyer_dashboard"),
    path("dashboard/seller/", views.seller_dashboard, name="seller_dashboard"),
    path("dashboard/admin/", views.admin_dashboard, name="admin_dashboard"),
    path("demo/<str:role>/", views.demo_login, name="demo_login"),
    path("demo-logout/", views.demo_logout, name="demo_logout"),
]
