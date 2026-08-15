"""Profile context assembly."""


def build_context(request):
    return {
        "active": "profile",
        "username": request.session.get("username"),
        "role": request.session.get("role"),
        "error": None,
        "success": None,
    }
