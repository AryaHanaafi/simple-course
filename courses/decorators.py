from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def role_required(allowed_roles=[]):
    """
    Decorator to check if user has one of the allowed roles.
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.shortcuts import redirect
                from django.conf import settings
                return redirect(settings.LOGIN_URL)
            if request.user.role in allowed_roles or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return _wrapped_view
    return decorator

def superadmin_only(view_func):
    return role_required(['superadmin'])(view_func)

def instructor_only(view_func):
    return role_required(['instructor'])(view_func)

def student_only(view_func):
    return role_required(['student'])(view_func)

def instructor_or_superadmin(view_func):
    return role_required(['instructor', 'superadmin'])(view_func)
