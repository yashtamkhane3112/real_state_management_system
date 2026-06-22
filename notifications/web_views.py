from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme

from .models import Notification
from .services import unread_count_for


@login_required
def notification_list(request):
    # Fetch once, derive unread count in Python — avoids a second DB query
    notifications = list(
        Notification.objects.filter(user=request.user)
        .order_by("-created_at")[:100]
    )
    unread_count = sum(1 for n in notifications if not n.is_read)
    return render(
        request,
        "dashboards/notifications.html",
        {
            "notifications": notifications,
            "unread_count": unread_count,
        },
    )


@login_required
def mark_read(request, pk):
    notif = Notification.objects.filter(pk=pk, user=request.user).first()
    if notif and not notif.is_read:
        notif.mark_read()
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "unread": unread_count_for(request.user)})
    
    # Handle optional next URL redirection
    next_url = request.GET.get("next")
    if next_url and url_has_allowed_host_and_scheme(url=next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return redirect(next_url)
    if notif and notif.link:
        return redirect(notif.link)
    return redirect("notifications:list")


@login_required
def mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True, read_at=timezone.now())
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "unread": 0})
    return redirect("notifications:list")


@login_required
def unread_badge(request):
    return JsonResponse({"unread": unread_count_for(request.user)})
