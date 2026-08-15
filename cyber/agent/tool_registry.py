from cyber.agent import tools as tool_mod

READ_TOOL_FUNCTIONS = {
    "search_incidents": tool_mod.search_incidents,
    "get_incident": tool_mod.get_incident,
    "get_incident_statistics": tool_mod.get_incident_statistics,
    "search_tickets": tool_mod.search_tickets,
    "get_ticket": tool_mod.get_ticket,
    "get_ticket_statistics": tool_mod.get_ticket_statistics,
    "search_datasets": tool_mod.search_datasets,
    "get_dataset": tool_mod.get_dataset,
    "get_dashboard_summary": tool_mod.get_dashboard_summary,
    "get_incident_category_statistics": tool_mod.get_incident_category_statistics,
    "get_ticket_workload": tool_mod.get_ticket_workload,
}

WRITE_TOOL_FUNCTIONS = {
    "close_incident": tool_mod.close_incident,
    "update_incident": tool_mod.update_incident,
    "create_incident": tool_mod.create_incident,
    "close_ticket": tool_mod.close_ticket,
    "assign_ticket": tool_mod.assign_ticket,
    "update_ticket": tool_mod.update_ticket,
    "create_ticket": tool_mod.create_ticket,
}

TOOL_FUNCTIONS = {**READ_TOOL_FUNCTIONS, **WRITE_TOOL_FUNCTIONS}


def get_tool_descriptions():
    return {
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
            "parameters": {"incident_id": "Required integer."},
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
            "parameters": {"ticket_id": "Required integer."},
            "returns": "Ticket dictionary or null if not found.",
        },
        "get_ticket_statistics": {
            "type": "read",
            "description": "Return high-level statistics about IT tickets.",
            "parameters": {},
            "returns": ("Dictionary with counts by status, priority and "
                        "avg resolution time."),
        },
        "search_datasets": {
            "type": "read",
            "description": "Search dataset metadata.",
            "parameters": {"uploaded_by": "Optional string e.g. data_scientist."},
            "returns": "List of dataset metadata dictionaries.",
        },
        "get_dataset": {
            "type": "read",
            "description": "Retrieve a single dataset metadata record.",
            "parameters": {"dataset_id": "Required integer."},
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
            "returns": ("Dictionary with tickets_by_assignee and "
                        "open_tickets_by_assignee."),
        },
        "close_incident": {
            "type": "write",
            "description": ("Propose closing an incident (sets status to Closed). "
                            "Requires admin confirmation."),
            "parameters": {"incident_id": "Required integer."},
            "returns": "Pending action stored for admin confirmation.",
        },
        "update_incident": {
            "type": "write",
            "description": ("Propose updating fields on an incident. "
                            "Requires admin confirmation."),
            "parameters": {
                "incident_id": "Required integer.",
                "updates": "Required dict of field -> new value e.g. {'status': 'Resolved'}.",
            },
            "returns": "Pending action stored for admin confirmation.",
        },
        "create_incident": {
            "type": "write",
            "description": ("Propose creating a new incident. "
                            "Requires admin confirmation."),
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
            "description": ("Propose closing an IT ticket (sets status to Closed). "
                            "Requires admin confirmation."),
            "parameters": {"ticket_id": "Required integer."},
            "returns": "Pending action stored for admin confirmation.",
        },
        "assign_ticket": {
            "type": "write",
            "description": ("Propose assigning an IT ticket to a support engineer. "
                            "Requires admin confirmation."),
            "parameters": {
                "ticket_id": "Required integer.",
                "assignee": "Required string e.g. IT_Support_A.",
            },
            "returns": "Pending action stored for admin confirmation.",
        },
        "update_ticket": {
            "type": "write",
            "description": ("Propose updating fields on an IT ticket. "
                            "Requires admin confirmation."),
            "parameters": {
                "ticket_id": "Required integer.",
                "updates": "Required dict of field -> new value.",
            },
            "returns": "Pending action stored for admin confirmation.",
        },
        "create_ticket": {
            "type": "write",
            "description": ("Propose creating a new IT ticket. "
                            "Requires admin confirmation."),
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
