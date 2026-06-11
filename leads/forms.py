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

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if phone:
            import re
            if not re.match(r'^[6-9]\d{9}$', phone):
                raise forms.ValidationError("Phone number must be exactly 10 digits and start with 6, 7, 8, or 9.")
        return phone


class LeadActivityForm(forms.ModelForm):
    class Meta:
        model = LeadActivity
        fields = ("activity_type", "note")

