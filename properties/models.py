import os
import uuid
import datetime
from django.conf import settings
from django.db import models
from django.utils.text import get_valid_filename, slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

def validate_year_built(value):
    if value is not None:
        current_year = datetime.datetime.now().year
        if value < 1900 or value > current_year:
            raise ValidationError(f"Year Built must be between 1900 and {current_year}.")

def get_short_sanitized_filename(filename, max_length=50):
    name, ext = os.path.splitext(filename)
    name = get_valid_filename(name).replace(' ', '_')
    allowed_length = max_length - len(ext)
    if allowed_length <= 0:
        return f"{uuid.uuid4().hex[:8]}{ext}"
    if len(name) > allowed_length:
        name = name[:allowed_length]
    return f"{name}{ext}"

def upload_property_cover(instance, filename):
    return os.path.join("properties/covers/", get_short_sanitized_filename(filename))

def upload_property_gallery(instance, filename):
    return os.path.join("properties/gallery/", get_short_sanitized_filename(filename))



class PropertyQuerySet(models.QuerySet):
    def public(self):
        return self.filter(status__in=[Property.Status.ACTIVE, Property.Status.SOLD], approval_status=Property.ApprovalStatus.APPROVED)

    def search(self, params):
        qs = self
        q = params.get("q")
        if q:
            qs = qs.filter(
                models.Q(title__icontains=q)
                | models.Q(description__icontains=q)
                | models.Q(city__icontains=q)
                | models.Q(locality__icontains=q)
                | models.Q(address__icontains=q)
            )
        for field in ("city", "locality", "property_type"):
            if params.get(field):
                qs = qs.filter(**{f"{field}__iexact": params[field]})
        for param, lookup in {
            "min_price": "price__gte",
            "max_price": "price__lte",
            "min_area": "area_sqft__gte",
            "max_area": "area_sqft__lte",
            "bedrooms": "bedrooms__gte",
            "bathrooms": "bathrooms__gte",
        }.items():
            if params.get(param):
                qs = qs.filter(**{lookup: params[param]})
        amenity_ids = params.getlist("amenities") if hasattr(params, "getlist") else []
        if amenity_ids:
            qs = qs.filter(amenities__id__in=amenity_ids).distinct()
        sort = params.get("sort")
        if sort in {"price", "-price", "popular", "date"}:
            return qs.order_by({"price": "price", "-price": "-price", "popular": "-view_count", "date": "-created_at"}[sort])
        return qs.order_by("-is_featured", "-created_at")


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(unique=True, db_index=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Amenity(models.Model):
    name = models.CharField(max_length=120, unique=True)
    icon = models.CharField(max_length=80, blank=True)

    def __str__(self):
        return self.name


def get_property_display_image(property_obj):
    if property_obj.cover_image:
        try:
            if property_obj.cover_image.storage.exists(property_obj.cover_image.name):
                # Detect and skip tiny transparent dummy placeholders (e.g. cover.gif, placeholder.png)
                file_size = property_obj.cover_image.storage.size(property_obj.cover_image.name)
                is_dummy = "cover.gif" in property_obj.cover_image.name.lower() or "placeholder" in property_obj.cover_image.name.lower()
                if file_size > 1000 and not is_dummy:
                    return property_obj.cover_image.url
        except Exception:
            pass
    
    # Stable pseudo-random fallback assignment from downloaded videoplayback (1) frames
    if property_obj.id:
        img_idx = (property_obj.id % 20) + 1
    else:
        img_idx = 1
    from django.templatetags.static import static
    return static(f"images/properties/fallbacks/{img_idx:04d}.jpg")


class Property(models.Model):
    class PropertyType(models.TextChoices):
        APARTMENT = "apartment", "Apartment"
        HOUSE = "house", "House"
        VILLA = "villa", "Villa"
        PLOT = "plot", "Plot"
        COMMERCIAL = "commercial", "Commercial"
        OFFICE = "office", "Office"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        ACTIVE = "active", "Active"
        SOLD = "sold", "Sold"
        CLOSED = "closed", "Closed"

    class ApprovalStatus(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    title = models.CharField(max_length=220, db_index=True)
    slug = models.SlugField(max_length=260, unique=True, db_index=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=14, decimal_places=2, db_index=True)
    property_type = models.CharField(max_length=30, choices=PropertyType.choices, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="properties")
    bedrooms = models.PositiveSmallIntegerField(default=1, db_index=True, validators=[MinValueValidator(1), MaxValueValidator(20)])
    bathrooms = models.PositiveSmallIntegerField(default=1, db_index=True, validators=[MinValueValidator(1), MaxValueValidator(20)])
    area_sqft = models.PositiveIntegerField(db_index=True, validators=[MinValueValidator(100)])
    furnishing = models.CharField(max_length=80, blank=True, db_index=True)
    year_built = models.PositiveSmallIntegerField(null=True, blank=True, validators=[validate_year_built])
    parking = models.PositiveSmallIntegerField(default=0)
    amenities = models.ManyToManyField(Amenity, blank=True, related_name="properties")
    cover_image = models.ImageField(upload_to=upload_property_cover, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, db_index=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, db_index=True)
    address = models.TextField()
    city = models.CharField(max_length=120, db_index=True)
    locality = models.CharField(max_length=140, db_index=True)
    pincode = models.CharField(max_length=12, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE, db_index=True)
    approval_status = models.CharField(max_length=20, choices=ApprovalStatus.choices, default=ApprovalStatus.PENDING, db_index=True)
    rejection_reason = models.TextField(blank=True)
    sold_date = models.DateTimeField(null=True, blank=True, db_index=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    view_count = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="properties")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PropertyQuerySet.as_manager()

    class Meta:
        ordering = ["-is_featured", "-created_at"]
        indexes = [
            models.Index(fields=["city", "locality"]),
            models.Index(fields=["approval_status", "status"]),
            models.Index(fields=["price", "area_sqft"]),
            models.Index(fields=["latitude", "longitude"]),
        ]

    def clean(self):
        super().clean()
        validate_year_built(self.year_built)
        if self.bedrooms is not None and (self.bedrooms < 1 or self.bedrooms > 20):
            raise ValidationError({"bedrooms": "Bedrooms must be between 1 and 20."})
        if self.bathrooms is not None and (self.bathrooms < 1 or self.bathrooms > 20):
            raise ValidationError({"bathrooms": "Bathrooms must be between 1 and 20."})
        if self.area_sqft is not None and self.area_sqft < 100:
            raise ValidationError({"area_sqft": "Area must be at least 100 sqft."})

    def save(self, *args, **kwargs):
        self.clean()
        # Resolve mismatches for programmatic creation (on insert only)
        if not self.pk:
            if self.approval_status in [Property.ApprovalStatus.PENDING, Property.ApprovalStatus.DRAFT, Property.ApprovalStatus.REJECTED]:
                if self.status in [Property.Status.APPROVED, Property.Status.ACTIVE, Property.Status.SOLD, Property.Status.CLOSED]:
                    if self.approval_status == Property.ApprovalStatus.PENDING:
                        self.status = Property.Status.PENDING
                    elif self.approval_status == Property.ApprovalStatus.DRAFT:
                        self.status = Property.Status.DRAFT
                    elif self.approval_status == Property.ApprovalStatus.REJECTED:
                        self.status = Property.Status.DRAFT

        # Auto-align status and approval_status
        if self.approval_status == Property.ApprovalStatus.REJECTED:
            # If rejected, set status to Draft
            self.status = Property.Status.DRAFT
        else:
            if self.status == Property.Status.DRAFT:
                self.approval_status = Property.ApprovalStatus.DRAFT
            elif self.status == Property.Status.PENDING:
                self.approval_status = Property.ApprovalStatus.PENDING
            elif self.status in [Property.Status.APPROVED, Property.Status.ACTIVE, Property.Status.SOLD, Property.Status.CLOSED]:
                self.approval_status = Property.ApprovalStatus.APPROVED

        # Handle sold_date auto-setting
        if self.status == Property.Status.SOLD:
            if not self.sold_date:
                from django.utils import timezone
                self.sold_date = timezone.now()
        else:
            self.sold_date = None

        if not self.slug:
            base = slugify(f"{self.title}-{self.city}-{self.locality}")[:230]
            slug = base
            counter = 2
            while Property.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug

        # Ensure status and approval_status are saved when update_fields is passed
        if "update_fields" in kwargs and kwargs["update_fields"] is not None:
            uf = list(kwargs["update_fields"])
            if "status" not in uf:
                uf.append("status")
            if "approval_status" not in uf:
                uf.append("approval_status")
            kwargs["update_fields"] = uf

        super().save(*args, **kwargs)

    @property
    def display_image_url(self):
        return get_property_display_image(self)

    @property
    def display_gallery_1(self):
        img_idx = ((self.id + 1) % 8) + 1 if self.id else 2
        from django.templatetags.static import static
        return static(f"images/properties/house-0{img_idx}.jpg")

    @property
    def display_gallery_2(self):
        img_idx = ((self.id + 2) % 8) + 1 if self.id else 3
        from django.templatetags.static import static
        return static(f"images/properties/house-0{img_idx}.jpg")

    @property
    def formatted_price(self):
        val = float(self.price)
        if val >= 10000000:
            num = val / 10000000
            if num.is_integer():
                return f"₹{int(num)} Cr"
            else:
                return f"₹{num:.2f} Cr"
        elif val >= 100000:
            num = val / 100000
            if num.is_integer():
                return f"₹{int(num)} Lakh"
            else:
                return f"₹{num:.1f} Lakh"
        return f"₹{int(val):,}"

    def __str__(self):
        return self.title


class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=upload_property_gallery)
    caption = models.CharField(max_length=160, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
