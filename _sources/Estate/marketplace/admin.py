from django.contrib import admin
from .models import BuyerProfile, Favorite, Inquiry, Profile, Property, PropertyImage, SellerProfile, Transaction

class PropertyImageInline(admin.TabularInline):
    model=PropertyImage; extra=1
@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display=('title','city','property_type','price','status','seller','created_at')
    list_filter=('status','property_type','city')
    search_fields=('title','city','address','seller__username')
    inlines=[PropertyImageInline]
admin.site.register(Profile); admin.site.register(BuyerProfile); admin.site.register(SellerProfile); admin.site.register(Favorite); admin.site.register(Inquiry); admin.site.register(Transaction)
