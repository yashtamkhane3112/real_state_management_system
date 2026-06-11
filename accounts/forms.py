from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Profile, User


class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    role = forms.ChoiceField(
        choices=[
            (User.Role.BUYER, "Buyer"),
            (User.Role.SELLER, "Seller"),
        ],
        widget=forms.Select(attrs={"class": "form-select"})
    )

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "phone", "role", "password1", "password2")
        widgets = {
            "phone": forms.TextInput(attrs={
                "class": "form-control", 
                "placeholder": "Phone number",
                "pattern": "[6-9][0-9]{9}",
                "title": "Phone number must be exactly 10 digits and start with 6, 7, 8, or 9."
            })
        }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if phone:
            import re
            if not re.match(r'^[6-9]\d{9}$', phone):
                raise forms.ValidationError("Phone number must be exactly 10 digits and start with 6, 7, 8, or 9.")
        return phone


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("city", "locality", "bio", "agency_name", "license_number", "budget_min", "budget_max")
        widgets = {
            "city": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter city"}),
            "locality": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter locality"}),
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Short bio..."}),
            "agency_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Agency name"}),
            "license_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "License number"}),
            "budget_min": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Min budget"}),
            "budget_max": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Max budget"}),
        }


class UserForm(forms.ModelForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email address"}))

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "phone", "avatar")
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "First name"}),
            "last_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Last name"}),
            "phone": forms.TextInput(attrs={
                "class": "form-control", 
                "placeholder": "Phone number",
                "pattern": "[6-9][0-9]{9}",
                "title": "Phone number must be exactly 10 digits and start with 6, 7, 8, or 9."
            }),
            "avatar": forms.FileInput(attrs={"class": "form-control"}),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email or not email.strip():
            raise forms.ValidationError("Email address cannot be empty.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if phone:
            import re
            if not re.match(r'^[6-9]\d{9}$', phone):
                raise forms.ValidationError("Phone number must be exactly 10 digits and start with 6, 7, 8, or 9.")
        return phone


