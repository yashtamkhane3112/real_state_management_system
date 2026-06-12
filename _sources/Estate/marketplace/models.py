from decimal import Decimal
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse

class Profile(models.Model):
    class Role(models.TextChoices):
        BUYER='BUYER','Buyer'; SELLER='SELLER','Seller'; ADMIN='ADMIN','Super Admin'
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name='profile')
    role=models.CharField(max_length=20,choices=Role.choices,default=Role.BUYER)
    phone=models.CharField(max_length=20,blank=True)
    address=models.TextField(blank=True)
    city=models.CharField(max_length=80,blank=True)
    avatar_url=models.URLField(blank=True)
    def __str__(self): return f'{self.user.username} - {self.get_role_display()}'

class BuyerProfile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name='buyer_profile')
    preferred_city=models.CharField(max_length=80,blank=True)
    min_budget=models.DecimalField(max_digits=12,decimal_places=2,default=0)
    max_budget=models.DecimalField(max_digits=12,decimal_places=2,default=0)
    def __str__(self): return self.user.get_full_name() or self.user.username

class SellerProfile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name='seller_profile')
    agency_name=models.CharField(max_length=120,blank=True)
    verified=models.BooleanField(default=False)
    def __str__(self): return self.agency_name or self.user.get_full_name() or self.user.username

class Property(models.Model):
    class PropertyType(models.TextChoices):
        FLAT='FLAT','Flat'; BUNGALOW='BUNGALOW','Bungalow'; PLOT='PLOT','Plot'; SHOP='SHOP','Shop'; OFFICE='OFFICE','Office'
    class Status(models.TextChoices):
        PENDING='PENDING','Pending Approval'; APPROVED='APPROVED','Available'; REJECTED='REJECTED','Rejected'; SOLD='SOLD','Sold'
    seller=models.ForeignKey(User,on_delete=models.CASCADE,related_name='properties')
    title=models.CharField(max_length=160)
    property_type=models.CharField(max_length=20,choices=PropertyType.choices)
    description=models.TextField()
    price=models.DecimalField(max_digits=12,decimal_places=2,validators=[MinValueValidator(Decimal('1.00'))])
    address=models.TextField()
    city=models.CharField(max_length=80)
    area_sqft=models.PositiveIntegerField(default=0)
    bedrooms=models.PositiveIntegerField(default=0)
    bathrooms=models.PositiveIntegerField(default=0)
    cover_image_url=models.URLField(blank=True)
    status=models.CharField(max_length=20,choices=Status.choices,default=Status.PENDING)
    rejection_reason=models.TextField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    class Meta:
        ordering=['-created_at']; verbose_name_plural='Properties'
    def __str__(self): return self.title
    def get_absolute_url(self): return reverse('property_detail',kwargs={'pk':self.pk})

class PropertyImage(models.Model):
    property=models.ForeignKey(Property,on_delete=models.CASCADE,related_name='gallery_images')
    image_url=models.URLField()
    caption=models.CharField(max_length=120,blank=True)
    def __str__(self): return self.caption or self.property.title

class Favorite(models.Model):
    buyer=models.ForeignKey(User,on_delete=models.CASCADE,related_name='favorites')
    property=models.ForeignKey(Property,on_delete=models.CASCADE,related_name='favorited_by')
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together=('buyer','property'); ordering=['-created_at']
    def __str__(self): return f'{self.buyer.username} saved {self.property.title}'

class Inquiry(models.Model):
    class Status(models.TextChoices):
        NEW='NEW','New'; VIEWED='VIEWED','Viewed'; RESPONDED='RESPONDED','Responded'
    property=models.ForeignKey(Property,on_delete=models.CASCADE,related_name='inquiries')
    buyer=models.ForeignKey(User,on_delete=models.CASCADE,related_name='inquiries')
    seller=models.ForeignKey(User,on_delete=models.CASCADE,related_name='seller_inquiries')
    buyer_name=models.CharField(max_length=120)
    email=models.EmailField()
    phone=models.CharField(max_length=20)
    message=models.TextField()
    status=models.CharField(max_length=20,choices=Status.choices,default=Status.NEW)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering=['-created_at']; verbose_name_plural='Inquiries'
    def __str__(self): return f'Inquiry for {self.property.title} by {self.buyer_name}'

class Transaction(models.Model):
    class Status(models.TextChoices):
        IN_PROGRESS='IN_PROGRESS','In Progress'; COMPLETED='COMPLETED','Completed'; CANCELLED='CANCELLED','Cancelled'
    property=models.ForeignKey(Property,on_delete=models.PROTECT,related_name='transactions')
    buyer=models.ForeignKey(User,on_delete=models.PROTECT,related_name='purchase_transactions')
    seller=models.ForeignKey(User,on_delete=models.PROTECT,related_name='sale_transactions')
    final_price=models.DecimalField(max_digits=12,decimal_places=2,validators=[MinValueValidator(Decimal('1.00'))])
    transaction_date=models.DateField()
    status=models.CharField(max_length=20,choices=Status.choices,default=Status.IN_PROGRESS)
    notes=models.TextField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['-transaction_date','-created_at']
    def __str__(self): return f'{self.property.title} - {self.get_status_display()}'
    def save(self,*args,**kwargs):
        super().save(*args,**kwargs)
        if self.status==self.Status.COMPLETED and self.property.status!=Property.Status.SOLD:
            self.property.status=Property.Status.SOLD
            self.property.save(update_fields=['status','updated_at'])
