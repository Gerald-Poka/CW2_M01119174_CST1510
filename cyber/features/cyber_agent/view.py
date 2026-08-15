"""Cyber Agent context assembly."""


def build_context(request):
    return {
        "active": "cyber_agent",
        "agent_text": request.session.get("agent_text"),
        "report_available": bool(request.session.get("latest_report_path")),
        "error": None,
    }
