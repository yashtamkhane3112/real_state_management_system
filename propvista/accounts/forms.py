from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Profile, User


class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "phone", "role", "password1", "password2")


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("city", "locality", "bio", "agency_name", "license_number", "budget_min", "budget_max")

