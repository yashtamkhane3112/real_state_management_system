"""
Property models for real estate marketplace.
"""
from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Property(models.Model):
    """Property listing model."""
    
    PROPERTY_TYPE_CHOICES = [
        ('house', 'House'),
        ('apartment', 'Apartment'),
        ('villa', 'Villa'),
        ('townhouse', 'Townhouse'),
        ('commercial', 'Commercial'),
        ('land', 'Land'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('sold', 'Sold'),
        ('rented', 'Rented'),
        ('pending', 'Pending'),
    ]
    
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='properties')
    title = models.CharField(max_length=200)
    description = models.TextField()
    slug = models.SlugField(unique=True, null=True, blank=True)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES, default='apartment')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    
    # Location
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='India')
    pincode = models.CharField(max_length=10)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    # Property Details
    price = models.DecimalField(max_digits=12, decimal_places=2)
    bedrooms = models.IntegerField(default=1)
    bathrooms = models.IntegerField(default=1)
    area = models.FloatField(help_text="Area in sq ft")
    
    # Features
    amenities = models.TextField(help_text="Comma-separated list of amenities")
    parking = models.BooleanField(default=True)
    balcony = models.BooleanField(default=False)
    garden = models.BooleanField(default=False)
    gym = models.BooleanField(default=False)
    swimming_pool = models.BooleanField(default=False)
    security = models.BooleanField(default=True)
    
    # Metadata
    is_featured = models.BooleanField(default=False)
    thumbnail = models.ImageField(upload_to='properties/thumbnails/')
    views = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Property'
        verbose_name_plural = 'Properties'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.city}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return f'/properties/{self.slug}/'
    
    def increment_views(self):
        self.views += 1
        self.save()


class PropertyImage(models.Model):
    """Images for properties."""
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='properties/images/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Property Image'
        verbose_name_plural = 'Property Images'
        ordering = ['-is_primary', 'uploaded_at']
    
    def __str__(self):
        return f"Image for {self.property.title}"


class Favorite(models.Model):
    """Favorite/Saved properties for users."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'property')
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.property.title}"
