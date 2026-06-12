from django import forms

from .models import Lead, LeadActivity


class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ("property", "name", "phone", "email", "stage", "score", "notes", "follow_up_at")
        widgets = {"follow_up_at": forms.DateTimeInput(attrs={"type": "datetime-local"}), "notes": forms.Textarea(attrs={"rows": 3})}


class LeadActivityForm(forms.ModelForm):
    class Meta:
        model = LeadActivity
        fields = ("activity_type", "note")

