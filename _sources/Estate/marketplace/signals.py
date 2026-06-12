from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import BuyerProfile, Profile, SellerProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        role=Profile.Role.ADMIN if instance.is_superuser else Profile.Role.BUYER
        Profile.objects.create(user=instance, role=role)

@receiver(post_save, sender=Profile)
def create_role_profile(sender, instance, **kwargs):
    if instance.role==Profile.Role.BUYER:
        BuyerProfile.objects.get_or_create(user=instance.user)
    elif instance.role==Profile.Role.SELLER:
        SellerProfile.objects.get_or_create(user=instance.user)
