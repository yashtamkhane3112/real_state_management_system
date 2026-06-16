from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count

from accounts.decorators import buyer_required, seller_required, admin_required
from accounts.models import User
from properties.models import Property, Inquiry, Favorite


@login_required
def redirect_dashboard(request):
    user = request.user
    if user.is_superuser or user.role == 'admin':
        return redirect('dashboard:admin')
    if user.role == 'seller':
        return redirect('dashboard:seller')
    return redirect('dashboard:buyer')


@buyer_required
def buyer_dashboard(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('property')[:6]
    inquiries = Inquiry.objects.filter(buyer=request.user).select_related('property')[:5]
    context = {
        'favorites_count': Favorite.objects.filter(user=request.user).count(),
        'inquiries_count': Inquiry.objects.filter(buyer=request.user).count(),
        'favorites': favorites,
        'inquiries': inquiries,
    }
    return render(request, 'dashboard/buyer.html', context)


@seller_required
def seller_dashboard(request):
    qs = Property.objects.filter(seller=request.user)
    context = {
        'total': qs.count(),
        'active': qs.filter(status='active').count(),
        'pending': qs.filter(status='pending').count(),
        'sold': qs.filter(status='sold').count(),
        'inquiries_count': Inquiry.objects.filter(property__seller=request.user).count(),
        'recent_props': qs[:5],
        'recent_inquiries': Inquiry.objects.filter(property__seller=request.user).select_related('property')[:5],
    }
    return render(request, 'dashboard/seller.html', context)


@admin_required
def admin_dashboard(request):
    context = {
        'total_users': User.objects.count(),
        'total_buyers': User.objects.filter(role='buyer').count(),
        'total_sellers': User.objects.filter(role='sellers' if False else 'seller').count(),
        'total_properties': Property.objects.count(),
        'active_properties': Property.objects.filter(status='active').count(),
        'pending_properties': Property.objects.filter(status='pending').count(),
        'sold_properties': Property.objects.filter(status='sold').count(),
        'total_inquiries': Inquiry.objects.count(),
        'recent_users': User.objects.order_by('-date_joined')[:5],
        'recent_properties': Property.objects.order_by('-created_at')[:5],
        'top_cities': Property.objects.values('city').annotate(c=Count('id')).order_by('-c')[:5],
    }
    return render(request, 'dashboard/admin.html', context)


@admin_required
def admin_approvals(request):
    pending = Property.objects.filter(status='pending').select_related('seller')
    return render(request, 'dashboard/approvals.html', {'pending': pending})


@admin_required
def approve_property(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    prop.status = 'active'
    prop.save()
    messages.success(request, f"{prop.title} approved.")
    return redirect('dashboard:approvals')


@admin_required
def reject_property(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    prop.status = 'rejected'
    prop.save()
    messages.info(request, f"{prop.title} rejected.")
    return redirect('dashboard:approvals')


@admin_required
def manage_users(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'dashboard/users.html', {'users': users})


@admin_required
def toggle_user_active(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.is_active = not user.is_active
    user.save()
    messages.success(request, f"{user.username} is now {'active' if user.is_active else 'disabled'}.")
    return redirect('dashboard:users')


@admin_required
def manage_properties(request):
    props = Property.objects.all().select_related('seller')
    return render(request, 'dashboard/properties.html', {'props': props})
