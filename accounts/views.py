from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render
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

from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .forms import ProfileForm, RegisterForm, UserForm
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
    if request.user.is_admin_role:
        return redirect("accounts:admin_dashboard")
    return redirect("accounts:buyer_dashboard")


def sanitize_uploaded_filenames(files_dict, max_length=60):
    import os
    import uuid
    for key in files_dict:
        for f in files_dict.getlist(key):
            name, ext = os.path.splitext(f.name)
            name = "".join(c for c in name if c.isalnum() or c in ("-", "_")).replace(" ", "_")
            if not name:
                name = uuid.uuid4().hex[:8]
            allowed_len = max_length - len(ext)
            if allowed_len <= 0:
                name = name[:10]
            else:
                name = name[:allowed_len]
            f.name = f"{name}{ext}"


@login_required
def profile(request):
    if request.FILES:
        sanitize_uploaded_filenames(request.FILES)
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)
    user_form = UserForm(request.POST or None, request.FILES or None, instance=request.user)
    profile_form = ProfileForm(request.POST or None, instance=profile_obj)
    password_form = PasswordChangeForm(request.user, request.POST or None)
    
    if request.method == "POST":
        if "change_password" in request.POST:
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password updated successfully.")
                return redirect("accounts:profile")
            else:
                messages.error(request, "Please correct the errors below for password change.")
        else:
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, "Profile updated successfully.")
                return redirect("accounts:profile")
            else:
                messages.error(request, "Please correct the errors below for profile details.")
                
    return render(
        request,
        "accounts/profile.html",
        {
            "user_form": user_form,
            "profile_form": profile_form,
            "password_form": password_form,
        }
    )


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
    from django.utils import timezone
    hour = timezone.localtime().hour
    greeting = "morning" if hour < 12 else ("afternoon" if hour < 17 else "evening")
    return render(
        request,
        "dashboards/buyer.html",
        {
            "favorites": favorites,
            "inquiries": inquiries,
            "visits": visits,
            "recommendations": recommendations,
            "unread_notifications": unread,
            "greeting": greeting,
        },
    )


@login_required
def seller_dashboard(request):
    listings = Property.objects.filter(created_by=request.user)
    inquiries = Inquiry.objects.select_related("property", "buyer").filter(property__created_by=request.user)
    from django.utils import timezone
    from django.db.models.functions import TruncDate
    from datetime import timedelta
    today = timezone.now().date()
    last7 = [today - timedelta(days=i) for i in range(6, -1, -1)]
    view_qs = (
        PropertyViewEvent.objects
        .filter(property__created_by=request.user, created_at__date__gte=last7[0])
        .annotate(day=TruncDate("created_at"))
        .values("day").annotate(cnt=Count("id"))
    )
    views_by_day = {row["day"]: row["cnt"] for row in view_qs}
    chart_labels = [d.strftime("%d %b").lstrip("0") for d in last7]
    chart_values = [views_by_day.get(d, 0) for d in last7]
    return render(
        request,
        "dashboards/seller.html",
        {
            "listings": listings,
            "inquiries": inquiries,
            "chart_labels": chart_labels,
            "chart_values": chart_values,
            "stats": {
                "active": listings.filter(status=Property.Status.ACTIVE).count(),
                "pending": listings.filter(approval_status=Property.ApprovalStatus.PENDING).count(),
                "views": PropertyViewEvent.objects.filter(property__created_by=request.user).count(),
                "inquiries": inquiries.count(),
                "inq_new": inquiries.filter(status="new").count(),
                "inq_contacted": inquiries.filter(status="contacted").count(),
                "inq_qualified": inquiries.filter(status="qualified").count(),
                "inq_closed": inquiries.filter(status="closed").count(),
                "prop_total": listings.count(),
                "prop_pending": listings.filter(approval_status=Property.ApprovalStatus.PENDING).count(),
                "prop_approved": listings.filter(approval_status=Property.ApprovalStatus.APPROVED).count(),
                "prop_rejected": listings.filter(approval_status=Property.ApprovalStatus.REJECTED).count(),
            },
        },
    )



@login_required
def admin_dashboard(request):
    if not request.user.is_admin_role:
        messages.error(request, "Admin access required.")
        return redirect("accounts:dashboard")
    from analytics.models import AuditLog
    from django.utils import timezone
    from django.db.models.functions import TruncMonth
    from datetime import timedelta
    # Real monthly user registration for last 6 months
    six_months_ago = timezone.now() - timedelta(days=180)
    monthly_users = (
        User.objects.filter(date_joined__gte=six_months_ago)
        .annotate(month=TruncMonth("date_joined"))
        .values("month").annotate(cnt=Count("id"))
        .order_by("month")
    )
    user_growth_labels = [row["month"].strftime("%b") for row in monthly_users]
    user_growth_values = [row["cnt"] for row in monthly_users]
    recent_audit = AuditLog.objects.select_related("actor").order_by("-created_at")[:10]
    return render(
        request,
        "dashboards/admin.html",
        {
            "users": User.objects.all()[:20],
            "total_users_count": User.objects.count(),
            "total_properties_count": Property.objects.count(),
            "pending_properties": Property.objects.filter(approval_status=Property.ApprovalStatus.PENDING),
            "top_cities": Property.objects.values("city").annotate(total=Count("id")).order_by("-total")[:6],
            "property_types": Property.objects.values("property_type").annotate(total=Count("id")),
            "total_value": Property.objects.aggregate(total=Sum("price"))["total"] or 0,
            "recent_audit": recent_audit,
            "user_growth_labels": user_growth_labels,
            "user_growth_values": user_growth_values,
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
    username = {"buyer": "buyer", "seller": "seller", "admin": "admin"}.get(role)
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
