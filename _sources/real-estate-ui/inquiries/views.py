"""
Views for inquiries and messaging.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from properties.models import Property
from .models import Inquiry, Message
from .forms import InquiryForm, MessageForm


@login_required
def submit_inquiry(request, slug):
    """Submit an inquiry for a property."""
    property = get_object_or_404(Property, slug=slug)
    
    # Check if user already has an inquiry
    existing_inquiry = Inquiry.objects.filter(property=property, buyer=request.user).first()
    
    if request.method == 'POST':
        form = InquiryForm(request.POST, instance=existing_inquiry)
        if form.is_valid():
            inquiry = form.save(commit=False)
            inquiry.property = property
            inquiry.buyer = request.user
            inquiry.save()
            messages.success(request, "Your inquiry has been submitted successfully!")
            return redirect('property_detail', slug=slug)
    else:
        form = InquiryForm(instance=existing_inquiry)
    
    context = {
        'form': form,
        'property': property,
    }
    return render(request, 'inquiry_form.html', context)


@login_required
def my_inquiries(request):
    """View user's inquiries (for buyers)."""
    inquiries = Inquiry.objects.filter(buyer=request.user).select_related('property').order_by('-created_at')
    
    context = {
        'inquiries': inquiries,
        'total_inquiries': inquiries.count(),
    }
    return render(request, 'my_inquiries.html', context)


@login_required
def property_inquiries(request):
    """View inquiries for seller's properties."""
    if not request.user.is_seller():
        messages.error(request, "Only sellers can view this page.")
        return redirect('index')
    
    inquiries = Inquiry.objects.filter(
        property__owner=request.user
    ).select_related('property', 'buyer').order_by('-created_at')
    
    # Filter by property if specified
    property_filter = request.GET.get('property')
    if property_filter:
        inquiries = inquiries.filter(property_id=property_filter)
    
    properties = Property.objects.filter(owner=request.user)
    
    context = {
        'inquiries': inquiries,
        'properties': properties,
        'total_inquiries': inquiries.count(),
    }
    return render(request, 'property_inquiries.html', context)


@login_required
def update_inquiry_status(request, inquiry_id):
    """Update the status of an inquiry."""
    inquiry = get_object_or_404(Inquiry, id=inquiry_id)
    
    if inquiry.property.owner != request.user and not request.user.is_super_admin():
        messages.error(request, "You don't have permission to update this inquiry.")
        return redirect('property_inquiries')
    
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in dict(Inquiry.STATUS_CHOICES):
            inquiry.status = status
            inquiry.save()
            messages.success(request, "Inquiry status updated successfully!")
        else:
            messages.error(request, "Invalid status.")
    
    return redirect('property_inquiries')


@login_required
def messages_list(request):
    """View user's messages."""
    # Get conversations with unread count
    received = Message.objects.filter(receiver=request.user).order_by('-created_at')
    sent = Message.objects.filter(sender=request.user).order_by('-created_at')
    
    # Get unique conversations
    users = set()
    for msg in received:
        users.add(msg.sender)
    for msg in sent:
        users.add(msg.receiver)
    
    context = {
        'received_messages': received[:20],
        'sent_messages': sent[:20],
        'unread_count': received.filter(is_read=False).count(),
        'users': list(users)[:10],
    }
    return render(request, 'messages.html', context)


@login_required
def conversation(request, user_id):
    """View conversation with a specific user."""
    other_user = get_object_or_404(
        __import__('django.contrib.auth', fromlist=['get_user_model']).get_user_model(),
        id=user_id
    )
    
    # Get all messages between the two users
    messages_list = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).order_by('created_at')
    
    # Mark all messages from other user as read
    Message.objects.filter(sender=other_user, receiver=request.user, is_read=False).update(is_read=True)
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = other_user
            message.save()
            messages.success(request, "Message sent successfully!")
            return redirect('conversation', user_id=user_id)
    else:
        form = MessageForm()
    
    context = {
        'other_user': other_user,
        'messages': messages_list,
        'form': form,
    }
    return render(request, 'conversation.html', context)


@login_required
def send_message(request, user_id):
    """Send a direct message to a user."""
    other_user = get_object_or_404(
        __import__('django.contrib.auth', fromlist=['get_user_model']).get_user_model(),
        id=user_id
    )
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = other_user
            message.save()
            messages.success(request, "Message sent successfully!")
            return redirect('conversation', user_id=user_id)
    else:
        form = MessageForm()
    
    context = {
        'form': form,
        'other_user': other_user,
    }
    return render(request, 'send_message.html', context)
