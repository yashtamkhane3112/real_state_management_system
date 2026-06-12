from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render

from properties.models import Property


@login_required
def reports_home(request):
    city_data = Property.objects.values("city").annotate(total=Count("id")).order_by("-total")
    return render(request, "dashboards/reports.html", {"city_data": city_data})

