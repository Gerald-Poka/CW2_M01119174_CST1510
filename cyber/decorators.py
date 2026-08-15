"""Shared view decorators for session-based authentication.

The platform authenticates users against the legacy ``users`` table (bcrypt
hashes) rather than Django's ``auth_user`` model, so these decorators replace
Django's ``login_required`` / ``user_passes_test``.
"""

from django.shortcuts import redirect


def login_required_custom(view_func):
    """Redirect to the login page when no session user is present."""
    def wrapper(request, *args, **kwargs):
        if not request.session.get("username"):
            return redirect("cyber:login")
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    """Require an authenticated admin session; otherwise redirect."""
    def wrapper(request, *args, **kwargs):
        if not request.session.get("username"):
            return redirect("cyber:login")
        if request.session.get("role") != "admin":
            return redirect("cyber:dashboard")
        return view_func(request, *args, **kwargs)
    return wrapper
