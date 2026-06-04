from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from properties.models import Property

from .models import Favorite


@login_required
@require_POST
def toggle(request, slug):
    prop = get_object_or_404(Property.objects.public(), slug=slug)
    favorite, created = Favorite.objects.get_or_create(user=request.user, property=prop)
    if not created:
        favorite.delete()
        messages.info(request, "Removed from wishlist.")
    else:
        messages.success(request, "Saved to wishlist.")
    return redirect("properties:detail", slug=slug)


@login_required
def wishlist(request):
    return render(request, "dashboards/wishlist.html", {"favorites": Favorite.objects.select_related("property").filter(user=request.user)})


