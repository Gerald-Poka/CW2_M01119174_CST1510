"""Admin Management controller: user administration and data entry.

Admin-only page. Handles promote/demote/reset/delete of users plus adding
cyber incidents, dataset metadata and IT tickets.
"""

from django.shortcuts import render

from cyber import services
from cyber.decorators import admin_required
from cyber.features.admin_management import js_view


ADMIN_USERNAME = "poka"


@admin_required
def index(request):
    message = None
    message_type = None
    actor = services.get_user(request.session.get("username"))
    users = services.get_all_users()

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "promote":
            username = request.POST.get("username")
            if username and services.promote_user(username, actor=actor):
                message, message_type = f"{username} promoted to Administrator.", "success"
        elif action == "demote":
            username = request.POST.get("username")
            if username and username != ADMIN_USERNAME and services.demote_user(username, actor=actor):
                message, message_type = f"{username} demoted to Normal Staff.", "success"
        elif action == "reset_password":
            username = request.POST.get("username")
            if username and username != ADMIN_USERNAME and services.admin_change_password(username):
                message, message_type = f"Password reset for {username}.", "success"
        elif action == "delete_user":
            username = request.POST.get("username")
            if username and username != ADMIN_USERNAME:
                services.delete_user(username)
                message, message_type = f"{username} deleted.", "success"
        elif action == "add_incident":
            timestamp = request.POST.get("timestamp")
            severity = request.POST.get("severity")
            category = request.POST.get("category")
            status = request.POST.get("status")
            description = request.POST.get("description")
            formatted = f"{timestamp} 00:00:00" if timestamp else None
            if formatted:
                services.add_cyber_incident(formatted, severity, category,
                                            status, description)
                message, message_type = "Cyber incident added.", "success"
        elif action == "add_dataset":
            try:
                name = request.POST.get("name")
                rows = int(request.POST.get("rows") or 0)
                columns = int(request.POST.get("columns") or 0)
                uploaded_by = request.POST.get("uploaded_by")
                upload_date = request.POST.get("upload_date")
                did = services.add_metadata(name, rows, columns,
                                            uploaded_by, upload_date)
                message, message_type = f"Dataset added. ID: {did}", "success"
            except (ValueError, TypeError):
                message, message_type = "Invalid dataset details.", "error"
        elif action == "add_ticket":
            priority = request.POST.get("priority")
            description = request.POST.get("description")
            status = request.POST.get("status")
            assigned_to = request.POST.get("assigned_to")
            created_at = request.POST.get("created_at")
            resolution_time = request.POST.get("resolution_time") or None
            if description and assigned_to:
                tid = services.add_it_ticket(
                    priority, description, status, assigned_to,
                    created_at, resolution_time)
                message, message_type = f"IT Ticket added. ID: {tid}", "success"
            else:
                message, message_type = "Please fill in all required fields.", "error"

        users = services.get_all_users()

    admin_count = sum(1 for u in users if u.role_name == "Administrator")
    user_count = sum(1 for u in users if u.role_name == "Normal Staff")

    return render(request, "admin_management/view.html", {
        "users": users,
        "total_users": len(users),
        "admin_count": admin_count,
        "user_count": user_count,
        "active": "admin_management",
        "message": message,
        "message_type": message_type,
        "js_view": js_view.build_js({}),
    })
