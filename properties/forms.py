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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == "amenities":
                continue
            if isinstance(field.widget, (forms.Select, forms.NullBooleanSelect)):
                field.widget.attrs.update({"class": "form-select"})
            elif isinstance(field.widget, (forms.CheckboxInput, forms.CheckboxSelectMultiple)):
                field.widget.attrs.update({"class": "form-check-input"})
            else:
                field.widget.attrs.update({"class": "form-control"})

    def clean_cover_image(self):
        cover_image = self.cleaned_data.get("cover_image")
        if cover_image:
            if cover_image.size > 10 * 1024 * 1024:
                raise forms.ValidationError("Cover image size must not exceed 10MB.")
        return cover_image

    def clean(self):
        cleaned_data = super().clean()
        if self.files:
            if hasattr(self.files, "getlist"):
                gallery_images = self.files.getlist("gallery_images")
            else:
                gallery_images = self.files.get("gallery_images")
                gallery_images = [gallery_images] if gallery_images else []
            for img in gallery_images:
                if img.size > 10 * 1024 * 1024:
                    raise forms.ValidationError("Each gallery image must not exceed 10MB.")
        return cleaned_data


class PropertyImageForm(forms.ModelForm):
    class Meta:
        model = PropertyImage
        fields = ("image", "caption")


