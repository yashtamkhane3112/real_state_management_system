import datetime

from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import get_object_or_404, redirect, render
from django.conf import settings
from django.http import Http404
from django.utils import timezone
from rest_framework import mixins, permissions, viewsets

from analytics.models import PropertyViewEvent
from favorites.models import Favorite
from inquiries.models import Inquiry
from notifications.services import unread_count_for
from properties.models import Property
from propvista.utils import sanitize_uploaded_filenames
from visits.models import Visit

from django.contrib.auth.forms import PasswordChangeForm
from .forms import ProfileForm, RegisterForm, UserForm
from .models import Profile, User
from .serializers import RegisterSerializer, UserSerializer
from accounts.decorators import role_required, dashboard_role_required


def register(request):
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        Profile.objects.get_or_create(user=user)
        login(request, user)
        
        # Trigger Emails
        from propvista.mail import send_welcome_email, send_verification_email
        send_welcome_email(user)
        send_verification_email(request, user)
        
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


# sanitize_uploaded_filenames is imported from propvista.utils (shared utility)


@login_required
def profile(request):
    if request.FILES:
        sanitize_uploaded_filenames(request.FILES)
    old_email = request.user.email
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)
    user_form = UserForm(request.POST or None, request.FILES or None, instance=request.user)
    profile_form = ProfileForm(request.POST or None, instance=profile_obj)
    password_form = PasswordChangeForm(request.user, request.POST or None)
    
    if request.method == "POST":
        if "change_password" in request.POST:
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                
                # Send Password Changed email
                from propvista.mail import send_password_changed_email
                send_password_changed_email(user)
                
                messages.success(request, "Password updated successfully.")
                return redirect("accounts:profile")
            else:
                messages.error(request, "Please correct the errors below for password change.")
        else:
            if user_form.is_valid() and profile_form.is_valid():
                user = user_form.save(commit=False)
                email_changed = user.email != old_email
                if email_changed:
                    user.is_verified = False
                user.save()
                profile_form.save()
                
                # Trigger Notification
                from notifications.services import create_notification
                create_notification(
                    user=request.user,
                    title="Profile Updated",
                    body="Your profile information has been successfully updated.",
                    link="/accounts/profile/",
                    category="profile",
                    level="success",
                )
                
                if email_changed:
                    from propvista.mail import send_verification_email
                    send_verification_email(request, user)
                    messages.success(request, "Profile updated. A verification email has been sent to your new address.")
                else:
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


@dashboard_role_required(User.Role.BUYER, User.Role.ADMIN)
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
    hour = timezone.localtime().hour
    greeting = "morning" if hour < 12 else ("afternoon" if hour < 17 else "evening")
    # Pre-compute counts to avoid 4 separate .count() DB queries at template render time
    favorites_count = favorites.count()
    inquiries_count = inquiries.count()
    visits_count = visits.count()
    recommendations_count = recommendations.count()
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
            "favorites_count": favorites_count,
            "inquiries_count": inquiries_count,
            "visits_count": visits_count,
            "recommendations_count": recommendations_count,
        },
    )


@dashboard_role_required(User.Role.SELLER, User.Role.ADMIN)
def seller_dashboard(request):
    listings = Property.objects.filter(created_by=request.user)
    inquiries = Inquiry.objects.select_related("property", "buyer").filter(property__created_by=request.user)
    
    # Phase 2: Property Performance
    performance = listings.annotate(
        total_views=Count("view_events", distinct=True),
        fav_count=Count("favorites", distinct=True),
        inq_count=Count("inquiries", distinct=True)
    ).order_by("-total_views")[:5]
    for p in performance:
        if p.total_views > 0:
            p.conversion_pct = round((p.inq_count / p.total_views) * 100, 1)
        else:
            p.conversion_pct = 0.0

    # Phase 3: Property View History
    recent_views = PropertyViewEvent.objects.select_related("property", "user").filter(
        property__created_by=request.user
    ).order_by("-created_at")[:10]

    from django.db.models.functions import TruncDate
    today = timezone.now().date()
    last7 = [today - datetime.timedelta(days=i) for i in range(6, -1, -1)]
    view_qs = (
        PropertyViewEvent.objects
        .filter(property__created_by=request.user, created_at__date__gte=last7[0])
        .annotate(day=TruncDate("created_at"))
        .values("day").annotate(cnt=Count("id"))
    )
    views_by_day = {row["day"]: row["cnt"] for row in view_qs}
    chart_labels = [d.strftime("%d %b").lstrip("0") for d in last7]
    chart_values = [views_by_day.get(d, 0) for d in last7]
    recent_favorites = Favorite.objects.filter(property__created_by=request.user).select_related("property", "user").order_by("-created_at")[:5]

    # --- Performance fix: replace 13 individual .filter().count() calls with 3 aggregate queries ---
    listing_agg = listings.aggregate(
        cnt_total=Count("id"),
        cnt_active=Count("id", filter=Q(status=Property.Status.ACTIVE)),
        cnt_pending=Count("id", filter=Q(status=Property.Status.PENDING)),
        cnt_sold=Count("id", filter=Q(status=Property.Status.SOLD)),
        cnt_closed=Count("id", filter=Q(status=Property.Status.CLOSED)),
        cnt_approved=Count("id", filter=Q(status=Property.Status.APPROVED)),
        cnt_rejected=Count("id", filter=Q(approval_status=Property.ApprovalStatus.REJECTED)),
    )
    inq_agg = inquiries.aggregate(
        cnt_total=Count("id"),
        cnt_new=Count("id", filter=Q(status="new")),
        cnt_contacted=Count("id", filter=Q(status="contacted")),
        cnt_qualified=Count("id", filter=Q(status="qualified")),
        cnt_closed=Count("id", filter=Q(status="closed")),
    )
    total_views = PropertyViewEvent.objects.filter(property__created_by=request.user).count()

    return render(
        request,
        "dashboards/seller.html",
        {
            "listings": listings,
            "inquiries": inquiries,
            "performance": performance,
            "recent_views": recent_views,
            "chart_labels": chart_labels,
            "chart_values": chart_values,
            "recent_favorites": recent_favorites,
            "stats": {
                "active": listing_agg["cnt_active"],
                "pending": listing_agg["cnt_pending"],
                "sold": listing_agg["cnt_sold"],
                "closed": listing_agg["cnt_closed"],
                "views": total_views,
                "inquiries": inq_agg["cnt_total"],
                "inq_new": inq_agg["cnt_new"],
                "inq_contacted": inq_agg["cnt_contacted"],
                "inq_qualified": inq_agg["cnt_qualified"],
                "inq_closed": inq_agg["cnt_closed"],
                "prop_total": listing_agg["cnt_total"],
                "prop_active": listing_agg["cnt_active"],
                "prop_pending": listing_agg["cnt_pending"],
                "prop_sold": listing_agg["cnt_sold"],
                "prop_closed": listing_agg["cnt_closed"],
                "prop_approved": listing_agg["cnt_approved"],
                "prop_rejected": listing_agg["cnt_rejected"],
            },
        },
    )



@dashboard_role_required(User.Role.ADMIN)
def admin_dashboard(request):
    from analytics.models import AuditLog
    # Real monthly user registration for last 6 months
    six_months_ago = timezone.now() - datetime.timedelta(days=180)
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


@dashboard_role_required(User.Role.ADMIN)
def admin_users(request):
    role_filter = request.GET.get('role', '')
    qs = User.objects.annotate(
        property_count=Count('properties', distinct=True),
        inquiry_count=Count('inquiries', distinct=True),
    ).order_by('-date_joined')
    if role_filter in ('buyer', 'seller', 'admin'):
        qs = qs.filter(role=role_filter)
    return render(request, 'dashboards/admin_users.html', {
        'users_list': qs,
        'role_filter': role_filter,
        'total_count': qs.count(),
    })


class UserViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.select_related("profile").all()

    def get_permissions(self):
        if self.action == "create":
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_authenticated and not self.request.user.is_admin_role:
            return qs.filter(pk=self.request.user.pk)
        return qs

    def get_serializer_class(self):
        return RegisterSerializer if self.action == "create" else UserSerializer


def demo_login(request, role):
    if not settings.DEBUG:
        raise Http404()
    username = {"buyer": "buyer", "seller": "seller", "admin": "admin"}.get(role)
    if not username:
        raise Http404()
    user = get_object_or_404(User, username=username)
    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    return redirect("accounts:dashboard")


def demo_logout(request):
    if not settings.DEBUG:
        raise Http404()
    logout(request)
    return redirect("home")


def verify_email(request, token):
    from django.core import signing
    try:
        data = signing.loads(token, max_age=86400) # 24 hours
        user_id = data.get("user_id")
        email = data.get("email")
        
        user = get_object_or_404(User, pk=user_id, email=email)
        user.is_verified = True
        user.save()
        messages.success(request, "Your email address has been verified successfully!")
    except signing.SignatureExpired:
        messages.error(request, "The verification link has expired.")
    except signing.BadSignature:
        messages.error(request, "The verification link is invalid.")
    
    return redirect("accounts:profile")
