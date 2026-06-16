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

