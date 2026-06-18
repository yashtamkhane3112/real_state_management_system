from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from properties.models import Property
from accounts.decorators import role_required, dashboard_role_required
from accounts.models import User

from .models import Favorite


@login_required
def toggle(request, slug):
    prop = get_object_or_404(Property.objects.public(), slug=slug)
    favorite, created = Favorite.objects.get_or_create(user=request.user, property=prop)
    if not created:
        favorite.delete()
        messages.info(request, "Removed from wishlist.")
    else:
        messages.success(request, "Saved to wishlist.")
    referer = request.META.get("HTTP_REFERER")
    if referer:
        return redirect(referer)
    return redirect("properties:detail", slug=slug)


@login_required
def wishlist(request):
    return render(request, "dashboards/wishlist.html", {"favorites": Favorite.objects.select_related("property").filter(user=request.user)})


@dashboard_role_required(User.Role.SELLER, User.Role.ADMIN)
def seller_favorites(request):
    favorites = Favorite.objects.filter(property__created_by=request.user).select_related("property", "user")
    return render(request, "dashboards/seller_favorites.html", {"favorites": favorites})


