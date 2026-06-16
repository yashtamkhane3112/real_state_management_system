"""
Views for user authentication and profile management.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser
from .forms import LoginForm, RegistrationForm, UserProfileForm
from properties.models import Property, Favorite, Inquiry


def index(request):
    """Landing page view."""
    featured_properties = Property.objects.filter(is_featured=True)[:6]
    total_properties = Property.objects.count()
    total_users = CustomUser.objects.count()
    
    context = {
        'featured_properties': featured_properties,
        'total_properties': total_properties,
        'total_users': total_users,
    }
    return render(request, 'landing.html', context)


def login_view(request):
    """User login view."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            
            try:
                user = CustomUser.objects.get(email=email)
                user = authenticate(request, username=user.username, password=password)
                
                if user is not None:
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.first_name}!")
                    return redirect('dashboard')
                else:
                    messages.error(request, "Invalid email or password.")
            except CustomUser.DoesNotExist:
                messages.error(request, "User not found.")
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})


def register_view(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Registration successful! Please log in.")
            return redirect('login')
    else:
        form = RegistrationForm()
    
    return render(request, 'register.html', {'form': form})


def logout_view(request):
    """User logout view."""
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('index')


@login_required
def dashboard(request):
    """Role-based dashboard view."""
    user = request.user
    
    if user.is_buyer():
        return buyer_dashboard(request)
    elif user.is_seller():
        return seller_dashboard(request)
    elif user.is_super_admin():
        return admin_dashboard(request)
    else:
        return redirect('index')


@login_required
def buyer_dashboard(request):
    """Buyer dashboard view."""
    user = request.user
    saved_properties = Favorite.objects.filter(user=user).select_related('property')
    inquiries = Inquiry.objects.filter(buyer=user).order_by('-created_at')
    recent_properties = Property.objects.all().order_by('-created_at')[:6]
    
    context = {
        'saved_properties': saved_properties,
        'inquiries': inquiries,
        'recent_properties': recent_properties,
        'dashboard_type': 'buyer',
    }
    return render(request, 'dashboard_buyer.html', context)


@login_required
def seller_dashboard(request):
    """Seller dashboard view."""
    user = request.user
    properties = Property.objects.filter(owner=user)
    inquiries = Inquiry.objects.filter(property__owner=user).order_by('-created_at')
    total_inquiries = inquiries.count()
    
    context = {
        'properties': properties,
        'inquiries': inquiries,
        'total_inquiries': total_inquiries,
        'dashboard_type': 'seller',
    }
    return render(request, 'dashboard_seller.html', context)


@login_required
def admin_dashboard(request):
    """Admin dashboard view."""
    if not request.user.is_super_admin():
        return redirect('index')
    
    users = CustomUser.objects.all()
    properties = Property.objects.all()
    inquiries = Inquiry.objects.all()
    
    context = {
        'total_users': users.count(),
        'total_properties': properties.count(),
        'total_inquiries': inquiries.count(),
        'recent_users': users.order_by('-created_at')[:10],
        'recent_properties': properties.order_by('-created_at')[:10],
        'recent_inquiries': inquiries.order_by('-created_at')[:10],
        'dashboard_type': 'admin',
    }
    return render(request, 'dashboard_admin.html', context)


@login_required
def profile_view(request):
    """User profile view."""
    user = request.user
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user)
    
    context = {
        'form': form,
        'user': user,
    }
    return render(request, 'profile.html', context)


@login_required
def public_profile_view(request, user_id):
    """View public profile of another user."""
    user = get_object_or_404(CustomUser, id=user_id)
    
    if user.is_seller():
        properties = Property.objects.filter(owner=user)
    else:
        properties = None
    
    context = {
        'profile_user': user,
        'properties': properties,
    }
    return render(request, 'public_profile.html', context)
