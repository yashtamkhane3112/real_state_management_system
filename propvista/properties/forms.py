from django import forms

from .models import Property, PropertyImage


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = (
            "title",
            "description",
            "price",
            "property_type",
            "category",
            "bedrooms",
            "bathrooms",
            "area_sqft",
            "furnishing",
            "year_built",
            "parking",
            "amenities",
            "cover_image",
            "latitude",
            "longitude",
            "address",
            "city",
            "locality",
            "pincode",
            "status",
            "is_featured",
        )
        widgets = {"amenities": forms.CheckboxSelectMultiple, "description": forms.Textarea(attrs={"rows": 5}), "address": forms.Textarea(attrs={"rows": 3})}


class PropertyImageForm(forms.ModelForm):
    class Meta:
        model = PropertyImage
        fields = ("image", "caption")

