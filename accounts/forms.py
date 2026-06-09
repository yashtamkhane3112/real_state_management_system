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
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "phone", "avatar")
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "First name"}),
            "last_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Last name"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email address"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone number"}),
            "avatar": forms.FileInput(attrs={"class": "form-control"}),
        }


