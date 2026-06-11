import os
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import get_valid_filename


def upload_avatar(instance, filename):
    name, ext = os.path.splitext(filename)
    name = get_valid_filename(name).replace(' ', '_')
    max_length = 50
    allowed_length = max_length - len(ext)
    if allowed_length <= 0:
        short_name = f"{uuid.uuid4().hex[:8]}{ext}"
    else:
        if len(name) > allowed_length:
            name = name[:allowed_length]
        short_name = f"{name}{ext}"
    return os.path.join("avatars/", short_name)


class User(AbstractUser):
    class Role(models.TextChoices):
        BUYER = "buyer", "Buyer"
        SELLER = "seller", "Seller"
        ADMIN = "admin", "Admin"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.BUYER, db_index=True)
    phone = models.CharField(max_length=24, blank=True, db_index=True)
    avatar = models.ImageField(upload_to=upload_avatar, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN or self.is_staff or self.is_superuser

    @property
    def initials(self):
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        elif self.first_name:
            return self.first_name[:2].upper()
        return self.username[:2].upper()

    @property
    def avatar_url(self):
        if self.avatar:
            try:
                mtime = int(self.avatar.storage.get_modified_time(self.avatar.name).timestamp())
                return f"{self.avatar.url}?t={mtime}"
            except Exception:
                return self.avatar.url
        return ""

    def has_perm(self, perm, obj=None):
        if self.is_active and (self.role == self.Role.ADMIN or self.is_superuser):
            return True
        return super().has_perm(perm, obj)

    def has_module_perms(self, app_label):
        if self.is_active and (self.role == self.Role.ADMIN or self.is_superuser):
            return True
        return super().has_module_perms(app_label)


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

