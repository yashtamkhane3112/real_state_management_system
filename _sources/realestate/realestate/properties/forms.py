from django import forms
from .models import Property, Inquiry


class PropertyForm(forms.ModelForm):
    # Gallery uploads are handled via a plain <input type="file" multiple> in
    # the template; values are read with request.FILES.getlist('extra_images').

    class Meta:
        model = Property
        fields = (
            'title', 'description', 'price', 'address', 'city', 'state',
            'property_type', 'listing_type', 'bedrooms', 'bathrooms', 'area',
            'amenities', 'cover_image',
        )
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'property_type': forms.Select(attrs={'class': 'form-select'}),
            'listing_type': forms.Select(attrs={'class': 'form-select'}),
            'bedrooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'bathrooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'area': forms.NumberInput(attrs={'class': 'form-control'}),
            'amenities': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Parking, Gym, Pool, Garden, ...',
            }),
            'cover_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ('name', 'email', 'phone', 'message')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4,
                                              'placeholder': 'I am interested in this property...'}),
        }


class InquiryReplyForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ('reply', 'status')
        widgets = {
            'reply': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class PropertySearchForm(forms.Form):
    q = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Search by title, city or address...'
    }))
    city = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    property_type = forms.ChoiceField(
        required=False,
        choices=[('', 'Any Type')] + Property.PROPERTY_TYPES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    listing_type = forms.ChoiceField(
        required=False,
        choices=[('', 'Buy or Rent')] + Property.LISTING_TYPE,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    min_price = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={
        'class': 'form-control', 'placeholder': 'Min Price'}))
    max_price = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={
        'class': 'form-control', 'placeholder': 'Max Price'}))
    bedrooms = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={
        'class': 'form-control', 'placeholder': 'Min Bedrooms'}))
