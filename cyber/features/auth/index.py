"""Authentication feature: login, registration and logout.

Standalone pages (no sidebar layout) rendered from ``templates/auth/``.
"""

from django.shortcuts import redirect, render

from cyber import services


def login(request):
    if request.session.get("username"):
        return redirect("cyber:dashboard")

    error = None
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        success, message, user = services.login_user(username, password)
        if success:
            request.session["username"] = user.username
            request.session["role"] = user.role
            request.session["user_id"] = user.id
            return redirect("cyber:dashboard")
        error = message

    return render(request, "auth/login.html", {"error": error})


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


def logout(request):
    request.session.flush()
    return redirect("cyber:login")
