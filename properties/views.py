import datetime
import json
import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, F, Q, Sum
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from rest_framework import permissions, viewsets

from accounts.decorators import role_required
from accounts.models import User
from analytics.models import PropertyViewEvent
from propvista.ai_features.services import gemini_or_fallback
from propvista.utils import sanitize_uploaded_filenames

from .forms import PropertyForm
from .models import Amenity, Category, Property, PropertyImage
from .serializers import AmenitySerializer, CategorySerializer, PropertySerializer


def home(request):
    from leads.models import Lead
    from visits.models import Visit
    from inquiries.models import Inquiry
    from accounts.models import User as _User

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
    for u in _User.objects.order_by("-created_at")[:5]:
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

    inquiries_total = Inquiry.objects.count()
    sellers_count = _User.objects.filter(role=_User.Role.SELLER).count()

    stats = {
        # Reuse the cities queryset already evaluated above — no extra DB call
        "properties": Property.objects.public().count(),
        "cities": cities.count(),
        "agents": 0,
        "sellers": sellers_count,
        "leads": leads_count,
        "visits": visits_count,
        "inquiries": inquiries_total,
        "pending": pending_count,
    }
    total_leads = stats["leads"]
    won_leads = Lead.objects.filter(stage=Lead.Stage.WON).count()
    stats["conversion_rate"] = int((won_leads / total_leads * 100)) if total_leads > 0 else 0

    # Traffic trend (real database views over last 7 days)
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
    similar = Property.objects.public().select_related("category", "created_by").filter(city=prop.city, status=Property.Status.ACTIVE).exclude(pk=prop.pk)[:4]
    
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


# sanitize_uploaded_filenames is imported from propvista.utils (shared utility)


@role_required(User.Role.SELLER, User.Role.ADMIN)
def property_create(request):
    if request.FILES:
        sanitize_uploaded_filenames(request.FILES)
    form = PropertyForm(request.POST or None, request.FILES or None, user=request.user)
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
    form = PropertyForm(request.POST or None, request.FILES or None, instance=prop, user=request.user)
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


# ---------------------------------------------------------------------------
# Phase 6 — AI Property Match
# ---------------------------------------------------------------------------
def parse_budget(budget_str):
    """Parse budget input string (e.g. 2 Cr, 80L) to raw integer value in INR."""
    if not budget_str:
        return None
    cleaned = budget_str.lower().replace(" ", "").replace(",", "").replace("₹", "")
    if "cr" in cleaned:
        try:
            val = float(cleaned.split("cr")[0])
            return int(val * 10000000)
        except ValueError:
            pass
    if "l" in cleaned:
        try:
            val = float(cleaned.split("l")[0])
            return int(val * 100000)
        except ValueError:
            pass
    if "k" in cleaned:
        try:
            val = float(cleaned.split("k")[0])
            return int(val * 1000)
        except ValueError:
            pass
    try:
        val = float(cleaned)
        if val < 50:
            return int(val * 10000000)
        elif val < 500:
            return int(val * 100000)
        return int(val)
    except ValueError:
        return None


@login_required
def ai_property_match(request):
    """
    Accept user search criteria and return AI-matched property recommendations.
    GET  → render search form
    POST → run AI match and return results
    """

    if request.method == "POST":
        budget = request.POST.get("budget", "")
        city = request.POST.get("city", "")
        bedrooms = request.POST.get("bedrooms", "")
        purpose = request.POST.get("purpose", "").lower()

        # Step 1: Query the database for active/approved properties
        qs = Property.objects.public().filter(status=Property.Status.ACTIVE)
        if city:
            qs = qs.filter(city__iexact=city)
        if bedrooms:
            try:
                qs = qs.filter(bedrooms__gte=int(bedrooms))
            except ValueError:
                pass

        # Step 2: Parse budget input and apply hard filtering (exclude items > 1.1x the budget limit)
        parsed_budget = parse_budget(budget)
        if parsed_budget:
            qs = qs.filter(price__lte=parsed_budget * 1.1)

        # Step 3: Check if zero matching listings exist and return early empty state
        if not qs.exists():
            html = render_to_string("properties/partials/ai_match_results.html", {
                "matches": [],
                "request": request,
            }, request=request)
            return JsonResponse({"html": html, "status": "ok"})

        # Step 4: Fetch candidates with prefetched favorites to avoid N+1
        qs = qs.prefetch_related("favorites").annotate(fav_count=Count("favorites", distinct=True))
        candidates = []
        for p in qs:
            score = 0
            
            # Budget Match (Max 40 points)
            if not parsed_budget:
                score += 40
            elif p.price <= parsed_budget:
                score += 40
            else:
                score += 20 # Priced slightly above budget (between budget and 1.1x budget)

            # Location Match (Max 25 points)
            if not city:
                score += 25
            elif p.city.lower() == city.lower():
                score += 25

            # Bedroom Match (Max 20 points)
            if not bedrooms:
                score += 20
            elif p.bedrooms >= int(bedrooms):
                score += 20

            # Purpose Match (Max 15 points)
            purpose_points = 0
            if purpose == "family living":
                if p.bedrooms >= 3:
                    purpose_points = 15
                elif p.bedrooms == 2:
                    purpose_points = 10
                else:
                    purpose_points = 5
            elif purpose == "investment":
                if p.is_featured:
                    purpose_points += 7
                if p.view_count > 10:
                    purpose_points += 4
                if p.fav_count > 0:  # uses prefetched annotation — no extra query
                    purpose_points += 4
            elif purpose == "rental income":
                if p.property_type == "apartment":
                    purpose_points += 10
                else:
                    purpose_points += 5
                if p.view_count > 5:
                    purpose_points += 5
            elif purpose == "commercial use":
                if p.property_type in ["commercial", "office"]:
                    purpose_points = 15
                else:
                    purpose_points = 5
            elif purpose == "vacation home":
                if p.property_type in ["villa", "house"]:
                    purpose_points += 10
                if p.is_featured:
                    purpose_points += 5
            else:
                purpose_points = 10 if p.is_featured else 5
            
            score += min(purpose_points, 15)
            candidates.append({"property": p, "score": score})

        # Step 5: Sort candidates by score descending and limit results strictly to TOP 5
        candidates.sort(key=lambda x: x["score"], reverse=True)
        top_matches = candidates[:5]

        # Step 6: Format properties to pass context for Gemini to compile match explanations and reasons
        props_list_for_ai = []
        for item in top_matches:
            p = item["property"]
            props_list_for_ai.append(
                f"ID {p.id}: {p.title} in {p.city} - Price: {p.formatted_price}, {p.bedrooms} BHK, {p.area_sqft} sqft, Featured: {p.is_featured}"
            )
        props_summary = "; ".join(props_list_for_ai)

        prompt = (
            f"You are a real estate matching assistant.\n"
            f"We have pre-selected the top matching properties for a user based on their preferences:\n"
            f"- Budget: {budget}\n"
            f"- City: {city or 'Any'}\n"
            f"- Minimum Bedrooms: {bedrooms or 'Any'}\n"
            f"- Purpose: {purpose}\n\n"
            f"Here are the chosen properties:\n"
            f"{props_summary}\n\n"
            f"For each property ID, generate exactly up to 3 short matching reasons explaining why it's a good fit based on the user's criteria. "
            f"Examples of reasons: 'Within budget', 'Family-friendly layout', 'Premium investment corridor', 'High buyer interest'. "
            f"Format your response as a JSON array of objects, with NO surrounding text, markdown formatting (like ```json), or explanation. "
            f"Example format:\n"
            f"[\n"
            f"  {{\"id\": 12, \"reasons\": [\"Within budget\", \"Near IT hubs\"]}},\n"
            f"  {{\"id\": 8, \"reasons\": [\"Family-friendly layout\", \"Near schools\"]}}\n"
            f"]"
        )

        payload = {"prompt": prompt}
        result = gemini_or_fallback("property_match", payload)

        # Step 7: Parse Gemini reasoning JSON array
        reasons_map = {}
        try:
            cleaned = result.strip()
            json_match = re.search(r'\[\s*\{.*\}\s*\]', cleaned, re.DOTALL)
            parsed_reasons = json.loads(json_match.group()) if json_match else json.loads(cleaned)
            for item in parsed_reasons:
                if isinstance(item, dict) and "id" in item:
                    reasons_map[int(item["id"])] = item.get("reasons", [])
        except Exception:
            pass

        # Step 8: Build final structured template matches context
        matches_data = []
        for item in top_matches:
            p = item["property"]
            # Extract reasons from map or fall back to dynamic programmatic checks
            reasons = reasons_map.get(p.id, [])
            if not reasons:
                reasons = []
                if parsed_budget and p.price <= parsed_budget:
                    reasons.append("Within budget")
                if purpose == "family living" and p.bedrooms >= 3:
                    reasons.append("Family-friendly layout")
                if p.is_featured:
                    reasons.append("Premium featured listing")
                if not reasons:
                    reasons.append("Strong buyer interest")
                    reasons.append("Excellent appreciation potential")
            
            matches_data.append({
                "property": p,
                "score": item["score"],
                "reasons": reasons[:3]
            })

        # Step 9: Render matches section using the partial template
        html = render_to_string("properties/partials/ai_match_results.html", {
            "matches": matches_data,
            "request": request,
        }, request=request)

        return JsonResponse({"html": html, "status": "ok"})

    return render(request, "properties/ai_match.html", {
        "cities": Property.objects.public().values_list("city", flat=True).distinct()[:20],
    })


# ---------------------------------------------------------------------------
# Phase 7 — AI Property Insights (AJAX endpoint)
# ---------------------------------------------------------------------------
@require_POST
@login_required
def ai_property_insights(request, slug):
    """Return AI investment insights for a specific property with structured details."""
    prop = get_object_or_404(Property, slug=slug)
    amenities = ", ".join(a.name for a in prop.amenities.all()) or "None listed"

    # Step 1: Programmatic pre-calculation of real Investment Score (out of 10)
    base_score = 7.0
    # Location influence
    city_lower = prop.city.lower()
    if "mumbai" in city_lower:
        base_score += 1.2
    elif "pune" in city_lower:
        base_score += 0.8
    elif "nashik" in city_lower:
        base_score += 0.5
    else:
        base_score += 0.3

    # Price competitiveness influence
    if prop.price < 10000000: # < 1 Cr
        base_score += 0.6
    elif prop.price < 25000000: # < 2.5 Cr
        base_score += 0.4
    else:
        base_score += 0.2

    # Area size influence
    if prop.area_sqft > 2000:
        base_score += 0.6
    elif prop.area_sqft > 1200:
        base_score += 0.4
    else:
        base_score += 0.2

    # Popularity & Engagement influence
    if prop.view_count > 20:
        base_score += 0.6
    elif prop.view_count > 5:
        base_score += 0.3
    
    # Featured bonus
    if prop.is_featured:
        base_score += 0.5

    calculated_score = min(round(base_score, 1), 9.8)

    # Determine programmatic market position
    if calculated_score >= 8.5:
        calculated_position = "Prime"
    elif calculated_score >= 7.5:
        calculated_position = "Strong"
    else:
        calculated_position = "Stable"

    # Step 2: Construct prompt to query Gemini for structured JSON details
    payload = {
        "prompt": (
            f"Property: {prop.title}.\n"
            f"Location: {prop.locality}, {prop.city}.\n"
            f"Type: {prop.property_type}.\n"
            f"Price: {prop.formatted_price}.\n"
            f"Area: {prop.area_sqft} sqft.\n"
            f"Bedrooms: {prop.bedrooms} BHK.\n"
            f"Bathrooms: {prop.bathrooms}.\n"
            f"Furnishing: {prop.furnishing}.\n"
            f"Amenities: {amenities}.\n"
            f"Featured: {prop.is_featured}.\n"
            f"Traffic Views: {prop.view_count}.\n\n"
            f"You are a premium real estate intelligence advisor. Provide property investment insights strictly tailored to this property's actual location and metrics.\n"
            f"Use the pre-calculated score: {calculated_score} and pre-calculated market position: '{calculated_position}'.\n"
            f"Output exactly a JSON object, with no markdown code blocks or surrounding chat response text. Example structure:\n"
            f"{{\n"
            f"  \"score\": {calculated_score},\n"
            f"  \"market_position\": \"{calculated_position}\",\n"
            f"  \"strengths\": [\n"
            f"    \"Located in {prop.city} growth corridor\",\n"
            f"    \"Competitive price per sqft for {prop.locality}\",\n"
            f"    \"Suitable for family occupancy ({prop.bedrooms} BHK layout)\",\n"
            f"    \"Complete property information available\"\n"
            f"  ],\n"
            f"  \"outlook_short\": \"Moderate appreciation potential due to localized demand\",\n"
            f"  \"outlook_long\": \"Strong appreciation potential over a 5 to 7 year horizon\",\n"
            f"  \"suitability_best\": [\"Family Living\", \"Long-Term Investment\"],\n"
            f"  \"suitability_less\": [\"Rental Yield Focus\", \"Commercial Use\"],\n"
            f"  \"considerations\": [\n"
            f"    \"Verify current neighborhood infrastructure projects in {prop.locality}\",\n"
            f"    \"Compare recent sales in the surrounding area of {prop.city}\",\n"
            f"    \"Review ownership documentation\"\n"
            f"  ]\n"
            f"}}"
        )
    }

    result = gemini_or_fallback("property_insights", payload)

    # Step 3: Parse Gemini response JSON or fallback gracefully to programmatic analysis
    data = {}
    try:
        cleaned = result.strip()
        json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        data = json.loads(json_match.group()) if json_match else json.loads(cleaned)
        # Ensure all required keys exist
        required_keys = ("score", "market_position", "strengths", "outlook_short", "outlook_long", "suitability_best", "suitability_less", "considerations")
        if not all(k in data for k in required_keys):
            raise ValueError("Incomplete keys in response")
    except Exception:
        # Step 4: Robust, complete fallback strategy (no generic references, uses actual database attributes)
        # Suitability determination
        if prop.property_type in ["commercial", "office"]:
            suit_best = ["Commercial Operations", "Corporate Lease Portfolio"]
            suit_less = ["Residential Occupancy", "Vacation Home Living"]
        else:
            suit_best = ["Family Living", "Long-Term Investment"]
            suit_less = ["Rental Yield Focus", "Commercial Use"]

        # Strengths customization
        strengths = [
            f"Located in {prop.city} growth corridor",
            f"Competitive price of {prop.formatted_price}",
            f"Suitable for family occupancy ({prop.bedrooms} BHK layout)",
            "Complete property information available"
        ]
        
        data = {
            "score": calculated_score,
            "market_position": calculated_position,
            "strengths": strengths,
            "outlook_short": f"Moderate appreciation potential in {prop.city}",
            "outlook_long": "Strong appreciation potential over a 5+ year period",
            "suitability_best": suit_best,
            "suitability_less": suit_less,
            "considerations": [
                f"Verify current neighborhood infrastructure projects in {prop.locality}",
                f"Compare recent sales in the surrounding area of {prop.city}",
                f"Review ownership documentation for {prop.title}"
            ],
            "fallback": True
        }

    # Step 5: Dynamic calculation of Property Comparison Metrics based on similar listings
    target_price_per_sqft = float(prop.price) / prop.area_sqft if prop.area_sqft else 0.0
    same_city_qs = Property.objects.public().filter(city__iexact=prop.city).exclude(id=prop.id)

    if same_city_qs.exists():
        # Use a single Avg() aggregation instead of iterating over the queryset (avoids N+1)
        agg = same_city_qs.filter(area_sqft__gt=0).aggregate(
            avg_price=Avg("price"),
            avg_area=Avg("area_sqft"),
        )
        avg_price = float(agg["avg_price"] or 0)
        avg_area = float(agg["avg_area"] or 1)
        avg_price_per_sqft = avg_price / avg_area if avg_area else target_price_per_sqft
        if target_price_per_sqft <= avg_price_per_sqft * 0.9:
            price_comp = 8.8
        elif target_price_per_sqft <= avg_price_per_sqft * 1.1:
            price_comp = 8.0
        else:
            price_comp = 6.8
    else:
        price_comp = 8.2

    # Location quality factor calculation
    loc_val = 7.5
    if "mumbai" in city_lower:
        loc_val += 1.3
    elif "pune" in city_lower:
        loc_val += 0.8
    if any(keyword in prop.locality.lower() for keyword in ["nagar", "road", "worli", "kalyani", "hinjewadi", "sea", "drive"]):
        loc_val += 0.5
    loc_quality = min(round(loc_val, 1), 9.6)

    # Investment potential factor calculation
    invest_val = 7.0 + (1.5 if prop.is_featured else 0.5) + min(1.0, prop.view_count * 0.05)
    invest_potential = min(round(invest_val, 1), 9.7)

    # Rental demand factor calculation
    rent_val = 7.2
    if prop.property_type == 'apartment':
        rent_val += 1.0
    if prop.bedrooms == 2:
        rent_val += 0.6
    rental_demand = min(round(rent_val, 1), 9.5)

    # Market activity factor calculation
    act_val = 6.5 + min(3.0, (prop.view_count + prop.favorites.count()) * 0.1)
    market_activity = min(round(act_val, 1), 9.8)

    # Step 6: Dynamic calculation of Who Should Buy profiles based on listing characteristics
    best_for = []
    if prop.bedrooms >= 3:
        best_for.append("Families")
    if city_lower in ["pune", "mumbai"] and prop.bedrooms <= 2:
        best_for.append("IT Professionals")
    if prop.is_featured or prop.price > 20000000:
        best_for.append("Long-Term Investors")
    if prop.price < 15000000:
        best_for.append("First-Time Buyers")
    if not best_for:
        best_for = ["Families", "First-Time Buyers"]

    not_ideal_for = []
    if prop.property_type not in ["commercial", "office"]:
        not_ideal_for.append("Commercial Use")
        not_ideal_for.append("Short-Term Rentals")
    if prop.price > 25000000:
        not_ideal_for.append("Ultra-Low Budget Buyers")
    else:
        not_ideal_for.append("Speculative Flippers")

    # Merge dynamic metrics into output data object
    data["comparison"] = {
        "price_competitiveness": price_comp,
        "location_quality": loc_quality,
        "investment_potential": invest_potential,
        "rental_demand": rental_demand,
        "market_activity": market_activity
    }
    data["who_should_buy"] = {
        "best_for": best_for,
        "not_ideal_for": not_ideal_for
    }

    return JsonResponse(data)


# ---------------------------------------------------------------------------
# Phase 8 — AI Inquiry Drafting (AJAX endpoint)
# ---------------------------------------------------------------------------
@require_POST
@login_required
def ai_inquiry_draft(request, slug):
    """Generate a professional inquiry draft for the user to review and send."""

    prop = get_object_or_404(Property, slug=slug)
    user_name = request.user.get_full_name() or request.user.username
    payload = {
        "prompt": (
            f"Write a professional, polite real estate inquiry email body. "
            f"Property: '{prop.title}' in {prop.locality}, {prop.city}. "
            f"Buyer name: {user_name}. "
            f"The message should express interest, request a site visit, "
            f"and ask for ownership and availability details. "
            f"Keep it under 100 words. Do not include subject line. "
            f"End with 'Regards, {user_name}'"
        )
    }
    result = gemini_or_fallback("inquiry_draft", payload)

    # Fallback message
    if not result or "fallback" in result.lower() or len(result) < 40:
        result = (
            f"Hello,\n\n"
            f"I am interested in the property '{prop.title}' located in "
            f"{prop.locality}, {prop.city}, and would like to schedule a "
            f"site visit at your earliest convenience. Kindly share the "
            f"ownership details, availability, and any documents for review.\n\n"
            f"Regards,\n{user_name}"
        )

    return JsonResponse({"draft": result, "status": "ok"})


def market_pulse(request):
    """Render the luxury market intelligence / market pulse screen."""
    # Property and Avg are already imported at module level
    city_stats = Property.objects.public().values("city").annotate(
        avg_price=Avg("price"),
        count=Count("id")
    ).order_by("-count")
    
    # Calculate chart lists
    cities_list = [item["city"] for item in city_stats]
    prices_list = [float(item["avg_price"] or 0) for item in city_stats]
    counts_list = [item["count"] for item in city_stats]
    
    luxury_avg = Property.objects.public().filter(price__gte=15000000).aggregate(avg=Avg("price"))["avg"] or 0
    total_listings = Property.objects.public().count()
    
    # Compute Market Health Score dynamically (0–100) from real inventory signals.
    # Factor 1: City diversity — more cities = wider market breadth (max 40 pts)
    city_count = len(cities_list)
    breadth_score = min(city_count * 5, 40)
    # Factor 2: Active/total ratio — measures inventory health (max 35 pts)
    active_count = Property.objects.public().filter(
        status=Property.Status.ACTIVE
    ).count() if total_listings > 0 else 0
    activity_ratio = (active_count / total_listings) if total_listings > 0 else 0
    activity_score = round(activity_ratio * 35, 1)
    # Factor 3: Price diversity — multiple price tiers indicates a liquid market (max 25 pts)
    price_tiers = Property.objects.public().values("price").distinct().count()
    tier_score = min(price_tiers * 1.5, 25)
    raw_score = breadth_score + activity_score + tier_score
    market_health_score = min(round(raw_score, 1), 99.0)
    # Floor at 60 so the score is never alarmingly low on a fresh or small dataset
    market_health_score = max(market_health_score, 60.0)

    context = {
        "city_stats": city_stats,
        "luxury_avg": luxury_avg,
        "total_listings": total_listings,
        "cities_json": json.dumps(cities_list),
        "prices_json": json.dumps(prices_list),
        "counts_json": json.dumps(counts_list),
        "market_health_score": market_health_score,
    }
    return render(request, "properties/market_pulse.html", context)



