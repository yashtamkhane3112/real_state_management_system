from django.contrib import messages
from django.shortcuts import redirect, render

from accounts.decorators import role_required
from accounts.models import User

from .forms import LeadForm
from .models import Lead


@role_required(User.Role.SELLER, User.Role.ADMIN)
def lead_list(request):
    leads = Lead.objects.filter(owner=request.user) if not request.user.is_admin_role else Lead.objects.all()
    return render(request, "dashboards/leads.html", {"leads": leads})


@role_required(User.Role.SELLER, User.Role.ADMIN)
def lead_create(request):
    form = LeadForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        lead = form.save(commit=False)
        lead.owner = request.user
        lead.save()
        messages.success(request, "Inquiry Pipeline entry created.")
        return redirect("leads:list")
    return render(request, "dashboards/lead_form.html", {"form": form})


@role_required(User.Role.SELLER, User.Role.ADMIN)
def lead_update(request, pk):
    from django.shortcuts import get_object_or_404
    lead = get_object_or_404(Lead, pk=pk)
    if not request.user.is_admin_role and lead.owner != request.user:
        messages.error(request, "You do not have permission to manage this inquiry.")
        return redirect("leads:list")
    form = LeadForm(request.POST or None, instance=lead)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Inquiry progress updated.")
        return redirect("leads:list")
    return render(request, "dashboards/lead_form.html", {"form": form})

