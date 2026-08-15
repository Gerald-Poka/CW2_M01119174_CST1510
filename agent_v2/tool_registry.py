# agent_v2/tool_registry.py

"""
Tool registry for the Cyber Intelligence Agent.

Defines which Python tools are available to the agent,
and provides descriptions that are sent to Gemini.

Read tools: execute immediately.
Write/action tools: agent proposes them as pending_action only.
                    A human admin must confirm before execution.
"""

from typing import Callable, Dict, Any
from agent_v2.tools import (
    incident_tools,
    ticket_tools,
    metadata_tools,
    analytics_tools,
    action_tools,
)


# ── Read-only tools (safe to execute immediately) ──────────────────────────
READ_TOOL_FUNCTIONS: Dict[str, Callable[..., Any]] = {
    "search_incidents": incident_tools.search_incidents,
    "get_incident": incident_tools.get_incident,
    "get_incident_statistics": incident_tools.get_incident_statistics,
    "search_tickets": ticket_tools.search_tickets,
    "get_ticket": ticket_tools.get_ticket,
    "get_ticket_statistics": ticket_tools.get_ticket_statistics,
    "search_datasets": metadata_tools.search_datasets,
    "get_dataset": metadata_tools.get_dataset,
    "get_dashboard_summary": analytics_tools.get_dashboard_summary,
    "get_incident_category_statistics": analytics_tools.get_incident_category_statistics,
    "get_ticket_workload": analytics_tools.get_ticket_workload,
}

# ── Write/action tools (NEVER executed directly by the agent) ──────────────
# These are registered so Gemini knows they exist and can PROPOSE them.
# The Streamlit UI + admin confirmation gate executes them.
WRITE_TOOL_FUNCTIONS: Dict[str, Callable[..., Any]] = {
    "close_incident": action_tools.close_incident,
    "update_incident": action_tools.update_incident,
    "create_incident": action_tools.create_incident,
    "close_ticket": action_tools.close_ticket,
    "assign_ticket": action_tools.assign_ticket,
    "update_ticket": action_tools.update_ticket,
    "create_ticket": action_tools.create_ticket,
}

# Combined registry used by agent for tool lookup
TOOL_FUNCTIONS: Dict[str, Callable[..., Any]] = {
    **READ_TOOL_FUNCTIONS,
    **WRITE_TOOL_FUNCTIONS,
}


def get_tool_descriptions() -> Dict[str, Dict[str, Any]]:
    """
    Return structured descriptions of all available tools for the LLM.

    Read tools: agent calls these directly.
    Write tools: agent proposes these as pending_action for admin confirmation.
    """
    return {
        # ── READ TOOLS ──────────────────────────────────────────────────────
        "search_incidents": {
            "type": "read",
            "description": "Search cyber incidents with optional filters.",
            "parameters": {
                "severity": "Optional string: Low, Medium, High, Critical.",
                "status": "Optional string: Open, Resolved, Closed.",
                "category": "Optional string e.g. Malware, Phishing.",
            },
            "returns": "List of incident dictionaries.",
        },
        "get_incident": {
            "type": "read",
            "description": "Retrieve a single incident by its incident_id.",
            "parameters": {
                "incident_id": "Required integer.",
            },
            "returns": "Incident dictionary or null if not found.",
        },
        "get_incident_statistics": {
            "type": "read",
            "description": "Return high-level statistics about all incidents.",
            "parameters": {},
            "returns": "Dictionary with counts by status and severity.",
        },
        "search_tickets": {
            "type": "read",
            "description": "Search IT tickets with optional filters.",
            "parameters": {
                "priority": "Optional string: High, Medium, Low.",
                "status": "Optional string: Open, Resolved, Closed.",
                "assigned_to": "Optional string e.g. IT_Support_A.",
            },
            "returns": "List of ticket dictionaries.",
        },
        "get_ticket": {
            "type": "read",
            "description": "Retrieve a single IT ticket by ticket_id.",
            "parameters": {
                "ticket_id": "Required integer.",
            },
            "returns": "Ticket dictionary or null if not found.",
        },
        "get_ticket_statistics": {
            "type": "read",
            "description": "Return high-level statistics about IT tickets.",
            "parameters": {},
            "returns": "Dictionary with counts by status, priority and avg resolution time.",
        },
        "search_datasets": {
            "type": "read",
            "description": "Search dataset metadata.",
            "parameters": {
                "uploaded_by": "Optional string e.g. data_scientist.",
            },
            "returns": "List of dataset metadata dictionaries.",
        },
        "get_dataset": {
            "type": "read",
            "description": "Retrieve a single dataset metadata record.",
            "parameters": {
                "dataset_id": "Required integer.",
            },
            "returns": "Dataset metadata dictionary or null.",
        },
        "get_dashboard_summary": {
            "type": "read",
            "description": "Return a compact summary of incidents, tickets, and datasets.",
            "parameters": {},
            "returns": "Dictionary with key summary metrics.",
        },
        "get_incident_category_statistics": {
            "type": "read",
            "description": "Return incident counts grouped by category.",
            "parameters": {},
            "returns": "Dictionary mapping category name to count.",
        },
        "get_ticket_workload": {
            "type": "read",
            "description": "Return IT support workload statistics by assignee.",
            "parameters": {},
            "returns": "Dictionary with tickets_by_assignee and open_tickets_by_assignee.",
        },

        # ── WRITE TOOLS ─────────────────────────────────────────────────────
        # These are PROPOSALS only. The agent must use action "propose_action"
        # for these. They will NOT be executed until an admin confirms.
        "close_incident": {
            "type": "write",
            "description": "Propose closing an incident (sets status to Closed). Requires admin confirmation.",
            "parameters": {
                "incident_id": "Required integer. The ID of the incident to close.",
            },
            "returns": "Pending action stored for admin confirmation.",
        },
        "update_incident": {
            "type": "write",
            "description": "Propose updating fields on an incident. Requires admin confirmation.",
            "parameters": {
                "incident_id": "Required integer.",
                "updates": "Required dict of field -> new value e.g. {'status': 'Resolved'}.",
            },
            "returns": "Pending action stored for admin confirmation.",
        },
        "create_incident": {
            "type": "write",
            "description": "Propose creating a new incident. Requires admin confirmation.",
            "parameters": {
                "timestamp": "Optional ISO datetime string.",
                "severity": "Required string: Low, Medium, High, Critical.",
                "category": "Required string.",
                "status": "Required string: Open, Resolved, Closed.",
                "description": "Required string.",
            },
            "returns": "Pending action stored for admin confirmation.",
        },
        "close_ticket": {
            "type": "write",
            "description": "Propose closing an IT ticket (sets status to Closed). Requires admin confirmation.",
            "parameters": {
                "ticket_id": "Required integer.",
            },
            "returns": "Pending action stored for admin confirmation.",
        },
        "assign_ticket": {
            "type": "write",
            "description": "Propose assigning an IT ticket to a support engineer. Requires admin confirmation.",
            "parameters": {
                "ticket_id": "Required integer.",
                "assignee": "Required string e.g. IT_Support_A.",
            },
            "returns": "Pending action stored for admin confirmation.",
        },
        "update_ticket": {
            "type": "write",
            "description": "Propose updating fields on an IT ticket. Requires admin confirmation.",
            "parameters": {
                "ticket_id": "Required integer.",
                "updates": "Required dict of field -> new value.",
            },
            "returns": "Pending action stored for admin confirmation.",
        },
        "create_ticket": {
            "type": "write",
            "description": "Propose creating a new IT ticket. Requires admin confirmation.",
            "parameters": {
                "priority": "Required string: High, Medium, Low.",
                "description": "Required string.",
                "status": "Required string: Open, Resolved, Closed.",
                "assigned_to": "Required string.",
                "created_at": "Optional ISO datetime string.",
                "resolution_time": "Optional float (hours).",
            },
            "returns": "Pending action stored for admin confirmation.",
        },
    }
