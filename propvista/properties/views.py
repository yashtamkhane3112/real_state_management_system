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
from .models import Amenity, Category, Property
from .serializers import AmenitySerializer, CategorySerializer, PropertySerializer


def home(request):
    featured = Property.objects.public().select_related("category", "created_by").prefetch_related("amenities")[:8]
    stats = {
        "properties": Property.objects.public().count(),
        "cities": Property.objects.public().values("city").distinct().count(),
        "agents": User.objects.filter(role=User.Role.AGENT).count(),
        "sellers": User.objects.filter(role=User.Role.SELLER).count(),
    }
    cities = Property.objects.public().values("city").annotate(total=Count("id")).order_by("-total")[:6]
    return render(request, "home.html", {"featured": featured, "stats": stats, "cities": cities})


def property_list(request):
    properties = Property.objects.public().select_related("category", "created_by").prefetch_related("amenities").search(request.GET)
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
    properties = Property.objects.public().filter(city__iexact=city)
    return render(request, "properties/city.html", {"city": city, "properties": properties})


def property_detail(request, slug):
    prop = get_object_or_404(Property.objects.select_related("category", "created_by").prefetch_related("amenities", "images"), slug=slug)
    if prop.approval_status == Property.ApprovalStatus.APPROVED:
        Property.objects.filter(pk=prop.pk).update(view_count=F("view_count") + 1)
        prop.refresh_from_db(fields=["view_count"])
        PropertyViewEvent.objects.create(
            property=prop,
            user=request.user if request.user.is_authenticated else None,
            source=request.headers.get("referer", "")[:80] or "direct",
        )
    similar = Property.objects.public().filter(city=prop.city).exclude(pk=prop.pk)[:4]
    return render(request, "properties/detail.html", {"property": prop, "similar": similar})


@role_required(User.Role.SELLER, User.Role.AGENT, User.Role.ADMIN)
def property_create(request):
    form = PropertyForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        prop = form.save(commit=False)
        prop.created_by = request.user
        prop.approval_status = Property.ApprovalStatus.APPROVED if request.user.is_admin_role else Property.ApprovalStatus.PENDING
        prop.save()
        form.save_m2m()
        messages.success(request, "Property saved. Admin approval is required before it appears publicly.")
        return redirect("properties:detail", slug=prop.slug)
    return render(request, "properties/form.html", {"form": form, "title": "Add Property"})


@login_required
def property_update(request, slug):
    prop = get_object_or_404(Property, slug=slug)
    if prop.created_by != request.user and not request.user.is_admin_role:
        messages.error(request, "You can edit only your own listings.")
        return redirect("properties:detail", slug=prop.slug)
    form = PropertyForm(request.POST or None, request.FILES or None, instance=prop)
    if request.method == "POST" and form.is_valid():
        updated = form.save(commit=False)
        if not request.user.is_admin_role:
            updated.approval_status = Property.ApprovalStatus.PENDING
        updated.save()
        form.save_m2m()
        messages.success(request, "Property updated.")
        return redirect("properties:detail", slug=updated.slug)
    image_form = PropertyImageForm()
    return render(request, "properties/form.html", {"form": form, "image_form": image_form, "property": prop, "title": "Edit Property"})


@login_required
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
    prop.rejection_reason = ""
    prop.save(update_fields=["approval_status", "rejection_reason", "updated_at"])
    messages.success(request, "Property approved.")
    return redirect("accounts:admin_dashboard")


@role_required(User.Role.ADMIN)
@require_POST
def reject_property(request, slug):
    prop = get_object_or_404(Property, slug=slug)
    prop.approval_status = Property.ApprovalStatus.REJECTED
    prop.rejection_reason = request.POST.get("reason", "Needs more information.")
    prop.save(update_fields=["approval_status", "rejection_reason", "updated_at"])
    messages.warning(request, "Property rejected.")
    return redirect("accounts:admin_dashboard")


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

