from django.db import models
from django.conf import settings
from django.urls import reverse


class Property(models.Model):
    PROPERTY_TYPES = [
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('villa', 'Villa'),
        ('plot', 'Plot / Land'),
        ('commercial', 'Commercial'),
        ('office', 'Office'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('active', 'Active'),
        ('rejected', 'Rejected'),
        ('sold', 'Sold'),
    ]
    LISTING_TYPE = [
        ('sale', 'For Sale'),
        ('rent', 'For Rent'),
    ]

    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='properties')
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES, default='apartment')
    listing_type = models.CharField(max_length=10, choices=LISTING_TYPE, default='sale')
    bedrooms = models.PositiveIntegerField(default=1)
    bathrooms = models.PositiveIntegerField(default=1)
    area = models.PositiveIntegerField(help_text='Area in sq ft')
    amenities = models.TextField(blank=True, help_text='Comma-separated amenities')
    cover_image = models.ImageField(upload_to='properties/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    is_featured = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Properties'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('properties:detail', args=[self.pk])

    def amenities_list(self):
        return [a.strip() for a in self.amenities.split(',') if a.strip()]


class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='properties/gallery/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.property.title}"


class Inquiry(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('replied', 'Replied'),
        ('closed', 'Closed'),
    ]
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='inquiries')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='inquiries')
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new')
    reply = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Inquiries'

    def __str__(self):
        return f"{self.name} -> {self.property.title}"


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'property')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} ♥ {self.property.title}"
