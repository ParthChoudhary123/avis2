from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

def manager_required(view_func):
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_manager():
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped_view

def vendor_required(view_func):
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_vendor():
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped_view
