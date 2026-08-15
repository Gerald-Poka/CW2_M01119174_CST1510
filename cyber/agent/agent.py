import json
import logging

from cyber import gemini_service
from cyber.agent.tool_registry import (
    READ_TOOL_FUNCTIONS,
    WRITE_TOOL_FUNCTIONS,
    get_tool_descriptions,
)

logger = logging.getLogger(__name__)


def _build_system_prompt():
    tool_desc_json = json.dumps(get_tool_descriptions(), indent=2)
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


def _call_gemini_for_action(user_request, history=None, tool_results=None):
    parts = [_build_system_prompt()]

    if history:
        history_text = "\n".join(
            f"{msg['role']}: {msg['content']}" for msg in history[-6:]
        )
        parts.append("Conversation history:\n" + history_text)

    if tool_results:
        parts.append(
            "Previous tool calls and results:\n"
            + json.dumps(tool_results, indent=2, default=str)
        )

    parts.append(f"User request:\n{user_request}\n")
    parts.append(
        "Decide what to do next. "
        "Respond with ONLY a valid JSON object as described above."
    )

    raw_text = gemini_service.generate_content("\n\n".join(parts))
    if raw_text is None:
        return {
            "action": "final_answer",
            "answer": "I encountered an error contacting the AI service.",
        }

    if raw_text.startswith("```"):
        raw_text = "\n".join(
            line for line in raw_text.splitlines() if not line.startswith("```")
        ).strip()

    try:
        action_obj = json.loads(raw_text)
    except json.JSONDecodeError:
        logger.error("JSON decode failed. Raw response:\n%s", raw_text)
        return {"action": "final_answer", "answer": raw_text}

    if "action" not in action_obj:
        return {"action": "final_answer", "answer": raw_text}

    return action_obj


def _execute_tool_call(tool_name, tool_args):
    if tool_name not in READ_TOOL_FUNCTIONS:
        return False, None, f"Tool '{tool_name}' is not a readable tool or does not exist."
    try:
        result = READ_TOOL_FUNCTIONS[tool_name](**tool_args)
        return True, result, ""
    except TypeError as e:
        return False, None, f"Wrong arguments for tool '{tool_name}': {e}"
    except Exception as e:
        logger.error("Tool error (%s): %s", tool_name, e)
        return False, None, f"Error running tool '{tool_name}': {e}"


def run_agent(user_request, history=None, max_iterations=5):
    activity_log = []
    tool_trace = []
    pending_action = None

    for iteration in range(max_iterations):
        activity_log.append(f"Step {iteration + 1}: Deciding what to do next...")

        action_obj = _call_gemini_for_action(
            user_request=user_request,
            history=history,
            tool_results=tool_trace if tool_trace else None,
        )
        action = action_obj.get("action")

        if action == "call_tool":
            tool_name = (action_obj.get("tool_name") or "").strip()
            tool_args = action_obj.get("tool_args") or {}

            if not tool_name:
                activity_log.append("Agent requested a tool but gave no tool name.")
                break

            if tool_name in WRITE_TOOL_FUNCTIONS:
                pending_action = {
                    "action_name": tool_name,
                    "target": tool_args,
                    "arguments": tool_args,
                    "reason": "Agent recommended this action.",
                }
                return {
                    "final_answer": (
                        f"I recommend the action '{tool_name}' "
                        f"with the following details: {tool_args}. "
                        "This requires admin confirmation before it is executed."
                    ),
                    "activity_log": activity_log,
                    "tool_trace": tool_trace,
                    "pending_action": pending_action,
                }

            activity_log.append(f"Calling tool: {tool_name}...")
            success, result, error_msg = _execute_tool_call(tool_name, tool_args)
            tool_trace.append({
                "tool_name": tool_name,
                "tool_args": tool_args,
                "success": success,
                "error": error_msg if not success else None,
                "result": result if success else None,
            })

            if not success:
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

        elif action == "propose_action":
            tool_name = (action_obj.get("tool_name") or "").strip()
            tool_args = action_obj.get("tool_args") or {}
            reason = action_obj.get("reason", "No reason provided.")

            if tool_name not in WRITE_TOOL_FUNCTIONS:
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
            return {
                "final_answer": (
                    f"I recommend the following action: **{tool_name}**.\n\n"
                    f"**Reason:** {reason}\n\n"
                    f"**Details:** {json.dumps(tool_args, indent=2)}\n\n"
                    "This action has been saved as a pending action. "
                    "An admin must confirm it before it is executed."
                ),
                "activity_log": activity_log,
                "tool_trace": tool_trace,
                "pending_action": pending_action,
            }

        elif action == "final_answer":
            answer = action_obj.get("answer", "")
            if not answer:
                answer = ("The agent completed its work but produced no response. "
                          "Please try rephrasing your question.")
            activity_log.append("Final answer generated.")
            return {
                "final_answer": answer,
                "activity_log": activity_log,
                "tool_trace": tool_trace,
                "pending_action": None,
            }

        else:
            activity_log.append(f"Unexpected action from agent: '{action}'. Stopping.")
            return {
                "final_answer": "I encountered an internal error while processing your request.",
                "activity_log": activity_log,
                "tool_trace": tool_trace,
                "pending_action": None,
            }

    activity_log.append("Reached maximum number of steps.")
    return {
        "final_answer": ("I reached the maximum number of steps. "
                         "Please try a more specific question."),
        "activity_log": activity_log,
        "tool_trace": tool_trace,
        "pending_action": None,
    }
