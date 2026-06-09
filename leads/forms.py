from django import forms

from .models import Lead, LeadActivity


class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ("property", "name", "phone", "email", "stage", "score", "notes", "follow_up_at")
        widgets = {
            "follow_up_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.Select, forms.NullBooleanSelect)):
                field.widget.attrs["class"] = "form-select"
            else:
                field.widget.attrs["class"] = "form-control"


class LeadActivityForm(forms.ModelForm):
    class Meta:
        model = LeadActivity
        fields = ("activity_type", "note")

