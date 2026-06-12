"""
Forms for property management.
"""
from django import forms
from .models import Property, PropertyImage


class PropertyForm(forms.ModelForm):
    """Form for creating and editing properties."""
    amenities = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Swimming Pool, Gym, Garden, etc.',
            'rows': 3
        })
    )
    
    class Meta:
        model = Property
        fields = [
            'title', 'description', 'property_type', 'status',
            'address', 'city', 'state', 'pincode',
            'price', 'bedrooms', 'bathrooms', 'area', 'thumbnail',
            'amenities', 'parking', 'balcony', 'garden', 'gym', 'swimming_pool', 'security'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Property Title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Detailed description of the property',
                'rows': 6
            }),
            'property_type': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full Address'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State/Province'
            }),
            'pincode': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ZIP Code'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Price',
                'step': '0.01'
            }),
            'bedrooms': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
            'bathrooms': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
            'area': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Area (sq ft)',
                'step': '0.01'
            }),
            'thumbnail': forms.FileInput(attrs={'class': 'form-control'}),
            'parking': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'balcony': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'garden': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'gym': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'swimming_pool': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'security': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PropertyImageForm(forms.ModelForm):
    """Form for uploading property images."""
    class Meta:
        model = PropertyImage
        fields = ['image', 'alt_text', 'is_primary']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'alt_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Image description'
            }),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PropertySearchForm(forms.Form):
    """Form for searching and filtering properties."""
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by title or location'
        })
    )
    property_type = forms.MultipleChoiceField(
        required=False,
        choices=Property.PROPERTY_TYPE_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    status = forms.MultipleChoiceField(
        required=False,
        choices=Property.STATUS_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    min_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Minimum Price',
            'step': '0.01'
        })
    )
    max_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Maximum Price',
            'step': '0.01'
        })
    )
    bedrooms = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Minimum Bedrooms'
        })
    )
    bathrooms = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Minimum Bathrooms'
        })
    )
    city = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City'
        })
    )
