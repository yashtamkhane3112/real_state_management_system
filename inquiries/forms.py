from django import forms

from .models import Inquiry


class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ("name", "email", "phone", "message")
        widgets = {"message": forms.Textarea(attrs={"rows": 4})}

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if phone:
            import re
            if not re.match(r'^[6-9]\d{9}$', phone):
                raise forms.ValidationError("Phone number must be exactly 10 digits and start with 6, 7, 8, or 9.")
        return phone

