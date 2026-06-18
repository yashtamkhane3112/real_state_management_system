from django.db.models import Count, Sum
from django.shortcuts import render

from properties.models import Property
from analytics.models import PropertyViewEvent, AuditLog
from inquiries.models import Inquiry
from visits.models import Visit
from accounts.decorators import role_required, dashboard_role_required
from accounts.models import User


@dashboard_role_required(User.Role.SELLER, User.Role.ADMIN)
def reports_home(request):
    city_data = Property.objects.values("city").annotate(total=Count("id")).order_by("-total")
    total_views = PropertyViewEvent.objects.count()
    total_visits = Visit.objects.count()
    total_inquiries = Inquiry.objects.count()
    
    # Advanced Analytics (Phase 6)
    most_viewed = Property.objects.annotate(vcount=Count("view_events")).order_by("-vcount").first()
    most_favorited = Property.objects.annotate(fcount=Count("favorites")).order_by("-fcount").first()
    
    # Calculate conversion: inquiries / views or visits / views
    if total_views > 0:
        lead_conv = round((total_inquiries / total_views) * 100, 1)
    else:
        lead_conv = 0
        
    total_value = Property.objects.aggregate(total=Sum("price"))["total"] or 0
    if total_value >= 10000000:
        pipeline_str = f"Rs {total_value / 10000000:.1f}Cr"
    elif total_value >= 100000:
        pipeline_str = f"Rs {total_value / 100000:.1f}L"
    else:
        pipeline_str = f"Rs {total_value:,}"
        
    inquiry_status_counts = Inquiry.objects.values("status").annotate(total=Count("id"))
    status_map = {item["status"]: item["total"] for item in inquiry_status_counts}
    chart_status_values = [
        status_map.get("new", 0) + status_map.get("contacted", 0),
        total_visits,
        status_map.get("qualified", 0),
        status_map.get("closed", 0),
    ]
    if sum(chart_status_values) == 0:
        chart_status_values = [0, 0, 0, 0]
        
    recent_audit = AuditLog.objects.select_related("actor").order_by("-created_at")[:5]
    from accounts.models import User
    from favorites.models import Favorite
    buyer_count = User.objects.filter(role=User.Role.BUYER).count()
    favorite_count = Favorite.objects.count()
    top_city = city_data[0] if city_data.exists() else None

    total_active = Property.objects.filter(status=Property.Status.ACTIVE).count()
    total_sold = Property.objects.filter(status=Property.Status.SOLD).count()
    total_closed = Property.objects.filter(status=Property.Status.CLOSED).count()
    total_lifecycle = total_active + total_sold + total_closed
    sales_conversion_rate = round((total_sold / total_lifecycle) * 100, 1) if total_lifecycle > 0 else 0.0

    context = {
        "city_data": city_data,
        "total_views": total_views,
        "total_visits": total_visits,
        "total_inquiries": total_inquiries,
        "lead_conv": lead_conv,
        "pipeline_str": pipeline_str,
        "chart_status_values": chart_status_values,
        "recent_audit": recent_audit,
        "buyer_count": buyer_count,
        "favorite_count": favorite_count,
        "top_city": top_city,
        "most_viewed": most_viewed,
        "most_favorited": most_favorited,
        "total_active": total_active,
        "total_sold": total_sold,
        "total_closed": total_closed,
        "sales_conversion_rate": sales_conversion_rate,
    }
    return render(request, "dashboards/reports.html", context)


@role_required(User.Role.ADMIN)
def download_audit_logs(request):
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="audit_logs.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Actor', 'Action', 'Object Type', 'Object ID', 'Metadata', 'Created At'])
    
    logs = AuditLog.objects.select_related("actor").all().order_by("-created_at")
    for log in logs:
        actor_name = log.actor.username if log.actor else 'System'
        writer.writerow([
            log.id, 
            actor_name, 
            log.action, 
            log.object_type, 
            log.object_id, 
            str(log.metadata), 
            log.created_at.strftime('%Y-%m-%d %H:%M:%S') if log.created_at else ''
        ])
        
    return response

