from django import forms

from .models import Visit


class VisitForm(forms.ModelForm):
    class Meta:
        model = Visit
        fields = ("scheduled_at", "notes")
        widgets = {"scheduled_at": forms.DateTimeInput(attrs={"type": "datetime-local"})}

