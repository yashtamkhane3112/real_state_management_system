from django.contrib import messages
from django.shortcuts import redirect, render

from accounts.decorators import role_required
from accounts.models import User

from .forms import LeadForm
from .models import Lead


@role_required(User.Role.SELLER, User.Role.AGENT, User.Role.ADMIN)
def lead_list(request):
    leads = Lead.objects.filter(owner=request.user) if not request.user.is_admin_role else Lead.objects.all()
    return render(request, "dashboards/leads.html", {"leads": leads})


@role_required(User.Role.SELLER, User.Role.AGENT, User.Role.ADMIN)
def lead_create(request):
    form = LeadForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        lead = form.save(commit=False)
        lead.owner = request.user
        lead.save()
        messages.success(request, "Lead created.")
        return redirect("leads:list")
    return render(request, "dashboards/lead_form.html", {"form": form})

