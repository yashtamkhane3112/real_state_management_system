from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from rest_framework import permissions, viewsets
from rest_framework.exceptions import ValidationError

from properties.models import Property

from .forms import InquiryForm
from .models import Inquiry
from .serializers import InquirySerializer


@login_required
def create_inquiry(request, slug):
    prop = get_object_or_404(Property.objects.public(), slug=slug)
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
        if user.role in {"seller", "agent"}:
            return qs.filter(property__created_by=user)
        return qs.filter(buyer=user)

    def perform_create(self, serializer):
        prop_id = self.request.data.get("property")
        if not prop_id:
            raise ValidationError({"property": "This field is required."})
        prop = get_object_or_404(Property, pk=prop_id)
        serializer.save(buyer=self.request.user, property=prop)


