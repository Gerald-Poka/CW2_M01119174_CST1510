"""Authentication feature: login, registration and logout.

Standalone pages (no sidebar layout) rendered from ``templates/auth/``.
"""

from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache

from cyber import services


@never_cache
def login(request):
    if request.session.get("username"):
        return redirect("cyber:dashboard")

    error = None
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        success, message, user = services.login_user(username, password, request)
        if success:
            request.session["username"] = user.username
            request.session["role"] = user.role_name
            request.session["user_id"] = user.id
            return redirect("cyber:dashboard")
        error = message

    return render(request, "auth/login.html", {"error": error})


@never_cache
def register(request):
    if request.session.get("username"):
        return redirect("cyber:dashboard")

    error = None
    success = None
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        confirm = request.POST.get("confirm_password", "")
        if password != confirm:
            error = "Passwords do not match."
        else:
            ok, message = services.register_user(username, password)
            if ok:
                success = message
            else:
                error = message

    return render(request, "auth/register.html",
                  {"error": error, "success": success})


@never_cache
def logout(request):
    user_id = request.session.get("user_id")
    if user_id:
        services.record_logout(user_id, request)
    request.session.flush()
    response = redirect("cyber:login")
    response["Cache-Control"] = "no-cache, no-store, must-revalidate, private"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    return response
