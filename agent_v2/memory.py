# agent_v2/memory.py

"""
Session-specific memory and task state for the Cyber Intelligence Agent.

This module uses Streamlit's st.session_state to keep:
- recent conversation messages
- current task focus (incident / ticket)
- previous tool results
- pending actions (to be confirmed by the user)
"""

from typing import Any, Dict, List, Optional
import streamlit as st


# ---- Keys used inside st.session_state ----
_AGENT_STATE_KEY = "agent_v2_state"
_AGENT_MESSAGES_KEY = "agent_v2_messages"


def initialize_agent_state() -> None:
    """
    Initialize the agent's state in st.session_state if not already present.

    This should be called at the start of any page that uses the agent.
    """
    if _AGENT_STATE_KEY not in st.session_state:
        st.session_state[_AGENT_STATE_KEY] = {
            "current_task": None,
            "current_incident": None,
            "current_ticket": None,
            "previous_tool_results": [],
            "pending_action": None,         # e.g. {"action": "...", "args": {...}, "reason": "..."}
            "requires_confirmation": False, # whether we are waiting for user confirmation
        }

    if _AGENT_MESSAGES_KEY not in st.session_state:
        st.session_state[_AGENT_MESSAGES_KEY] = []  # list of {"role": "user"|"assistant", "content": str}


# ---- Conversation memory ----

def add_message(role: str, content: str) -> None:
    """
    Add a message to the agent's conversation history.

    role: "user" or "assistant"
    content: text of the message
    """
    initialize_agent_state()
    messages: List[Dict[str, str]] = st.session_state[_AGENT_MESSAGES_KEY]
    messages.append({"role": role, "content": content})

    # Prevent unlimited growth – keep last N messages
    MAX_MESSAGES = 30
    if len(messages) > MAX_MESSAGES:
        st.session_state[_AGENT_MESSAGES_KEY] = messages[-MAX_MESSAGES:]


def get_recent_messages(n: int = 10) -> List[Dict[str, str]]:
    """
    Get the most recent n messages from the conversation history.
    """
    initialize_agent_state()
    messages: List[Dict[str, str]] = st.session_state[_AGENT_MESSAGES_KEY]
    return messages[-n:]


# ---- Task / working memory ----

def set_current_task(task: Optional[str]) -> None:
    """
    Set a human-readable description of the current task, e.g.:
    - "Investigate incident 1023"
    - "Summarise open critical incidents"
    """
    initialize_agent_state()
    st.session_state[_AGENT_STATE_KEY]["current_task"] = task


def set_current_incident(incident_id: Optional[int]) -> None:
    """
    Track which incident the agent is currently focused on.
    """
    initialize_agent_state()
    st.session_state[_AGENT_STATE_KEY]["current_incident"] = incident_id


def set_current_ticket(ticket_id: Optional[int]) -> None:
    """
    Track which IT ticket the agent is currently focused on.
    """
    initialize_agent_state()
    st.session_state[_AGENT_STATE_KEY]["current_ticket"] = ticket_id


def store_tool_result(tool_name: str, args: Dict[str, Any], result: Any) -> None:
    """
    Store a record of a tool result in the agent's working memory.

    This allows follow-up questions like:
    "What about the incidents you just found?"
    """
    initialize_agent_state()
    state = st.session_state[_AGENT_STATE_KEY]

    record = {
        "tool_name": tool_name,
        "args": args,
        "result": result,
    }
    state["previous_tool_results"].append(record)

    # Limit size
    MAX_RESULTS = 10
    if len(state["previous_tool_results"]) > MAX_RESULTS:
        state["previous_tool_results"] = state["previous_tool_results"][-MAX_RESULTS:]


def set_pending_action(action: Optional[Dict[str, Any]]) -> None:
    """
    Set or clear a pending action that requires user confirmation.

    Example structure:
    {
        "action_name": "close_incident",
        "target": {"incident_id": 1023},
        "arguments": {...},
        "reason": "Incident is resolved and verified."
    }
    """
    initialize_agent_state()
    state = st.session_state[_AGENT_STATE_KEY]
    state["pending_action"] = action
    state["requires_confirmation"] = bool(action)


def get_agent_state() -> Dict[str, Any]:
    """
    Return the full agent state dict.
    """
    initialize_agent_state()
    return st.session_state[_AGENT_STATE_KEY]


def clear_agent_state() -> None:
    """
    Reset the agent's memory and task state for a fresh session.
    """
    if _AGENT_STATE_KEY in st.session_state:
        del st.session_state[_AGENT_STATE_KEY]
    if _AGENT_MESSAGES_KEY in st.session_state:
        del st.session_state[_AGENT_MESSAGES_KEY]
        
def get_pending_action() -> Optional[Dict[str, Any]]:
    """
    Return the current pending action dict or None if there isn't one.
    """
    initialize_agent_state()
    state = st.session_state[_AGENT_STATE_KEY]
    return state.get("pending_action")
