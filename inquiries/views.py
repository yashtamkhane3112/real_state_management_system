from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import permissions, viewsets
from rest_framework.exceptions import ValidationError

from properties.models import Property

from .forms import InquiryForm
from .models import Inquiry
from .serializers import InquirySerializer


@login_required
def create_inquiry(request, slug):
    prop = get_object_or_404(Property.objects.public(), slug=slug)
    if prop.status in [Property.Status.SOLD, Property.Status.CLOSED]:
        messages.error(request, "Inquiries are not allowed on sold or closed properties.")
        return redirect("properties:detail", slug=slug)
        
    # Restrict owners from inquiring on their own listings
    if prop.created_by == request.user:
        messages.error(request, "You cannot inquire on your own listing.")
        return redirect("properties:detail", slug=slug)
        
    # Restrict admins from inquiring
    if request.user.is_admin_role:
        messages.error(request, "Administrators cannot submit property inquiries.")
        return redirect("properties:detail", slug=slug)
        
    if request.method != "POST":
        return redirect("properties:detail", slug=slug)
    form = InquiryForm(request.POST)
    if form.is_valid():
        inquiry = form.save(commit=False)
        inquiry.property = prop
        inquiry.buyer = request.user
        inquiry.save()
        messages.success(request, "Inquiry sent. The listing owner can now follow up.")
    else:
        messages.error(request, "Please complete the inquiry form.")
    return redirect("properties:detail", slug=slug)


@login_required
def inquiry_list(request):
    user = request.user
    if user.is_admin_role:
        inquiries = Inquiry.objects.all().select_related("property", "buyer").order_by("-created_at")
    elif user.role == "seller":
        inquiries = Inquiry.objects.filter(property__created_by=user).select_related("property", "buyer").order_by("-created_at")
    else:
        inquiries = Inquiry.objects.filter(buyer=user).select_related("property", "buyer").order_by("-created_at")
        
    return render(
        request,
        "inquiries/list.html",
        {
            "inquiries": inquiries,
            "status_choices": Inquiry.Status.choices,
        }
    )


@login_required
def update_inquiry_status(request, pk):
    inquiry = get_object_or_404(Inquiry, pk=pk)
    if not request.user.is_admin_role and inquiry.property.created_by != request.user:
        messages.error(request, "You do not have permission to manage this inquiry.")
        return redirect("inquiries:list")
        
    if request.method == "POST":
        status = request.POST.get("status")
        if status in dict(Inquiry.Status.choices):
            inquiry.status = status
            inquiry.save()
            messages.success(request, f"Inquiry status updated to {inquiry.get_status_display()}.")
        else:
            messages.error(request, "Invalid status choice.")
            
    return redirect("inquiries:list")



class InquiryViewSet(viewsets.ModelViewSet):
    serializer_class = InquirySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Inquiry.objects.none()
        user = self.request.user
        qs = Inquiry.objects.select_related("property", "buyer")
        if user.is_admin_role:
            return qs
        if user.role == "seller":
            return qs.filter(property__created_by=user)
        return qs.filter(buyer=user)

    def perform_create(self, serializer):
        prop_id = self.request.data.get("property")
        if not prop_id:
            raise ValidationError({"property": "This field is required."})
        prop = get_object_or_404(Property, pk=prop_id)
        if prop.status in [Property.Status.SOLD, Property.Status.CLOSED]:
            raise ValidationError({"property": "Inquiries are not allowed on sold or closed properties."})
        serializer.save(buyer=self.request.user, property=prop)


