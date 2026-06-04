from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Notification
from .services import unread_count_for


@login_required
def notification_list(request):
    qs = Notification.objects.filter(user=request.user)
    unread_count = qs.filter(is_read=False).count()
    notifications = qs[:100]
    return render(
        request,
        "dashboards/notifications.html",
        {
            "notifications": notifications,
            "unread_count": unread_count,
        },
    )


@login_required
@require_POST
def mark_read(request, pk):
    notif = Notification.objects.filter(pk=pk, user=request.user).first()
    if notif and not notif.is_read:
        notif.mark_read()
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "unread": unread_count_for(request.user)})
    return redirect("notifications:list")


@login_required
@require_POST
def mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True, read_at=timezone.now())
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "unread": 0})
    return redirect("notifications:list")


@login_required
def unread_badge(request):
    return JsonResponse({"unread": unread_count_for(request.user)})
