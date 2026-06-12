from django.contrib import admin

from .models import AuditLog, PropertyViewEvent

admin.site.register([PropertyViewEvent, AuditLog])
