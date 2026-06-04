from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone
from .models import BuyerProfile, Inquiry, Profile, Property, PropertyImage, SellerProfile, Transaction

BOOT='form-control form-control-lg rounded-4'; SELECT='form-select form-select-lg rounded-4'
def style_form_fields(form):
    for f in form.fields.values():
        if isinstance(f.widget, forms.Select): f.widget.attrs.setdefault('class', SELECT)
        elif isinstance(f.widget, forms.Textarea):
            f.widget.attrs.setdefault('class','form-control rounded-4'); f.widget.attrs.setdefault('rows',4)
        else: f.widget.attrs.setdefault('class', BOOT)
    return form

class UserRegisterForm(UserCreationForm):
    ROLE_CHOICES=((Profile.Role.BUYER,'Buyer'),(Profile.Role.SELLER,'Seller'))
    first_name=forms.CharField(max_length=80,label='Full name')
    email=forms.EmailField(); phone=forms.CharField(max_length=20,required=False); city=forms.CharField(max_length=80,required=False)
    role=forms.ChoiceField(choices=ROLE_CHOICES)
    class Meta:
        model=User; fields=('first_name','username','email','phone','city','role','password1','password2')
    def __init__(self,*args,**kwargs): super().__init__(*args,**kwargs); style_form_fields(self)
    def save(self,commit=True):
        user=super().save(commit=False); user.email=self.cleaned_data['email']
        parts=self.cleaned_data['first_name'].strip().split(' ',1); user.first_name=parts[0]; user.last_name=parts[1] if len(parts)>1 else ''
        if commit:
            user.save(); profile=user.profile; profile.role=self.cleaned_data['role']; profile.phone=self.cleaned_data.get('phone',''); profile.city=self.cleaned_data.get('city',''); profile.save()
            if profile.role==Profile.Role.BUYER: BuyerProfile.objects.get_or_create(user=user)
            if profile.role==Profile.Role.SELLER: SellerProfile.objects.get_or_create(user=user)
        return user

class PropertyForm(forms.ModelForm):
    gallery_image_1_url=forms.URLField(required=False,label='Gallery image 1 URL')
    gallery_image_2_url=forms.URLField(required=False,label='Gallery image 2 URL')
    gallery_image_3_url=forms.URLField(required=False,label='Gallery image 3 URL')
    class Meta:
        model=Property; fields=['title','property_type','description','price','address','city','area_sqft','bedrooms','bathrooms','cover_image_url']
        widgets={'description':forms.Textarea(attrs={'rows':5}),'address':forms.Textarea(attrs={'rows':3})}
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs); style_form_fields(self); self.fields['cover_image_url'].help_text='Paste property image URL or keep blank.'
        if self.instance and self.instance.pk:
            for i,img in enumerate(self.instance.gallery_images.all()[:3],1): self.fields[f'gallery_image_{i}_url'].initial=img.image_url
    def save_gallery(self,prop):
        urls=[self.cleaned_data.get(f'gallery_image_{i}_url') for i in range(1,4)]
        prop.gallery_images.all().delete()
        for i,u in enumerate(urls,1):
            if u: PropertyImage.objects.create(property=prop,image_url=u,caption=f'Gallery view {i}')

class InquiryForm(forms.ModelForm):
    class Meta: model=Inquiry; fields=('buyer_name','email','phone','message')
    def __init__(self,*args,user=None,**kwargs):
        super().__init__(*args,**kwargs); style_form_fields(self)
        if user and user.is_authenticated:
            self.fields['buyer_name'].initial=user.get_full_name() or user.username; self.fields['email'].initial=user.email; self.fields['phone'].initial=getattr(user.profile,'phone','')

class TransactionForm(forms.ModelForm):
    class Meta:
        model=Transaction; fields=('property','buyer','seller','final_price','transaction_date','status','notes'); widgets={'transaction_date':forms.DateInput(attrs={'type':'date'})}
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs); style_form_fields(self)
        self.fields['property'].queryset=Property.objects.exclude(status=Property.Status.REJECTED)
        self.fields['buyer'].queryset=User.objects.filter(profile__role=Profile.Role.BUYER)
        self.fields['seller'].queryset=User.objects.filter(profile__role=Profile.Role.SELLER)
        self.fields['transaction_date'].initial=timezone.localdate()

class ProfileForm(forms.ModelForm):
    first_name=forms.CharField(max_length=80,label='First name'); last_name=forms.CharField(max_length=80,required=False,label='Last name'); email=forms.EmailField()
    class Meta: model=Profile; fields=('phone','address','city','avatar_url')
    def __init__(self,*args,user=None,**kwargs):
        self.user=user; super().__init__(*args,**kwargs)
        if user: self.fields['first_name'].initial=user.first_name; self.fields['last_name'].initial=user.last_name; self.fields['email'].initial=user.email
        style_form_fields(self)
    def save(self,commit=True):
        profile=super().save(commit=False)
        if self.user: self.user.first_name=self.cleaned_data['first_name']; self.user.last_name=self.cleaned_data.get('last_name',''); self.user.email=self.cleaned_data['email']; self.user.save()
        if commit: profile.save()
        return profile
