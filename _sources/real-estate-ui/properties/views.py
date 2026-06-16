"""
Views for property management.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from .models import Property, Favorite
from .forms import PropertyForm, PropertySearchForm


def property_list(request):
    """Display list of properties with filters."""
    properties = Property.objects.filter(status='available').select_related('owner')
    
    form = PropertySearchForm(request.GET)
    
    # Search by query
    query = request.GET.get('query', '')
    if query:
        properties = properties.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(city__icontains=query) |
            Q(address__icontains=query)
        )
    
    # Filter by property type
    property_types = request.GET.getlist('property_type')
    if property_types:
        properties = properties.filter(property_type__in=property_types)
    
    # Filter by price
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        properties = properties.filter(price__gte=min_price)
    if max_price:
        properties = properties.filter(price__lte=max_price)
    
    # Filter by bedrooms
    bedrooms = request.GET.get('bedrooms')
    if bedrooms:
        properties = properties.filter(bedrooms__gte=bedrooms)
    
    # Filter by bathrooms
    bathrooms = request.GET.get('bathrooms')
    if bathrooms:
        properties = properties.filter(bathrooms__gte=bathrooms)
    
    # Filter by city
    city = request.GET.get('city')
    if city:
        properties = properties.filter(city__icontains=city)
    
    context = {
        'properties': properties,
        'form': form,
        'total_count': properties.count(),
    }
    return render(request, 'properties_list.html', context)


def property_detail(request, slug):
    """Display detailed view of a property."""
    property = get_object_or_404(Property, slug=slug)
    property.increment_views()
    
    images = property.images.all()
    is_favorite = False
    
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, property=property).exists()
    
    context = {
        'property': property,
        'images': images,
        'is_favorite': is_favorite,
    }
    return render(request, 'property_detail.html', context)


@login_required
def create_property(request):
    """Create a new property listing."""
    if not (request.user.is_seller() or request.user.is_super_admin()):
        messages.error(request, "Only sellers can create property listings.")
        return redirect('index')
    
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property = form.save(commit=False)
            property.owner = request.user
            property.save()
            messages.success(request, "Property created successfully!")
            return redirect('property_detail', slug=property.slug)
    else:
        form = PropertyForm()
    
    context = {'form': form}
    return render(request, 'list_property.html', context)


@login_required
def edit_property(request, slug):
    """Edit a property listing."""
    property = get_object_or_404(Property, slug=slug)
    
    if property.owner != request.user and not request.user.is_super_admin():
        messages.error(request, "You don't have permission to edit this property.")
        return redirect('property_detail', slug=slug)
    
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property)
        if form.is_valid():
            form.save()
            messages.success(request, "Property updated successfully!")
            return redirect('property_detail', slug=property.slug)
    else:
        form = PropertyForm(instance=property)
    
    context = {'form': form, 'property': property, 'is_edit': True}
    return render(request, 'list_property.html', context)


@login_required
def delete_property(request, slug):
    """Delete a property listing."""
    property = get_object_or_404(Property, slug=slug)
    
    if property.owner != request.user and not request.user.is_super_admin():
        messages.error(request, "You don't have permission to delete this property.")
        return redirect('property_detail', slug=slug)
    
    if request.method == 'POST':
        property.delete()
        messages.success(request, "Property deleted successfully!")
        return redirect('seller_dashboard' if request.user.is_seller() else 'admin_dashboard')
    
    context = {'property': property}
    return render(request, 'confirm_delete.html', context)


@login_required
@require_http_methods(["POST"])
def toggle_favorite(request, slug):
    """Toggle property as favorite."""
    property = get_object_or_404(Property, slug=slug)
    favorite, created = Favorite.objects.get_or_create(user=request.user, property=property)
    
    if not created:
        favorite.delete()
        messages.success(request, "Property removed from favorites.")
    else:
        messages.success(request, "Property added to favorites.")
    
    return redirect('property_detail', slug=slug)


@login_required
def my_properties(request):
    """View seller's properties."""
    if not request.user.is_seller():
        messages.error(request, "Only sellers can view this page.")
        return redirect('index')
    
    properties = Property.objects.filter(owner=request.user)
    
    context = {
        'properties': properties,
        'total_properties': properties.count(),
    }
    return render(request, 'my_properties.html', context)


@login_required
def favorites(request):
    """View user's favorite properties."""
    favorites = Favorite.objects.filter(user=request.user).select_related('property')
    
    context = {
        'favorites': favorites,
        'total_favorites': favorites.count(),
    }
    return render(request, 'favorites.html', context)
