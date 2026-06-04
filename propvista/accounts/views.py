from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Count, Sum
from django.shortcuts import redirect, render
from django.conf import settings
from django.http import Http404
from rest_framework import mixins, permissions, viewsets

from analytics.models import PropertyViewEvent
from favorites.models import Favorite
from inquiries.models import Inquiry
from leads.models import Lead
from notifications.services import unread_count_for
from properties.models import Property
from visits.models import Visit

from .forms import ProfileForm, RegisterForm
from .models import Profile, User
from .serializers import RegisterSerializer, UserSerializer


def register(request):
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        Profile.objects.get_or_create(user=user)
        login(request, user)
        messages.success(request, "Welcome to PropVista.")
        return redirect("accounts:dashboard")
    return render(request, "accounts/register.html", {"form": form})


class UserLoginView(LoginView):
    template_name = "accounts/login.html"


class UserLogoutView(LogoutView):
    pass


@login_required
def dashboard(request):
    if request.user.role == User.Role.SELLER:
        return redirect("accounts:seller_dashboard")
    if request.user.role == User.Role.AGENT:
        return redirect("accounts:agent_dashboard")
    if request.user.is_admin_role:
        return redirect("accounts:admin_dashboard")
    return redirect("accounts:buyer_dashboard")


@login_required
def profile(request):
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)
    form = ProfileForm(request.POST or None, instance=profile_obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated.")
        return redirect("accounts:profile")
    return render(request, "accounts/profile.html", {"form": form})


@login_required
def buyer_dashboard(request):
    favorites = Favorite.objects.select_related("property").filter(user=request.user)
    inquiries = Inquiry.objects.select_related("property").filter(buyer=request.user)
    visits = Visit.objects.select_related("property").filter(buyer=request.user)
    profile = Profile.objects.filter(user=request.user).first()
    buyer_city = (getattr(profile, "city", "") or "").strip()
    recommendations = (
        Property.objects.public().filter(city__iexact=buyer_city)[:6]
        if buyer_city
        else Property.objects.public()[:6]
    )
    unread = unread_count_for(request.user)
    return render(
        request,
        "dashboards/buyer.html",
        {
            "favorites": favorites,
            "inquiries": inquiries,
            "visits": visits,
            "recommendations": recommendations,
            "unread_notifications": unread,
        },
    )


@login_required
def seller_dashboard(request):
    listings = Property.objects.filter(created_by=request.user)
    inquiries = Inquiry.objects.select_related("property", "buyer").filter(property__created_by=request.user)
    return render(
        request,
        "dashboards/seller.html",
        {
            "listings": listings,
            "inquiries": inquiries,
            "stats": {
                "active": listings.filter(status=Property.Status.ACTIVE).count(),
                "pending": listings.filter(approval_status=Property.ApprovalStatus.PENDING).count(),
                "views": PropertyViewEvent.objects.filter(property__created_by=request.user).count(),
                "inquiries": inquiries.count(),
            },
        },
    )


@login_required
def agent_dashboard(request):
    leads = Lead.objects.filter(owner=request.user)
    return render(request, "dashboards/agent.html", {"leads": leads, "properties": Property.objects.filter(created_by=request.user)[:6]})


@login_required
def admin_dashboard(request):
    if not request.user.is_admin_role:
        messages.error(request, "Admin access required.")
        return redirect("accounts:dashboard")
    return render(
        request,
        "dashboards/admin.html",
        {
            "users": User.objects.all()[:20],
            "pending_properties": Property.objects.filter(approval_status=Property.ApprovalStatus.PENDING),
            "top_cities": Property.objects.values("city").annotate(total=Count("id")).order_by("-total")[:6],
            "property_types": Property.objects.values("property_type").annotate(total=Count("id")),
            "total_value": Property.objects.aggregate(total=Sum("price"))["total"] or 0,
        },
    )


class UserViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.select_related("profile").all()
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        return RegisterSerializer if self.action == "create" else UserSerializer


def demo_login(request, role):
    if not settings.DEBUG:
        raise Http404()
    username = {"buyer": "buyer", "seller": "seller", "agent": "agent", "admin": "admin"}.get(role)
    if not username:
        raise Http404()
    user = get_object_or_404(User, username=username)
    login(request, user)
    return redirect("accounts:dashboard")


def demo_logout(request):
    if not settings.DEBUG:
        raise Http404()
    logout(request)
    return redirect("home")
