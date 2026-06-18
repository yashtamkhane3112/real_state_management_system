from functools import wraps

from django.contrib.auth.decorators import login_required


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.is_superuser or request.user.role in roles:
                return view_func(request, *args, **kwargs)
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied

        return wrapper

    return decorator


def dashboard_role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.contrib.auth.views import redirect_to_login
                from django.conf import settings
                return redirect_to_login(request.get_full_path(), login_url=settings.LOGIN_URL)

            if request.user.is_superuser or request.user.role in roles:
                return view_func(request, *args, **kwargs)

            from django.shortcuts import redirect
            from accounts.models import User
            if request.user.is_admin_role:
                return redirect("accounts:admin_dashboard")
            elif request.user.role == User.Role.SELLER:
                return redirect("accounts:seller_dashboard")
            else:
                return redirect("accounts:buyer_dashboard")

        return wrapper

    return decorator


