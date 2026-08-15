"""AI Assistant context assembly."""


def build_context(request):
    return {
        "active": "ai_assistant",
        "messages": request.session.get("chat_messages", []),
        "error": None,
    }
