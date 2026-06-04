from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

from properties.models import Property

from .forms import VisitForm


@login_required
def book_visit(request, slug):
    prop = get_object_or_404(Property.objects.public(), slug=slug)
    if request.method != "POST":
        return redirect("properties:detail", slug=slug)
    form = VisitForm(request.POST)
    if form.is_valid():
        visit = form.save(commit=False)
        visit.property = prop
        visit.buyer = request.user
        visit.save()
        messages.success(request, "Visit requested.")
    else:
        messages.error(request, "Choose a valid visit time.")
    return redirect("properties:detail", slug=slug)

