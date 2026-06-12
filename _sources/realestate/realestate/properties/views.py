from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from accounts.decorators import seller_required
from .models import Property, PropertyImage, Inquiry, Favorite
from .forms import PropertyForm, InquiryForm, PropertySearchForm, InquiryReplyForm


def landing(request):
    featured = Property.objects.filter(status='active', is_featured=True)[:6]
    if not featured.exists():
        featured = Property.objects.filter(status='active')[:6]
    stats = {
        'properties': Property.objects.filter(status='active').count(),
        'cities': Property.objects.filter(status='active').values('city').distinct().count(),
        'sellers': Property.objects.values('seller').distinct().count(),
        'happy_clients': Inquiry.objects.values('buyer').distinct().count() + 120,
    }
    return render(request, 'properties/landing.html', {
        'featured': featured,
        'stats': stats,
        'search_form': PropertySearchForm(),
    })


def property_list(request):
    form = PropertySearchForm(request.GET or None)
    qs = Property.objects.filter(status='active')

    if form.is_valid():
        cd = form.cleaned_data
        if cd.get('q'):
            qs = qs.filter(Q(title__icontains=cd['q']) | Q(city__icontains=cd['q']) | Q(address__icontains=cd['q']))
        if cd.get('city'):
            qs = qs.filter(city__icontains=cd['city'])
        if cd.get('property_type'):
            qs = qs.filter(property_type=cd['property_type'])
        if cd.get('listing_type'):
            qs = qs.filter(listing_type=cd['listing_type'])
        if cd.get('min_price') is not None:
            qs = qs.filter(price__gte=cd['min_price'])
        if cd.get('max_price') is not None:
            qs = qs.filter(price__lte=cd['max_price'])
        if cd.get('bedrooms'):
            qs = qs.filter(bedrooms__gte=cd['bedrooms'])

    paginator = Paginator(qs, 9)
    page_obj = paginator.get_page(request.GET.get('page'))

    favorite_ids = set()
    if request.user.is_authenticated:
        favorite_ids = set(Favorite.objects.filter(user=request.user).values_list('property_id', flat=True))

    return render(request, 'properties/list.html', {
        'page_obj': page_obj,
        'form': form,
        'favorite_ids': favorite_ids,
    })


def property_detail(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    if prop.status != 'active' and not (
        request.user.is_authenticated and (request.user == prop.seller or request.user.is_admin_user())
    ):
        messages.warning(request, "This property is not available yet.")
        return redirect('properties:list')

    Property.objects.filter(pk=pk).update(views_count=prop.views_count + 1)
    similar = Property.objects.filter(
        status='active', city=prop.city
    ).exclude(pk=prop.pk)[:3]

    inquiry_form = InquiryForm(initial={
        'name': request.user.get_full_name() or request.user.username if request.user.is_authenticated else '',
        'email': request.user.email if request.user.is_authenticated else '',
    })
    is_favorited = (
        request.user.is_authenticated
        and Favorite.objects.filter(user=request.user, property=prop).exists()
    )

    return render(request, 'properties/detail.html', {
        'prop': prop,
        'similar': similar,
        'inquiry_form': inquiry_form,
        'is_favorited': is_favorited,
    })


@login_required
def send_inquiry(request, pk):
    prop = get_object_or_404(Property, pk=pk, status='active')
    if request.method == 'POST':
        form = InquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save(commit=False)
            inquiry.property = prop
            inquiry.buyer = request.user
            inquiry.save()
            messages.success(request, "Your inquiry has been sent to the seller.")
            return redirect('properties:detail', pk=pk)
    return redirect('properties:detail', pk=pk)


@login_required
@require_POST
def toggle_favorite(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    fav, created = Favorite.objects.get_or_create(user=request.user, property=prop)
    if not created:
        fav.delete()
        favorited = False
    else:
        favorited = True
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'favorited': favorited})
    return redirect(request.META.get('HTTP_REFERER', 'properties:list'))


# ---------- Seller ----------
@seller_required
def add_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            prop = form.save(commit=False)
            prop.seller = request.user
            prop.save()
            for image in request.FILES.getlist('extra_images'):
                PropertyImage.objects.create(property=prop, image=image)
            messages.success(request, "Property submitted! It will be visible after admin approval.")
            return redirect('dashboard:seller')
    else:
        form = PropertyForm()
    return render(request, 'properties/add_edit.html', {'form': form, 'mode': 'Add'})


@seller_required
def edit_property(request, pk):
    prop = get_object_or_404(Property, pk=pk, seller=request.user)
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=prop)
        if form.is_valid():
            prop = form.save()
            for image in request.FILES.getlist('extra_images'):
                PropertyImage.objects.create(property=prop, image=image)
            messages.success(request, "Property updated successfully.")
            return redirect('properties:my_properties')
    else:
        form = PropertyForm(instance=prop)
    return render(request, 'properties/add_edit.html', {'form': form, 'mode': 'Edit', 'prop': prop})


@seller_required
def delete_property(request, pk):
    prop = get_object_or_404(Property, pk=pk, seller=request.user)
    if request.method == 'POST':
        prop.delete()
        messages.success(request, "Property deleted.")
        return redirect('properties:my_properties')
    return render(request, 'properties/confirm_delete.html', {'prop': prop})


@seller_required
def my_properties(request):
    props = Property.objects.filter(seller=request.user)
    return render(request, 'properties/my_properties.html', {'props': props})


@seller_required
def mark_sold(request, pk):
    prop = get_object_or_404(Property, pk=pk, seller=request.user)
    prop.status = 'sold'
    prop.save()
    messages.success(request, f"{prop.title} marked as sold.")
    return redirect('properties:my_properties')


@seller_required
def inquiry_management(request):
    inquiries = Inquiry.objects.filter(property__seller=request.user)
    return render(request, 'properties/inquiries.html', {'inquiries': inquiries})


@seller_required
def reply_inquiry(request, pk):
    inquiry = get_object_or_404(Inquiry, pk=pk, property__seller=request.user)
    if request.method == 'POST':
        form = InquiryReplyForm(request.POST, instance=inquiry)
        if form.is_valid():
            obj = form.save(commit=False)
            if obj.reply and obj.status == 'new':
                obj.status = 'replied'
            obj.save()
            messages.success(request, "Reply sent.")
            return redirect('properties:inquiries')
    else:
        form = InquiryReplyForm(instance=inquiry)
    return render(request, 'properties/reply_inquiry.html', {'form': form, 'inquiry': inquiry})


# ---------- Buyer ----------
@login_required
def my_favorites(request):
    favs = Favorite.objects.filter(user=request.user).select_related('property')
    return render(request, 'properties/favorites.html', {'favorites': favs})


@login_required
def my_inquiries(request):
    inquiries = Inquiry.objects.filter(buyer=request.user)
    return render(request, 'properties/my_inquiries.html', {'inquiries': inquiries})
