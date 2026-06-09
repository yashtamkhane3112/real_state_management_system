import os
import uuid
from django.conf import settings
from django.db import models
from django.utils.text import get_valid_filename, slugify

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
        return self.filter(status=Property.Status.ACTIVE, approval_status=Property.ApprovalStatus.APPROVED)

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


class Property(models.Model):
    class PropertyType(models.TextChoices):
        APARTMENT = "apartment", "Apartment"
        HOUSE = "house", "House"
        VILLA = "villa", "Villa"
        PLOT = "plot", "Plot"
        COMMERCIAL = "commercial", "Commercial"
        OFFICE = "office", "Office"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        SOLD = "sold", "Sold"
        RENTED = "rented", "Rented"

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
    bedrooms = models.PositiveSmallIntegerField(default=0, db_index=True)
    bathrooms = models.PositiveSmallIntegerField(default=0, db_index=True)
    area_sqft = models.PositiveIntegerField(db_index=True)
    furnishing = models.CharField(max_length=80, blank=True, db_index=True)
    year_built = models.PositiveSmallIntegerField(null=True, blank=True)
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

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(f"{self.title}-{self.city}-{self.locality}")[:230]
            slug = base
            counter = 2
            while Property.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=upload_property_gallery)
    caption = models.CharField(max_length=160, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
