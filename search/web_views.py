from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from properties.models import Property

from .models import SavedSearch


def _merge_params(get_params):
    data = {}
    for key in get_params:
        values = get_params.getlist(key)
        if values:
            data[key] = values if len(values) > 1 else values[0]
    return data


@login_required
def saved_search_list(request):
    searches = SavedSearch.objects.filter(user=request.user)
    return render(request, "dashboards/saved_searches.html", {"searches": searches, "results": None})


@login_required
@require_POST
def saved_search_create(request):
    name = (request.POST.get("name") or "").strip() or "Saved search"
    query_params = _merge_params(request.GET)
    saved, created = SavedSearch.objects.get_or_create(
        user=request.user,
        name=name,
        defaults={"query_params": query_params, "notify_on_new": True},
    )
    if not created:
        saved.query_params = query_params
        saved.save(update_fields=["query_params", "updated_at"])
    messages.success(request, "Search saved.")
    return redirect(request.META.get("HTTP_REFERER") or "search:saved_list")


@login_required
def saved_search_run(request, pk):
    saved = get_object_or_404(SavedSearch, pk=pk, user=request.user)
    results = Property.objects.public().search(saved.query_params)
    return render(
        request,
        "dashboards/saved_searches.html",
        {"searches": SavedSearch.objects.filter(user=request.user), "results": results, "active": saved},
    )


@login_required
@require_POST
def saved_search_delete(request, pk):
    saved = get_object_or_404(SavedSearch, pk=pk, user=request.user)
    saved.delete()
    messages.info(request, "Saved search removed.")
    return redirect("search:saved_list")
