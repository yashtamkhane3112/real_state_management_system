"""
Inquiry models for property inquiries and messaging.
"""
from django.db import models
from django.conf import settings
from properties.models import Property


class Inquiry(models.Model):
    """Property inquiry model."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('responded', 'Responded'),
        ('closed', 'Closed'),
    ]
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='inquiries')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='inquiries_made')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Inquiry'
        verbose_name_plural = 'Inquiries'
        ordering = ['-created_at']
        unique_together = ('property', 'buyer')
    
    def __str__(self):
        return f"Inquiry from {self.buyer.username} for {self.property.title}"


class Message(models.Model):
    """Direct message between users."""
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username}"
    
    def mark_as_read(self):
        self.is_read = True
        self.save()


class Transaction(models.Model):
    """Transaction records for properties."""
    
    TRANSACTION_TYPE_CHOICES = [
        ('purchase', 'Purchase'),
        ('rental', 'Rental'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True, related_name='transactions')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='purchases')
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sales')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES, default='purchase')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.transaction_type.title()} - {self.property.title if self.property else 'Deleted'}"
