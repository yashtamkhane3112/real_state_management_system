# Django Integration Guide

Complete guide for converting the RealEstate Pro HTML/CSS/Bootstrap templates into a Django application.

## Step 1: Project Setup

### Create Django Project
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install django
django-admin startproject realestate_pro
cd realestate_pro
python manage.py startapp marketplace
python manage.py startapp accounts
python manage.py startapp properties
python manage.py startapp messaging
```

### Directory Structure
```
realestate_pro/
├── realestate_pro/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── marketplace/
│   ├── migrations/
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── properties/
│   │   │   ├── list.html
│   │   │   └── detail.html
│   │   └── dashboard/
│   │       ├── buyer.html
│   │       ├── seller.html
│   │       └── admin.html
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
├── accounts/
│   ├── templates/
│   │   ├── login.html
│   │   ├── register.html
│   │   └── profile.html
│   ├── models.py
│   └── views.py
├── properties/
│   ├── models.py
│   └── views.py
├── messaging/
│   ├── models.py
│   └── views.py
├── static/
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── main.js
├── media/
│   ├── properties/
│   └── users/
├── templates/
│   └── base.html
└── manage.py
```

## Step 2: Configure Settings

### settings.py
```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'marketplace',
    'accounts',
    'properties',
    'messaging',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

AUTH_USER_MODEL = 'accounts.CustomUser'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Security
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'yourdomain.com']
CSRF_TRUSTED_ORIGINS = ['https://yourdomain.com']
SECURE_SSL_REDIRECT = False  # Set to True in production
```

## Step 3: Create Models

### accounts/models.py
```python
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
    )
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='buyer')
    phone = models.CharField(max_length=15, blank=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='users/', null=True, blank=True)
    verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

class UserAddress(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='address')
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    country = models.CharField(max_length=100, default='USA')
    
    class Meta:
        verbose_name_plural = "User Addresses"
    
    def __str__(self):
        return f"{self.street_address}, {self.city}, {self.state}"
```

### properties/models.py
```python
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()

class PropertyType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Property Types"
    
    def __str__(self):
        return self.name

class Property(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('sold', 'Sold'),
        ('rented', 'Rented'),
    )
    
    LIST_TYPE_CHOICES = (
        ('sale', 'For Sale'),
        ('rent', 'For Rent'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    property_type = models.ForeignKey(PropertyType, on_delete=models.SET_NULL, null=True)
    list_type = models.CharField(max_length=10, choices=LIST_TYPE_CHOICES, default='sale')
    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    
    # Location
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    
    # Details
    bedrooms = models.IntegerField(validators=[MinValueValidator(0)])
    bathrooms = models.IntegerField(validators=[MinValueValidator(0)])
    square_feet = models.IntegerField(validators=[MinValueValidator(0)])
    year_built = models.IntegerField()
    
    # Amenities (JSON)
    amenities = models.JSONField(default=list, blank=True)
    
    # Owner
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    featured = models.BooleanField(default=False)
    views_count = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['city', 'status']),
            models.Index(fields=['price', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.city}"
    
    def get_full_address(self):
        return f"{self.street_address}, {self.city}, {self.state} {self.zip_code}"

class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='properties/')
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_primary', 'uploaded_at']
    
    def __str__(self):
        return f"Image for {self.property.title}"

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'property')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} liked {self.property.title}"

class Offer(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    )
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='offers')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offers_made')
    offer_price = models.DecimalField(max_digits=12, decimal_places=2)
    offer_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-offer_date']
    
    def __str__(self):
        return f"Offer on {self.property.title} by {self.buyer.username}"
```

### messaging/models.py
```python
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')
    property = models.ForeignKey('properties.Property', on_delete=models.SET_NULL, 
                                 null=True, blank=True, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Conversation #{self.id}"

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message from {self.sender.username}"
```

## Step 4: Create Views

### marketplace/views.py
```python
from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView
from properties.models import Property

class HomeView(TemplateView):
    template_name = 'index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_properties'] = Property.objects.filter(
            featured=True, status='active'
        )[:3]
        context['recent_properties'] = Property.objects.filter(
            status='active'
        ).order_by('-created_at')[:6]
        return context

class PropertyListView(ListView):
    model = Property
    template_name = 'properties/list.html'
    context_object_name = 'properties'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Property.objects.filter(status='active')
        
        # Filters
        city = self.request.GET.get('city')
        property_type = self.request.GET.get('property_type')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        bedrooms = self.request.GET.get('bedrooms')
        
        if city:
            queryset = queryset.filter(city__icontains=city)
        if property_type:
            queryset = queryset.filter(property_type__name=property_type)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if bedrooms:
            queryset = queryset.filter(bedrooms__gte=bedrooms)
        
        return queryset.order_by('-created_at')

class PropertyDetailView(DetailView):
    model = Property
    template_name = 'properties/detail.html'
    context_object_name = 'property'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['similar_properties'] = Property.objects.filter(
            city=self.object.city,
            property_type=self.object.property_type,
            status='active'
        ).exclude(id=self.object.id)[:3]
        return context
```

### accounts/views.py
```python
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import CustomUser
from .forms import CustomUserCreationForm

class RegisterView(CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'register.html'
    success_url = reverse_lazy('index')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response

class ProfileView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = 'profile.html'
    context_object_name = 'user'
    
    def get_object(self):
        return self.request.user

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    template_name = 'profile_edit.html'
    fields = ['first_name', 'last_name', 'email', 'phone', 'bio', 'profile_picture']
    success_url = reverse_lazy('profile')
    
    def get_object(self):
        return self.request.user
```

## Step 5: Create URL Configuration

### realestate_pro/urls.py
```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('marketplace.urls')),
    path('accounts/', include('accounts.urls')),
    path('properties/', include('properties.urls')),
    path('messages/', include('messaging.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```

### marketplace/urls.py
```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='index'),
    path('properties/', views.PropertyListView.as_view(), name='properties_list'),
    path('property/<int:pk>/', views.PropertyDetailView.as_view(), name='property_detail'),
]
```

## Step 6: Create Django Templates

### templates/base.html
```html
{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}RealEstate Pro{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="{% static 'css/styles.css' %}">
    {% block extra_css %}{% endblock %}
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-light sticky-top" style="background-color: #ffffff; border-bottom: 1px solid #e8ecf1;">
        <div class="container-fluid px-4">
            <a class="navbar-brand fw-bold" href="{% url 'index' %}" style="color: #0066cc;">
                <i class="fas fa-home"></i> RealEstate Pro
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link" href="{% url 'index' %}">Home</a></li>
                    <li class="nav-item"><a class="nav-link" href="{% url 'properties_list' %}">Browse</a></li>
                    {% if user.is_authenticated %}
                        <li class="nav-item dropdown">
                            <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                                <i class="fas fa-user-circle"></i> {{ user.get_full_name }}
                            </a>
                            <ul class="dropdown-menu dropdown-menu-end">
                                <li><a class="dropdown-item" href="{% url 'profile' %}">Profile</a></li>
                                {% if user.role == 'buyer' %}
                                    <li><a class="dropdown-item" href="">My Dashboard</a></li>
                                {% elif user.role == 'seller' %}
                                    <li><a class="dropdown-item" href="">Seller Dashboard</a></li>
                                {% elif user.role == 'admin' %}
                                    <li><a class="dropdown-item" href="/admin/">Admin Panel</a></li>
                                {% endif %}
                                <li><hr class="dropdown-divider"></li>
                                <li><a class="dropdown-item" href="">Logout</a></li>
                            </ul>
                        </li>
                    {% else %}
                        <li class="nav-item"><a class="nav-link" href="{% url 'login' %}">Sign In</a></li>
                        <li class="nav-item"><a class="nav-link" href="{% url 'register' %}">Sign Up</a></li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <main>
        {% block content %}{% endblock %}
    </main>

    <!-- Footer -->
    <footer class="bg-dark text-white py-5 mt-5">
        <div class="container">
            <p class="text-center text-muted small mb-0">&copy; 2024 RealEstate Pro. All rights reserved.</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="{% static 'js/main.js' %}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

## Step 7: Run Migrations and Test

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Step 8: Admin Configuration

### accounts/admin.py
```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserAddress

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'role', 'verified', 'created_at')
    list_filter = ('role', 'verified')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone', 'bio', 'profile_picture', 'verified')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserAddress)
```

### properties/admin.py
```python
from django.contrib import admin
from .models import Property, PropertyType, PropertyImage, Favorite, Offer

class PropertyImageInline(admin.TabularInline):
    model = PropertyImage

class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'city', 'price', 'status', 'featured', 'created_at')
    list_filter = ('status', 'city', 'property_type', 'featured')
    search_fields = ('title', 'description', 'city')
    inlines = [PropertyImageInline]

admin.site.register(PropertyType)
admin.site.register(Property, PropertyAdmin)
admin.site.register(PropertyImage)
admin.site.register(Favorite)
admin.site.register(Offer)
```

## Conclusion

This guide provides a complete foundation for converting the RealEstate Pro static templates into a full-featured Django application. Customize the models, views, and templates according to your specific requirements.

For questions or issues, refer to the Django documentation: https://docs.djangoproject.com/
