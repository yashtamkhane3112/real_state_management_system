from django.contrib import admin

from .models import Lead, LeadActivity

admin.site.register([Lead, LeadActivity])

