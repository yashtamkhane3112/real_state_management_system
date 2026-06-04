"""Role-based access control decorators."""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            user_role = request.user.role
            if request.user.is_superuser:
                user_role = 'admin'
            if user_role not in roles:
                messages.error(request, "You don't have permission to access that page.")
                return redirect('dashboard:redirect')
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator


buyer_required = role_required('buyer')
seller_required = role_required('seller')
admin_required = role_required('admin')
