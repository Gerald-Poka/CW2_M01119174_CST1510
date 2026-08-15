# agent_v2/agent.py

"""
Core Cyber Intelligence Agent.

Read tools  → executed immediately.
Write tools → stored as pending_action in memory for admin confirmation.
"""

from typing import Any, Dict, List, Optional, Tuple
import json
import logging

from google import genai
from agent_v2.tool_registry import (
    TOOL_FUNCTIONS,
    READ_TOOL_FUNCTIONS,
    WRITE_TOOL_FUNCTIONS,
    get_tool_descriptions,
)

logging.basicConfig(
    filename="gemini_errors.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def _get_client():
    """
    Create Gemini client lazily using Streamlit secrets.
    """
    import streamlit as st
    return genai.Client(api_key=st.secrets["GEMINI_API_KEY"])


def _build_system_prompt() -> str:
    tool_descriptions = get_tool_descriptions()
    tool_desc_json = json.dumps(tool_descriptions, indent=2)

    return f"""
You are a Cyber Intelligence Operations Agent for an internal cybersecurity platform.

You can READ data from the database and PROPOSE write actions.

AVAILABLE TOOLS:
{tool_desc_json}

HOW TO RESPOND:

1. To call a READ tool (type = "read"), respond with:
{{
  "action": "call_tool",
  "tool_name": "<read tool name>",
  "tool_args": {{}}
}}

2. To PROPOSE a write action (type = "write"), respond with:
{{
  "action": "propose_action",
  "tool_name": "<write tool name>",
  "tool_args": {{}},
  "reason": "<explain clearly why this action is recommended>"
}}

Write actions are NOT executed automatically.
They are stored as pending actions and require explicit confirmation from an admin user.
You must always use "propose_action" for write tools, never "call_tool".

3. To give a final answer, respond with:
{{
  "action": "final_answer",
  "answer": "<your answer>"
}}

STRICT RULES:
- Return ONLY a JSON object. No text before or after it.
- Do NOT wrap in markdown like ```json
- Do NOT add comments inside JSON.
- Do NOT invent tool names not in the list.
- Use "propose_action" for ALL write tools (close_incident, update_incident,
  create_incident, close_ticket, assign_ticket, update_ticket, create_ticket).
- Use "call_tool" ONLY for read tools.
- If the request is unrelated to cybersecurity or this database, use final_answer.
"""


def _call_gemini_for_action(
    user_request: str,
    history: Optional[List[Dict[str, str]]] = None,
    tool_results: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Ask Gemini what to do next.
    """
    system_prompt = _build_system_prompt()
    conversation_parts = [system_prompt]

    if history:
        history_text = ""
        for msg in history[-6:]:
            history_text += f"{msg['role']}: {msg['content']}\n"
        conversation_parts.append("Conversation history:\n" + history_text)

    if tool_results:
        tr_text = json.dumps(tool_results, indent=2, default=str)
        conversation_parts.append(
            "Previous tool calls and results:\n" + tr_text
        )

    conversation_parts.append(f"User request:\n{user_request}\n")
    conversation_parts.append(
        "Decide what to do next. "
        "Respond with ONLY a valid JSON object as described above."
    )

    full_prompt = "\n\n".join(conversation_parts)

    try:
        client = _get_client()
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt,
        )
        raw_text = response.text.strip()

    except Exception as e:
        logging.error(f"Gemini API error: {e}")
        return {
            "action": "final_answer",
            "answer": f"I encountered an error contacting the AI service: {e}",
        }

    # Strip markdown fences if present
    if raw_text.startswith("```"):
        lines = [
            line for line in raw_text.splitlines()
            if not line.startswith("```")
        ]
        raw_text = "\n".join(lines).strip()

    try:
        action_obj = json.loads(raw_text)
    except json.JSONDecodeError:
        logging.error(f"JSON decode failed. Raw response:\n{raw_text}")
        return {
            "action": "final_answer",
            "answer": raw_text,
        }

    if "action" not in action_obj:
        return {
            "action": "final_answer",
            "answer": raw_text,
        }

    return action_obj


def _execute_tool_call(
    tool_name: str,
    tool_args: Dict[str, Any],
) -> Tuple[bool, Any, str]:
    """
    Execute a READ tool only.
    """
    if tool_name not in READ_TOOL_FUNCTIONS:
        return (
            False,
            None,
            f"Tool '{tool_name}' is not a readable tool or does not exist.",
        )

    tool_fn = READ_TOOL_FUNCTIONS[tool_name]

    try:
        result = tool_fn(**tool_args)
        return True, result, ""
    except TypeError as e:
        return False, None, f"Wrong arguments for tool '{tool_name}': {e}"
    except Exception as e:
        logging.error(f"Tool error ({tool_name}): {e}")
        return False, None, f"Error running tool '{tool_name}': {e}"


def run_agent(
    user_request: str,
    history: Optional[List[Dict[str, str]]] = None,
    max_iterations: int = 5,
) -> Dict[str, Any]:
    """
    Run the agent loop.

    Returns:
        {
            "final_answer": str,
            "activity_log": List[str],
            "tool_trace": List[Dict],
            "pending_action": Dict or None
        }
    """
    activity_log: List[str] = []
    tool_trace: List[Dict[str, Any]] = []
    pending_action = None

    for iteration in range(max_iterations):

        activity_log.append(
            f"Step {iteration + 1}: Deciding what to do next..."
        )

        action_obj = _call_gemini_for_action(
            user_request=user_request,
            history=history,
            tool_results=tool_trace if tool_trace else None,
        )

        action = action_obj.get("action")

        # ── Read tool call ──────────────────────────────────────────────────
        if action == "call_tool":
            tool_name = action_obj.get("tool_name", "").strip()
            tool_args = action_obj.get("tool_args") or {}

            if not tool_name:
                activity_log.append(
                    "Agent requested a tool but gave no tool name."
                )
                break

            # Safety: if agent tries to call_tool on a write tool, redirect
            if tool_name in WRITE_TOOL_FUNCTIONS:
                activity_log.append(
                    f"Agent tried to directly call write tool '{tool_name}'. "
                    "Redirecting to propose_action."
                )
                pending_action = {
                    "action_name": tool_name,
                    "target": tool_args,
                    "arguments": tool_args,
                    "reason": "Agent recommended this action.",
                }
                final_answer = (
                    f"I recommend the action '{tool_name}' "
                    f"with the following details: {tool_args}. "
                    "This requires admin confirmation before it is executed."
                )
                activity_log.append(
                    f"Proposed write action: {tool_name}. Awaiting admin confirmation."
                )
                return {
                    "final_answer": final_answer,
                    "activity_log": activity_log,
                    "tool_trace": tool_trace,
                    "pending_action": pending_action,
                }

            activity_log.append(f"Calling tool: {tool_name}...")
            success, result, error_msg = _execute_tool_call(
                tool_name, tool_args
            )

            tool_call_record = {
                "tool_name": tool_name,
                "tool_args": tool_args,
                "success": success,
                "error": error_msg if not success else None,
                "result": result if success else None,
            }
            tool_trace.append(tool_call_record)

            if not success:
                activity_log.append(f"Tool '{tool_name}' failed: {error_msg}")
                return {
                    "final_answer": (
                        f"I tried to use the tool '{tool_name}' "
                        f"but encountered an error: {error_msg}"
                    ),
                    "activity_log": activity_log,
                    "tool_trace": tool_trace,
                    "pending_action": None,
                }

            activity_log.append(f"Tool '{tool_name}' ran successfully.")

        # ── Write action proposal ───────────────────────────────────────────
        elif action == "propose_action":
            tool_name = action_obj.get("tool_name", "").strip()
            tool_args = action_obj.get("tool_args") or {}
            reason = action_obj.get("reason", "No reason provided.")

            if tool_name not in WRITE_TOOL_FUNCTIONS:
                activity_log.append(
                    f"Agent proposed unknown write action: '{tool_name}'."
                )
                return {
                    "final_answer": (
                        f"I tried to propose an action '{tool_name}' "
                        "but it is not a recognised write operation."
                    ),
                    "activity_log": activity_log,
                    "tool_trace": tool_trace,
                    "pending_action": None,
                }

            pending_action = {
                "action_name": tool_name,
                "target": tool_args,
                "arguments": tool_args,
                "reason": reason,
            }

            activity_log.append(
                f"Proposed write action: '{tool_name}'. "
                "Awaiting admin confirmation."
            )

            final_answer = (
                f"I recommend the following action: **{tool_name}**.\n\n"
                f"**Reason:** {reason}\n\n"
                f"**Details:** {json.dumps(tool_args, indent=2)}\n\n"
                "This action has been saved as a pending action. "
                "An admin must confirm it before it is executed."
            )

            return {
                "final_answer": final_answer,
                "activity_log": activity_log,
                "tool_trace": tool_trace,
                "pending_action": pending_action,
            }

        # ── Final answer ────────────────────────────────────────────────────
        elif action == "final_answer":
            answer = action_obj.get("answer", "")
            if not answer:
                answer = (
                    "The agent completed its work but produced no response. "
                    "Please try rephrasing your question."
                )
            activity_log.append("Final answer generated.")
            return {
                "final_answer": answer,
                "activity_log": activity_log,
                "tool_trace": tool_trace,
                "pending_action": None,
            }

        # ── Unknown action ──────────────────────────────────────────────────
        else:
            activity_log.append(
                f"Unexpected action from agent: '{action}'. Stopping."
            )
            return {
                "final_answer": (
                    "I encountered an internal error while "
                    "processing your request."
                ),
                "activity_log": activity_log,
                "tool_trace": tool_trace,
                "pending_action": None,
            }

    # Max iterations reached
    activity_log.append("Reached maximum number of steps.")
    return {
        "final_answer": (
            "I reached the maximum number of steps. "
            "Please try a more specific question."
        ),
        "activity_log": activity_log,
        "tool_trace": tool_trace,
        "pending_action": None,
    }
