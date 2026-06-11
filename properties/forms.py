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
        error_messages = {
            "bedrooms": {
                "min_value": "Bedrooms cannot be negative.",
            },
            "bathrooms": {
                "min_value": "Bathrooms cannot be negative.",
            },
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if "status" in self.fields:
            if user and not user.is_admin_role:
                # Sellers/regular users can only choose Draft or Pending when creating/editing
                current_status = self.instance.status if (self.instance and self.instance.pk) else None
                allowed_choices = [
                    (Property.Status.DRAFT, "Draft"),
                    (Property.Status.PENDING, "Pending"),
                ]
                if current_status and current_status not in [Property.Status.DRAFT, Property.Status.PENDING]:
                    allowed_choices.append((current_status, self.instance.get_status_display()))
                self.fields["status"].choices = allowed_choices

        for name, field in self.fields.items():
            if name == "amenities":
                continue
            if isinstance(field.widget, (forms.Select, forms.NullBooleanSelect)):
                field.widget.attrs.update({"class": "form-select"})
            elif isinstance(field.widget, (forms.CheckboxInput, forms.CheckboxSelectMultiple)):
                field.widget.attrs.update({"class": "form-check-input"})
            else:
                field.widget.attrs.update({"class": "form-control"})
        
        # HTML5 frontend validation constraints
        if "price" in self.fields:
            self.fields["price"].widget.attrs.update({"min": "0.01", "required": "required", "type": "number", "step": "any"})
        if "bedrooms" in self.fields:
            self.fields["bedrooms"].widget.attrs.update({"min": "0", "required": "required", "type": "number"})
        if "bathrooms" in self.fields:
            self.fields["bathrooms"].widget.attrs.update({"min": "0", "required": "required", "type": "number"})
        if "area_sqft" in self.fields:
            self.fields["area_sqft"].widget.attrs.update({"min": "1", "required": "required", "type": "number"})

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price is not None and price <= 0:
            raise forms.ValidationError("Price must be greater than 0.")
        return price

    def clean_year_built(self):
        import datetime
        year_built = self.cleaned_data.get("year_built")
        current_year = datetime.datetime.now().year
        if year_built is not None:
            if year_built < 1900 or year_built > current_year:
                raise forms.ValidationError(f"Year Built must be between 1900 and {current_year}.")
        return year_built

    def clean_bedrooms(self):
        bedrooms = self.cleaned_data.get("bedrooms")
        if bedrooms is not None:
            if bedrooms < 1 or bedrooms > 20:
                raise forms.ValidationError("Bedrooms must be between 1 and 20.")
        return bedrooms

    def clean_bathrooms(self):
        bathrooms = self.cleaned_data.get("bathrooms")
        if bathrooms is not None:
            if bathrooms < 1 or bathrooms > 20:
                raise forms.ValidationError("Bathrooms must be between 1 and 20.")
        return bathrooms

    def clean_area_sqft(self):
        area_sqft = self.cleaned_data.get("area_sqft")
        if area_sqft is not None:
            if area_sqft < 100:
                raise forms.ValidationError("Area must be at least 100 sqft.")
        return area_sqft


class PropertyImageForm(forms.ModelForm):
    class Meta:
        model = PropertyImage
        fields = ("image", "caption")


