from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, F
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from rest_framework import permissions, viewsets

from accounts.decorators import role_required
from accounts.models import User
from analytics.models import PropertyViewEvent

from .forms import PropertyForm, PropertyImageForm
from .models import Amenity, Category, Property, PropertyImage
from .serializers import AmenitySerializer, CategorySerializer, PropertySerializer


def home(request):
    from django.db.models import Sum
    from leads.models import Lead
    from visits.models import Visit
    from inquiries.models import Inquiry
    from accounts.models import User

    featured = Property.objects.public().select_related("category", "created_by").prefetch_related("amenities")[:8]
    cities = Property.objects.public().values("city").annotate(total=Count("id")).order_by("-total")[:6]

    # Metrics
    properties_count = Property.objects.count()
    leads_count = Lead.objects.count()
    visits_count = Visit.objects.count()
    pending_count = Property.objects.filter(approval_status=Property.ApprovalStatus.PENDING).count()
    revenue_sum = Property.objects.filter(status=Property.Status.ACTIVE, approval_status=Property.ApprovalStatus.APPROVED).aggregate(total=Sum('price'))['total'] or 0
    
    if revenue_sum >= 10000000:
        revenue_display = f"₹{revenue_sum / 10000000:.1f} Cr"
    elif revenue_sum >= 100000:
        revenue_display = f"₹{revenue_sum / 100000:.1f} L"
    else:
        revenue_display = f"₹{revenue_sum:,}"

    # Activities Timeline
    activities = []
    
    # 1. Properties
    for p in Property.objects.select_related("created_by").order_by("-created_at")[:5]:
        role_label = p.created_by.get_role_display() if (p.created_by and hasattr(p.created_by, 'get_role_display')) else 'Seller'
        activities.append({
            "text": f"{role_label} submitted {p.title}",
            "time": p.created_at,
            "icon": "bi-house-add text-primary"
        })
        
    # 2. Inquiries
    for inq in Inquiry.objects.select_related("property").order_by("-created_at")[:5]:
        activities.append({
            "text": f"Inquiry received for {inq.property.title if inq.property else 'Property'}",
            "time": inq.created_at,
            "icon": "bi-chat-left-text text-warning"
        })
        
    # 3. Visits
    for v in Visit.objects.select_related("property").order_by("-created_at")[:5]:
        activities.append({
            "text": f"Site visit scheduled for {v.property.title if v.property else 'Property'}",
            "time": v.created_at,
            "icon": "bi-calendar2-check text-info"
        })
        
    # 4. Approvals
    for p in Property.objects.filter(approval_status=Property.ApprovalStatus.APPROVED).order_by("-updated_at")[:5]:
        activities.append({
            "text": f"Property approved by Admin: {p.title}",
            "time": p.updated_at,
            "icon": "bi-patch-check-fill text-success"
        })
        
    # 5. User registrations
    for u in User.objects.order_by("-created_at")[:5]:
        role_name = u.get_role_display() if hasattr(u, 'get_role_display') else u.role
        activities.append({
            "text": f"New {role_name} registered: {u.username}",
            "time": u.created_at,
            "icon": "bi-person-plus text-secondary"
        })

    activities.sort(key=lambda x: x["time"], reverse=True)
    recent_activities = activities[:10]

    # Check for empty counts to hide cards
    metrics = {
        "properties": properties_count,
        "leads": leads_count,
        "visits": visits_count,
        "pending": pending_count,
        "revenue": revenue_display
    }

    stats = {
        "properties": Property.objects.public().count(),
        "cities": Property.objects.public().values("city").distinct().count(),
        "agents": 0,
        "sellers": User.objects.filter(role=User.Role.SELLER).count(),
        "leads": leads_count,
        "visits": visits_count,
        "inquiries": Inquiry.objects.count(),
        "pending": pending_count,
    }
    total_leads = stats["leads"]
    won_leads = Lead.objects.filter(stage=Lead.Stage.WON).count()
    stats["conversion_rate"] = int((won_leads / total_leads * 100)) if total_leads > 0 else 0

    # Traffic trend (real database views over last 7 days)
    import datetime
    from django.utils import timezone
    from django.db.models.functions import TruncDate
    today = timezone.now().date()
    last_7_days = [today - datetime.timedelta(days=i) for i in range(6, -1, -1)]
    views_by_date = (
        PropertyViewEvent.objects.filter(created_at__date__gte=last_7_days[0])
        .annotate(view_date=TruncDate("created_at"))
        .values("view_date")
        .annotate(count=Count("id"))
    )
    views_dict = {item["view_date"]: item["count"] for item in views_by_date}
    traffic_labels = [d.strftime("%a") for d in last_7_days]
    traffic_values = [views_dict.get(d, 0) for d in last_7_days]

    # Asset distribution (real property type distribution)
    type_counts = Property.objects.values("property_type").annotate(total=Count("id")).order_by("-total")
    type_display_map = dict(Property.PropertyType.choices)
    asset_labels = [type_display_map.get(item["property_type"], item["property_type"]).title() for item in type_counts]
    asset_values = [item["total"] for item in type_counts]
    if not asset_labels:
        asset_labels = ["None"]
        asset_values = [0]

    return render(
        request,
        "home.html",
        {
            "featured": featured,
            "stats": stats,
            "cities": cities,
            "metrics": metrics,
            "recent_activities": recent_activities,
            "traffic_labels": traffic_labels,
            "traffic_values": traffic_values,
            "asset_labels": asset_labels,
            "asset_values": asset_values,
        }
    )



def property_list(request):
    if request.GET.get("owner") == "me" and request.user.is_authenticated:
        qs = Property.objects.filter(created_by=request.user)
        # Check both status and approval_status filters for seller list
        status_filter = request.GET.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        else:
            approval_status_filter = request.GET.get("approval_status")
            if approval_status_filter:
                qs = qs.filter(approval_status=approval_status_filter)
        properties = qs.select_related("category", "created_by").prefetch_related("amenities").search(request.GET)
    else:
        # Default public search: filter by ACTIVE status unless 'status' is explicitly queried
        status_query = request.GET.get("status")
        if status_query in [Property.Status.ACTIVE, Property.Status.SOLD]:
            qs = Property.objects.public().filter(status=status_query)
        else:
            # Default to only ACTIVE properties
            qs = Property.objects.public().filter(status=Property.Status.ACTIVE)
        properties = qs.select_related("category", "created_by").prefetch_related("amenities").search(request.GET)
        
    return render(
        request,
        "properties/list.html",
        {
            "properties": properties,
            "categories": Category.objects.all(),
            "amenities": Amenity.objects.all(),
            "property_types": Property.PropertyType.choices,
            "filters": request.GET,
        },
    )


def city_page(request, city):
    # Public city page should show only active properties
    properties = Property.objects.public().filter(city__iexact=city, status=Property.Status.ACTIVE)
    return render(request, "properties/city.html", {"city": city, "properties": properties})


def property_detail(request, slug):
    prop = get_object_or_404(Property.objects.select_related("category", "created_by").prefetch_related("amenities", "images"), slug=slug)
    
    # Check public visibility: only Active and Sold properties approved by admin are public.
    is_public = (prop.status in [Property.Status.ACTIVE, Property.Status.SOLD]) and (prop.approval_status == Property.ApprovalStatus.APPROVED)
    if not is_public:
        if not request.user.is_authenticated or (prop.created_by != request.user and not request.user.is_admin_role):
            from django.http import Http404
            raise Http404("Property not found or restricted.")
            
    if prop.approval_status == Property.ApprovalStatus.APPROVED:
        Property.objects.filter(pk=prop.pk).update(view_count=F("view_count") + 1)
        prop.refresh_from_db(fields=["view_count"])
        PropertyViewEvent.objects.create(
            property=prop,
            user=request.user if request.user.is_authenticated else None,
            source=request.headers.get("referer", "")[:80] or "direct",
        )
    similar = Property.objects.public().filter(city=prop.city, status=Property.Status.ACTIVE).exclude(pk=prop.pk)[:4]
    
    gallery_count = prop.images.count()
    has_images = bool(prop.cover_image) or gallery_count > 0
    show_gallery_controls = (bool(prop.cover_image) and gallery_count > 0) or gallery_count > 1
    
    # Calculate performance analytics
    favs_count = prop.favorites.count()
    inqs_count = prop.inquiries.count()
    views_count = prop.view_count
    if views_count > 0:
        conversion_pct = round((inqs_count / views_count) * 100, 1)
    else:
        conversion_pct = 0.0

    return render(request, "properties/detail.html", {
        "property": prop, 
        "similar": similar,
        "has_images": has_images,
        "show_gallery_controls": show_gallery_controls,
        "analytics": {
            "views": views_count,
            "favorites": favs_count,
            "inquiries": inqs_count,
            "conversion": conversion_pct
        }
    })


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


@role_required(User.Role.SELLER, User.Role.ADMIN)
def property_create(request):
    if request.FILES:
        sanitize_uploaded_filenames(request.FILES)
    form = PropertyForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        prop = form.save(commit=False)
        prop.created_by = request.user
        prop.approval_status = Property.ApprovalStatus.APPROVED if request.user.is_admin_role else Property.ApprovalStatus.PENDING
        prop.save()
        form.save_m2m()
        
        # Handle multiple gallery images upload
        gallery_images = request.FILES.getlist("gallery_images")
        for img in gallery_images:
            PropertyImage.objects.create(property=prop, image=img)
            
        messages.success(request, "Property saved. Admin approval is required before it appears publicly.")
        return redirect("properties:detail", slug=prop.slug)
    return render(request, "properties/form.html", {"form": form, "title": "Add Property"})


@role_required(User.Role.SELLER, User.Role.ADMIN)
def property_update(request, slug):
    prop = get_object_or_404(Property, slug=slug)
    if prop.created_by != request.user and not request.user.is_admin_role:
        messages.error(request, "You can edit only your own listings.")
        return redirect("properties:detail", slug=prop.slug)
    if request.FILES:
        sanitize_uploaded_filenames(request.FILES)
    form = PropertyForm(request.POST or None, request.FILES or None, instance=prop)
    if request.method == "POST" and form.is_valid():
        updated = form.save(commit=False)
        if not request.user.is_admin_role:
            updated.approval_status = Property.ApprovalStatus.PENDING
        updated.save()
        form.save_m2m()
        
        # Handle multiple gallery images upload
        gallery_images = request.FILES.getlist("gallery_images")
        for img in gallery_images:
            PropertyImage.objects.create(property=updated, image=img)
            
        # Handle gallery images deletion
        delete_image_ids = request.POST.getlist("delete_images")
        if delete_image_ids:
            PropertyImage.objects.filter(id__in=delete_image_ids, property=updated).delete()
            
        messages.success(request, "Property updated.")
        return redirect("properties:detail", slug=updated.slug)
    return render(request, "properties/form.html", {"form": form, "property": prop, "title": "Edit Property"})


@role_required(User.Role.SELLER, User.Role.ADMIN)
def property_delete(request, slug):
    prop = get_object_or_404(Property, slug=slug)
    if prop.created_by != request.user and not request.user.is_admin_role:
        messages.error(request, "You can delete only your own listings.")
        return redirect("properties:detail", slug=prop.slug)
    if request.method == "POST":
        prop.delete()
        messages.success(request, "Property deleted.")
        return redirect("properties:list")
    return render(request, "properties/delete.html", {"property": prop})


@role_required(User.Role.ADMIN)
@require_POST
def approve_property(request, slug):
    prop = get_object_or_404(Property, slug=slug)
    prop.approval_status = Property.ApprovalStatus.APPROVED
    prop.status = Property.Status.APPROVED
    prop.rejection_reason = ""
    prop.save(update_fields=["approval_status", "status", "rejection_reason", "updated_at"])
    messages.success(request, "Property approved.")
    return redirect("properties:approvals_list")


@role_required(User.Role.ADMIN)
@require_POST
def reject_property(request, slug):
    prop = get_object_or_404(Property, slug=slug)
    prop.approval_status = Property.ApprovalStatus.REJECTED
    prop.status = Property.Status.DRAFT
    prop.rejection_reason = request.POST.get("reason", "Needs more information.")
    prop.save(update_fields=["approval_status", "status", "rejection_reason", "updated_at"])
    messages.warning(request, "Property rejected.")
    return redirect("properties:approvals_list")


@role_required(User.Role.ADMIN)
def approvals_list(request):
    pending = Property.objects.filter(approval_status=Property.ApprovalStatus.PENDING).select_related("category", "created_by")
    approved = Property.objects.filter(approval_status=Property.ApprovalStatus.APPROVED).select_related("category", "created_by")
    rejected = Property.objects.filter(approval_status=Property.ApprovalStatus.REJECTED).select_related("category", "created_by")
    return render(
        request,
        "properties/approvals.html",
        {
            "pending": pending,
            "approved": approved,
            "rejected": rejected,
        }
    )


class PropertyViewSet(viewsets.ModelViewSet):
    serializer_class = PropertySerializer
    queryset = Property.objects.select_related("category", "created_by").prefetch_related("amenities")

    def get_permissions(self):
        if self.action in {"list", "retrieve"}:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action in {"list", "retrieve"}:
            qs = qs.public()
        return qs.search(self.request.query_params)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class AmenityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    permission_classes = [permissions.AllowAny]


@role_required(User.Role.SELLER, User.Role.ADMIN)
@require_POST
def mark_property_sold(request, slug):
    prop = get_object_or_404(Property, slug=slug)
    if prop.created_by != request.user and not request.user.is_admin_role:
        messages.error(request, "You do not have permission to modify this property.")
        return redirect("properties:detail", slug=prop.slug)
    if prop.status != Property.Status.ACTIVE:
        messages.error(request, "Only active properties can be marked as sold.")
        return redirect("properties:detail", slug=prop.slug)
    
    prop.status = Property.Status.SOLD
    prop.save()
    messages.success(request, f"Property '{prop.title}' has been marked as SOLD.")
    return redirect("properties:detail", slug=prop.slug)


@role_required(User.Role.SELLER, User.Role.ADMIN)
@require_POST
def mark_property_closed(request, slug):
    prop = get_object_or_404(Property, slug=slug)
    if prop.created_by != request.user and not request.user.is_admin_role:
        messages.error(request, "You do not have permission to modify this property.")
        return redirect("properties:detail", slug=prop.slug)
    if prop.status != Property.Status.ACTIVE:
        messages.error(request, "Only active properties can be marked as closed.")
        return redirect("properties:detail", slug=prop.slug)
    
    prop.status = Property.Status.CLOSED
    prop.save()
    messages.success(request, f"Property '{prop.title}' has been closed.")
    return redirect("properties:detail", slug=prop.slug)


@role_required(User.Role.SELLER, User.Role.ADMIN)
@require_POST
def reopen_property(request, slug):
    prop = get_object_or_404(Property, slug=slug)
    if prop.created_by != request.user and not request.user.is_admin_role:
        messages.error(request, "You do not have permission to modify this property.")
        return redirect("properties:detail", slug=prop.slug)
    if prop.status != Property.Status.CLOSED:
        messages.error(request, "Only closed properties can be reopened.")
        return redirect("properties:detail", slug=prop.slug)
    
    prop.status = Property.Status.ACTIVE
    prop.save()
    messages.success(request, f"Property '{prop.title}' has been reopened and is now Active.")
    return redirect("properties:detail", slug=prop.slug)


@role_required(User.Role.SELLER, User.Role.ADMIN)
@require_POST
def activate_property(request, slug):
    prop = get_object_or_404(Property, slug=slug)
    if prop.created_by != request.user and not request.user.is_admin_role:
        messages.error(request, "You do not have permission to modify this property.")
        return redirect("properties:detail", slug=prop.slug)
    if prop.status != Property.Status.APPROVED:
        messages.error(request, "Only approved properties can be activated.")
        return redirect("properties:detail", slug=prop.slug)
    
    prop.status = Property.Status.ACTIVE
    prop.save()
    messages.success(request, f"Property '{prop.title}' is now Active and listed publicly.")
    return redirect("properties:detail", slug=prop.slug)


@role_required(User.Role.SELLER, User.Role.ADMIN)
@require_POST
def submit_for_approval(request, slug):
    prop = get_object_or_404(Property, slug=slug)
    if prop.created_by != request.user and not request.user.is_admin_role:
        messages.error(request, "You do not have permission to modify this property.")
        return redirect("properties:detail", slug=prop.slug)
    if prop.status != Property.Status.DRAFT:
        messages.error(request, "Only draft properties can be submitted for approval.")
        return redirect("properties:detail", slug=prop.slug)
    
    prop.status = Property.Status.PENDING
    prop.save()
    messages.success(request, f"Property '{prop.title}' has been submitted for approval.")
    return redirect("properties:detail", slug=prop.slug)

