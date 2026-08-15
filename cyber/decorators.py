"""Shared view decorators for session-based authentication.

The platform authenticates users against the ``user`` table (bcrypt hashes)
rather than Django's ``auth_user`` model, so these decorators replace
Django's ``login_required`` / ``user_passes_test``.
"""

from functools import wraps
from django.shortcuts import redirect
from django.views.decorators.cache import never_cache


def login_required_custom(view_func):
    """Redirect to the login page when no session user is present, and prevent browser caching."""
    @never_cache
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get("username"):
            return redirect("cyber:login")
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    """Require an authenticated Administrator session; otherwise redirect, and prevent caching."""
    @never_cache
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get("username"):
            return redirect("cyber:login")
        if request.session.get("role") != "Administrator":
            return redirect("cyber:dashboard")
        return view_func(request, *args, **kwargs)
    return wrapper
