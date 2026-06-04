"""
Forms for inquiries and messaging.
"""
from django import forms
from .models import Inquiry, Message


class InquiryForm(forms.ModelForm):
    """Form for submitting property inquiries."""
    class Meta:
        model = Inquiry
        fields = ['subject', 'message', 'phone', 'email']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subject'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Your message',
                'rows': 6
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address'
            }),
        }


class MessageForm(forms.ModelForm):
    """Form for sending messages."""
    class Meta:
        model = Message
        fields = ['subject', 'message']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subject'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Your message',
                'rows': 6
            }),
        }
