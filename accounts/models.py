from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        BUYER = "buyer", "Buyer"
        SELLER = "seller", "Seller"
        AGENT = "agent", "Agent"
        ADMIN = "admin", "Admin"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.BUYER, db_index=True)
    phone = models.CharField(max_length=24, blank=True, db_index=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN or self.is_staff or self.is_superuser


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    city = models.CharField(max_length=100, blank=True, db_index=True)
    locality = models.CharField(max_length=120, blank=True)
    bio = models.TextField(blank=True)
    agency_name = models.CharField(max_length=160, blank=True)
    license_number = models.CharField(max_length=80, blank=True)
    budget_min = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    budget_max = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

