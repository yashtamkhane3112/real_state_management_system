from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Count, Q, Sum
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .decorators import is_admin_user, role_required
from .forms import InquiryForm, ProfileForm, PropertyForm, TransactionForm, UserRegisterForm
from .models import Favorite, Inquiry, Profile, Property, Transaction
from .utils import make_simple_pdf, money


def _role(user):
    if not user.is_authenticated:
        return None
    if user.is_superuser:
        return Profile.Role.ADMIN
    return getattr(getattr(user, 'profile', None), 'role', None)


def _property_queryset_for_catalog(request):
    if is_admin_user(request.user):
        return Property.objects.select_related('seller').all()
    return Property.objects.select_related('seller').filter(status__in=[Property.Status.APPROVED, Property.Status.SOLD])


def _filtered_properties(request, queryset):
    city = request.GET.get('city', '').strip()
    property_type = request.GET.get('property_type', '').strip()
    status = request.GET.get('status', '').strip()
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    query = request.GET.get('q', '').strip()

    if query:
        queryset = queryset.filter(Q(title__icontains=query) | Q(city__icontains=query) | Q(address__icontains=query))
    if city:
        queryset = queryset.filter(city__icontains=city)
    if property_type:
        queryset = queryset.filter(property_type=property_type)
    if status:
        queryset = queryset.filter(status=status)
    if min_price:
        queryset = queryset.filter(price__gte=min_price)
    if max_price:
        queryset = queryset.filter(price__lte=max_price)
    return queryset


def _recommendations(base_property=None, user=None, limit=4):
    qs = Property.objects.filter(status=Property.Status.APPROVED)
    if base_property:
        low = base_property.price * Decimal('0.80')
        high = base_property.price * Decimal('1.20')
        qs = qs.exclude(pk=base_property.pk).filter(
            Q(city__iexact=base_property.city) | Q(property_type=base_property.property_type) | Q(price__range=(low, high))
        )
    elif user and hasattr(user, 'buyer_profile'):
        buyer_profile = user.buyer_profile
        if buyer_profile.preferred_city:
            qs = qs.filter(city__icontains=buyer_profile.preferred_city)
        if buyer_profile.min_budget:
            qs = qs.filter(price__gte=buyer_profile.min_budget)
        if buyer_profile.max_budget:
            qs = qs.filter(price__lte=buyer_profile.max_budget)
    return qs.distinct()[:limit]


def home(request):
    featured = Property.objects.filter(status=Property.Status.APPROVED)[:6]
    latest_sold = Property.objects.filter(status=Property.Status.SOLD)[:3]
    context = {
        'featured_properties': featured,
        'latest_sold': latest_sold,
        'cities': Property.objects.exclude(city='').values_list('city', flat=True).distinct()[:8],
    }
    return render(request, 'home.html', context)


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully.')
            return redirect('dashboard')
    else:
        form = UserRegisterForm()
    return render(request, 'auth/register.html', {'form': form})


@login_required
def dashboard_redirect(request):
    role = _role(request.user)
    if role == Profile.Role.SELLER:
        return redirect('seller_dashboard')
    if role == Profile.Role.ADMIN:
        return redirect('admin_dashboard')
    return redirect('buyer_dashboard')


@login_required
def profile_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile, user=request.user)
    return render(request, 'profile.html', {'form': form})


def property_list(request):
    qs = _filtered_properties(request, _property_queryset_for_catalog(request))
    favorites = set()
    if request.user.is_authenticated:
        favorites = set(Favorite.objects.filter(buyer=request.user).values_list('property_id', flat=True))
    context = {
        'properties': qs,
        'property_types': Property.PropertyType.choices,
        'status_choices': Property.Status.choices,
        'favorites': favorites,
        'filter_values': request.GET,
    }
    return render(request, 'properties/list.html', context)


def property_detail(request, pk):
    prop = get_object_or_404(Property.objects.select_related('seller'), pk=pk)
    if prop.status == Property.Status.PENDING and not (request.user == prop.seller or is_admin_user(request.user)):
        return HttpResponseForbidden('This property is awaiting approval.')
    inquiry_form = InquiryForm(user=request.user)
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(buyer=request.user, property=prop).exists()
    context = {
        'property': prop,
        'gallery': prop.gallery_images.all(),
        'inquiry_form': inquiry_form,
        'is_favorite': is_favorite,
        'recommendations': _recommendations(prop),
    }
    return render(request, 'properties/detail.html', context)


@login_required
def toggle_favorite(request, pk):
    prop = get_object_or_404(Property, pk=pk, status=Property.Status.APPROVED)
    favorite, created = Favorite.objects.get_or_create(buyer=request.user, property=prop)
    if not created:
        favorite.delete()
        messages.info(request, 'Property removed from favorites.')
    else:
        messages.success(request, 'Property saved to favorites.')
    return redirect(request.META.get('HTTP_REFERER') or 'property_detail', pk=prop.pk)


@role_required(Profile.Role.BUYER)
def create_inquiry(request, pk):
    prop = get_object_or_404(Property, pk=pk, status=Property.Status.APPROVED)
    if request.method != 'POST':
        return redirect('property_detail', pk=prop.pk)
    form = InquiryForm(request.POST, user=request.user)
    if form.is_valid():
        inquiry = form.save(commit=False)
        inquiry.property = prop
        inquiry.buyer = request.user
        inquiry.seller = prop.seller
        inquiry.save()
        send_mail(
            subject=f'New Property Inquiry: {prop.title}',
            message=f'{inquiry.buyer_name} sent an inquiry for {prop.title}.\nPhone: {inquiry.phone}\nMessage: {inquiry.message}',
            from_email=None,
            recipient_list=[prop.seller.email or 'seller@example.com'],
            fail_silently=True,
        )
        messages.success(request, 'Your inquiry has been sent successfully.')
    else:
        messages.error(request, 'Please correct the inquiry form.')
    return redirect('property_detail', pk=prop.pk)


@role_required(Profile.Role.BUYER)
def buyer_dashboard(request):
    inquiries = Inquiry.objects.filter(buyer=request.user).select_related('property')[:5]
    favorites = Favorite.objects.filter(buyer=request.user).select_related('property')[:4]
    context = {
        'inquiries': inquiries,
        'favorites': favorites,
        'recommendations': _recommendations(user=request.user),
        'stats': {
            'favorites': Favorite.objects.filter(buyer=request.user).count(),
            'inquiries': Inquiry.objects.filter(buyer=request.user).count(),
            'available': Property.objects.filter(status=Property.Status.APPROVED).count(),
        },
    }
    return render(request, 'dashboards/buyer.html', context)


@role_required(Profile.Role.BUYER)
def favorite_list(request):
    favorites = Favorite.objects.filter(buyer=request.user).select_related('property')
    return render(request, 'properties/favorites.html', {'favorites': favorites})


@role_required(Profile.Role.BUYER)
def buyer_inquiries(request):
    inquiries = Inquiry.objects.filter(buyer=request.user).select_related('property', 'seller')
    return render(request, 'inquiries/buyer_list.html', {'inquiries': inquiries})


@role_required(Profile.Role.SELLER)
def seller_dashboard(request):
    props = Property.objects.filter(seller=request.user)
    context = {
        'properties': props[:5],
        'inquiries': Inquiry.objects.filter(seller=request.user).select_related('property', 'buyer')[:6],
        'stats': {
            'total': props.count(),
            'approved': props.filter(status=Property.Status.APPROVED).count(),
            'pending': props.filter(status=Property.Status.PENDING).count(),
            'sold': props.filter(status=Property.Status.SOLD).count(),
        },
    }
    return render(request, 'dashboards/seller.html', context)


@role_required(Profile.Role.SELLER)
def seller_properties(request):
    props = Property.objects.filter(seller=request.user)
    return render(request, 'properties/seller_list.html', {'properties': props})


@role_required(Profile.Role.SELLER)
def add_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST)
        if form.is_valid():
            prop = form.save(commit=False)
            prop.seller = request.user
            prop.status = Property.Status.PENDING
            prop.save()
            form.save_gallery(prop)
            messages.success(request, 'Property submitted for admin approval.')
            return redirect('seller_properties')
    else:
        form = PropertyForm()
    return render(request, 'properties/form.html', {'form': form, 'title': 'Add New Property'})


@role_required(Profile.Role.SELLER)
def edit_property(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    if prop.seller != request.user and not is_admin_user(request.user):
        return HttpResponseForbidden('You can edit only your own property.')
    if request.method == 'POST':
        form = PropertyForm(request.POST, instance=prop)
        if form.is_valid():
            prop = form.save(commit=False)
            if not is_admin_user(request.user):
                prop.status = Property.Status.PENDING
                prop.rejection_reason = ''
            prop.save()
            form.save_gallery(prop)
            messages.success(request, 'Property updated successfully.')
            return redirect('seller_properties')
    else:
        form = PropertyForm(instance=prop)
    return render(request, 'properties/form.html', {'form': form, 'title': 'Edit Property'})


@role_required(Profile.Role.SELLER)
def delete_property(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    if prop.seller != request.user and not is_admin_user(request.user):
        return HttpResponseForbidden('You can delete only your own property.')
    if request.method == 'POST':
        prop.delete()
        messages.success(request, 'Property deleted successfully.')
        return redirect('seller_properties')
    return render(request, 'properties/delete_confirm.html', {'property': prop})


@role_required(Profile.Role.SELLER)
def seller_inquiries(request):
    inquiries = Inquiry.objects.filter(seller=request.user).select_related('property', 'buyer')
    return render(request, 'inquiries/seller_list.html', {'inquiries': inquiries})


@role_required(Profile.Role.SELLER)
def mark_inquiry_responded(request, pk):
    inquiry = get_object_or_404(Inquiry, pk=pk)
    if inquiry.seller != request.user and not is_admin_user(request.user):
        return HttpResponseForbidden('Invalid inquiry access.')
    inquiry.status = Inquiry.Status.RESPONDED
    inquiry.save(update_fields=['status'])
    messages.success(request, 'Inquiry marked as responded.')
    return redirect(request.META.get('HTTP_REFERER') or 'seller_inquiries')


def _admin_required(request):
    if not is_admin_user(request.user):
        messages.error(request, 'Super Admin access required.')
        return False
    return True


@login_required
def admin_dashboard(request):
    if not _admin_required(request):
        return redirect('dashboard')
    stats = {
        'total_properties': Property.objects.count(),
        'available': Property.objects.filter(status=Property.Status.APPROVED).count(),
        'sold': Property.objects.filter(status=Property.Status.SOLD).count(),
        'pending': Property.objects.filter(status=Property.Status.PENDING).count(),
        'buyers': User.objects.filter(profile__role=Profile.Role.BUYER).count(),
        'sellers': User.objects.filter(profile__role=Profile.Role.SELLER).count(),
        'inquiries': Inquiry.objects.count(),
        'transactions': Transaction.objects.count(),
    }
    context = {
        'stats': stats,
        'recent_properties': Property.objects.select_related('seller')[:6],
        'recent_inquiries': Inquiry.objects.select_related('property', 'buyer')[:6],
        'status_chart': Property.objects.values('status').annotate(total=Count('id')),
    }
    return render(request, 'dashboards/admin.html', context)


@login_required
def admin_properties(request):
    if not _admin_required(request):
        return redirect('dashboard')
    props = _filtered_properties(request, Property.objects.select_related('seller').all())
    return render(request, 'admin_panel/properties.html', {'properties': props, 'property_types': Property.PropertyType.choices, 'status_choices': Property.Status.choices})


@login_required
def approve_property(request, pk):
    if not _admin_required(request):
        return redirect('dashboard')
    prop = get_object_or_404(Property, pk=pk)
    prop.status = Property.Status.APPROVED
    prop.rejection_reason = ''
    prop.save(update_fields=['status', 'rejection_reason', 'updated_at'])
    messages.success(request, 'Property approved successfully.')
    return redirect(request.META.get('HTTP_REFERER') or 'admin_properties')


@login_required
def reject_property(request, pk):
    if not _admin_required(request):
        return redirect('dashboard')
    prop = get_object_or_404(Property, pk=pk)
    prop.status = Property.Status.REJECTED
    prop.rejection_reason = request.POST.get('rejection_reason', 'Listing information is incomplete.')
    prop.save(update_fields=['status', 'rejection_reason', 'updated_at'])
    messages.warning(request, 'Property rejected.')
    return redirect(request.META.get('HTTP_REFERER') or 'admin_properties')


@login_required
def admin_buyers(request):
    if not _admin_required(request):
        return redirect('dashboard')
    query = request.GET.get('q', '').strip()
    buyers = User.objects.filter(profile__role=Profile.Role.BUYER).select_related('profile').annotate(total_inquiries=Count('inquiries'))
    if query:
        buyers = buyers.filter(Q(username__icontains=query) | Q(first_name__icontains=query) | Q(email__icontains=query) | Q(profile__city__icontains=query))
    return render(request, 'admin_panel/buyers.html', {'buyers': buyers})


@login_required
def admin_sellers(request):
    if not _admin_required(request):
        return redirect('dashboard')
    query = request.GET.get('q', '').strip()
    sellers = User.objects.filter(profile__role=Profile.Role.SELLER).select_related('profile').annotate(total_properties=Count('properties'))
    if query:
        sellers = sellers.filter(Q(username__icontains=query) | Q(first_name__icontains=query) | Q(email__icontains=query) | Q(profile__city__icontains=query))
    return render(request, 'admin_panel/sellers.html', {'sellers': sellers})


@login_required
def admin_inquiries(request):
    if not _admin_required(request):
        return redirect('dashboard')
    inquiries = Inquiry.objects.select_related('property', 'buyer', 'seller')
    return render(request, 'admin_panel/inquiries.html', {'inquiries': inquiries})


@login_required
def transactions(request):
    if not _admin_required(request):
        return redirect('dashboard')
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save()
            messages.success(request, f'Transaction saved. Property status: {transaction.property.get_status_display()}.')
            return redirect('transactions')
    else:
        form = TransactionForm(initial={'transaction_date': timezone.localdate()})
    qs = Transaction.objects.select_related('property', 'buyer', 'seller')
    return render(request, 'transactions/list.html', {'form': form, 'transactions': qs})


@login_required
def reports(request):
    if not _admin_required(request):
        return redirect('dashboard')
    city = request.GET.get('city', '').strip()
    property_type = request.GET.get('property_type', '').strip()
    status = request.GET.get('status', '').strip()
    props = Property.objects.all()
    if city:
        props = props.filter(city__icontains=city)
    if property_type:
        props = props.filter(property_type=property_type)
    if status:
        props = props.filter(status=status)
    transactions_qs = Transaction.objects.select_related('property', 'buyer', 'seller')
    context = {
        'properties': props[:50],
        'transactions': transactions_qs[:20],
        'property_types': Property.PropertyType.choices,
        'status_choices': Property.Status.choices,
        'summary': {
            'available': props.filter(status=Property.Status.APPROVED).count(),
            'sold': props.filter(status=Property.Status.SOLD).count(),
            'pending': props.filter(status=Property.Status.PENDING).count(),
            'total_value': props.aggregate(total=Sum('price'))['total'] or 0,
            'transaction_value': transactions_qs.filter(status=Transaction.Status.COMPLETED).aggregate(total=Sum('final_price'))['total'] or 0,
        },
    }
    return render(request, 'reports/reports.html', context)


@login_required
def export_report_pdf(request):
    if not _admin_required(request):
        return redirect('dashboard')
    props = Property.objects.all()[:30]
    rows = [
        f'Generated on: {timezone.localtime().strftime("%d %b %Y, %I:%M %p")}',
        f'Total Properties: {Property.objects.count()}',
        f'Available Properties: {Property.objects.filter(status=Property.Status.APPROVED).count()}',
        f'Sold Properties: {Property.objects.filter(status=Property.Status.SOLD).count()}',
        '',
        'Property Preview:',
    ]
    for prop in props:
        rows.append(f'{prop.title} | {prop.city} | {prop.get_property_type_display()} | {money(prop.price)} | {prop.get_status_display()}')
    pdf = make_simple_pdf('EstateSphere Sales and Purchase Report', rows)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="estate_sales_purchase_report.pdf"'
    return response
