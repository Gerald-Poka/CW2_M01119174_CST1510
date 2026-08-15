"""Profile controller: change password for the current user."""

from django.shortcuts import render

from cyber import services
from cyber.decorators import login_required_custom
from cyber.features.profile import js_view


@login_required_custom
def index(request):
    error = None
    success = None

    if request.method == "POST":
        current_password = request.POST.get("current_password", "")
        new_password = request.POST.get("new_password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not current_password or not new_password or not confirm_password:
            error = "Please complete all fields."
        elif new_password != confirm_password:
            error = "New passwords do not match."
        else:
            ok, message = services.change_password(
                request.session.get("user_id"), current_password, new_password
            )
            if ok:
                success = message
            else:
                error = message

    return render(request, "profile/view.html", {
        "username": request.session.get("username"),
        "role": request.session.get("role"),
        "active": "profile",
        "error": error,
        "success": success,
        "js_view": js_view.build_js({}),
    })
