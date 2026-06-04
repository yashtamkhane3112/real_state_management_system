from functools import wraps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .models import Profile

def is_admin_user(user):
    return bool(user.is_authenticated and (user.is_superuser or (getattr(user,'profile',None) and user.profile.role==Profile.Role.ADMIN)))

def role_required(*roles):
    def dec(view):
        @login_required
        @wraps(view)
        def wrapper(request,*args,**kwargs):
            if is_admin_user(request.user): return view(request,*args,**kwargs)
            profile=getattr(request.user,'profile',None)
            if profile and profile.role in roles: return view(request,*args,**kwargs)
            messages.error(request,'You do not have permission to access that page.'); return redirect('dashboard')
        return wrapper
    return dec
