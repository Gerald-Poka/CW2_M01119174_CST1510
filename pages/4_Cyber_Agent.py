# pages/3_Cyber_Agent.py

import streamlit as st
import os
from agent_v2 import agent, memory
from agent_v2.monitoring import generate_monitoring_summary
from agent_v2.investigation import investigate_incident
from agent_v2.tools import incident_tools, ticket_tools, analytics_tools
from agent_v2.tools import action_tools

st.set_page_config(page_title="Cyber Intelligence Operations Agent", page_icon="🛡️")

# --- Access control: must be logged in ---
if not st.session_state.get("logged_in", False):
    st.error("Please log in to access this page.")
    if st.button("Go to Login Page"):
        st.session_state.logged_in = False
        st.switch_page("Home.py")
    st.stop()

user_role = st.session_state.get("role", "user")

st.title("Cyber Intelligence Operations Agent")

# Ensure agent state is initialized
memory.initialize_agent_state()

# --- Pop-down flap: Task catalogue and example prompts ---
with st.expander("Show Cyber Agent Task Guide (examples & prompts)", expanded=False):
    st.markdown("### What can the Cyber Intelligence Agent do?")
    st.write(
        "This agent can perform multi-step cybersecurity operations using your database. "
        "Here are some supported tasks and example prompts you can copy or adapt."
    )

    st.markdown("#### 1. Incident Investigation")
    st.write(
        "- **Task:** Investigate a specific incident and look for related patterns.\n"
        "- **Example prompts:**\n"
        "  - `Investigate incident 1023.`\n"
        "  - `Is incident 1050 part of a broader pattern?`\n"
    )

    st.markdown("#### 2. Incident Search & Analysis")
    st.write(
        "- **Task:** Find incidents that match certain criteria.\n"
        "- **Example prompts:**\n"
        "  - `Find all open critical incidents.`\n"
        "  - `Show me recent phishing incidents that are still open.`\n"
        "  - `Summarise the current incident situation by severity and status.`\n"
    )

    st.markdown("#### 3. IT Ticket Operations & Workload")
    st.write(
        "- **Task:** Analyse IT support workload and ticket status.\n"
        "- **Example prompts:**\n"
        "  - `Find high priority tickets and analyse support workload.`\n"
        "  - `Which IT support engineer has the most open tickets?`\n"
        "  - `List all open high-priority tickets.`\n"
    )

    st.markdown("#### 4. Monitoring & Alerts")
    st.write(
        "- **Task:** Run monitoring checks to identify urgent issues.\n"
        "- **Example prompts:**\n"
        "  - `Check whether there are any urgent cybersecurity issues.`\n"
        "  - `Run a monitoring summary for critical incidents and high-priority tickets.`\n"
    )

    st.markdown("#### 5. Cybersecurity Operations Summary")
    st.write(
        "- **Task:** Get a high-level overview of current operations.\n"
        "- **Example prompts:**\n"
        "  - `Give me a cybersecurity operations summary.`\n"
        "  - `Summarise incidents, tickets, and datasets in one report.`\n"
    )

    st.markdown("#### 6. (Planned) Controlled Write Actions – Admin only")
    st.write(
        "These actions will only be executed after **explicit admin confirmation**.\n"
        "For now, the agent may propose these but they will not run automatically.\n"
        "- **Examples:**\n"
        "  - `Recommend whether incident 1023 should be closed.`\n"
        "  - `Propose ticket assignments to balance workload.`\n"
    )

    st.info(
        "You can type your own natural-language request below. "
        "The agent will choose tools, analyse the data and produce a final answer."
    )

st.markdown("---")

# --- Chat / interaction area ---

# Local session for this page: separate from your existing assistant
if "agent_v2_ui_messages" not in st.session_state:
    st.session_state["agent_v2_ui_messages"] = []

# Display previous messages (simple text, not the old chat component)
for msg in st.session_state["agent_v2_ui_messages"]:
    role = msg["role"]
    content = msg["content"]
    if role == "user":
        st.markdown(f"**You:** {content}")
    else:
        st.markdown(f"**Agent:** {content}")

# Input
user_input = st.chat_input("Ask the Cyber Intelligence Agent a question or give it a task...")

if user_input:
    # Store user message
    st.session_state["agent_v2_ui_messages"].append({"role": "user", "content": user_input})
    memory.add_message("user", user_input)

    # Get recent history for context
    history = memory.get_recent_messages()

    with st.spinner("Agent is thinking..."):
        # For now we directly call run_agent; later we can branch if the request
        # is specifically 'monitoring' or 'investigation' to use specialised flows.
        result = agent.run_agent(user_input, history=history)

    final_answer = result.get("final_answer", "I couldn't generate a response.")
    activity_log = result.get("activity_log", [])
    tool_trace = result.get("tool_trace", [])
    # If agent proposed a write action, store it in memory
    if pending_action:
         memory.set_pending_action(pending_action)
    # Display agent answer
    st.markdown(f"**Agent:** {final_answer}")
    st.session_state["agent_v2_ui_messages"].append({"role": "assistant", "content": final_answer})
    memory.add_message("assistant", final_answer)

    # --- Activity / status display ---
    with st.expander("Show agent activity log", expanded=False):
        if activity_log:
            for step in activity_log:
                st.write(f"- {step}")
        else:
            st.write("No activity recorded for this request.")

    # --- Tool result summary (no raw internals/trace by default) ---
    with st.expander("Show tool calls (technical details)", expanded=False):
        if tool_trace:
            for call in tool_trace:
                st.write(f"**Tool:** {call['tool_name']}")
                st.write(f"- Success: {call['success']}")
                if not call["success"]:
                    st.write(f"- Error: {call['error']}")
                else:
                    # Show brief summary of result (len or keys)
                    result_obj = call["result"]
                    if isinstance(result_obj, list):
                        st.write(f"- Result: list with {len(result_obj)} items")
                    elif isinstance(result_obj, dict):
                        st.write(f"- Result keys: {list(result_obj.keys())}")
                    else:
                        st.write(f"- Result: {str(result_obj)[:300]}")
                st.markdown("---")
        else:
            st.write("No tools were called for this request.")

# --- Quick actions / shortcuts (buttons) ---

st.markdown("### Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Investigate an Incident (ID)", use_container_width=True):
        incident_id = st.number_input("Incident ID to investigate", min_value=0, step=1, key="investigate_inc_id")
        if st.button("Run Investigation", key="run_investigation_btn"):
            with st.spinner("Running investigation..."):
                result = investigate_incident(int(incident_id))
            st.subheader(f"Investigation for Incident {int(incident_id)}")
            for step in result["activity_log"]:
                st.write(f"- {step}")
            st.markdown("**Summary insights:**")
            st.write(result["summary_insights"])

with col2:
    if st.button("Run Monitoring Summary", use_container_width=True):
        with st.spinner("Running monitoring checks..."):
            summary = generate_monitoring_summary(threshold=5)
        st.subheader("Monitoring Summary")
        st.write("Totals:", summary["[                                                                                                                                                         totals"])
        st.markdown("**Alerts:**")
        if summary["alerts"]:
            for alert in summary["alerts"]:
                st.write(alert)
        else:
            st.write("No alerts detected.")

with col3:
    if st.button("Show Dashboard Snapshot", use_container_width=True):
        from agent_v2.tools.analytics_tools import get_dashboard_summary
        summary = get_dashboard_summary()
        st.subheader("Dashboard Snapshot")
        st.write(summary)

# --- Admin-only pending action confirmation (placeholder wiring) ---

from agent_v2 import memory as agent_memory  # alias to avoid confusion
pending = agent_memory.get_agent_state().get("pending_action")

if pending:
    st.markdown("---")
    st.subheader("Pending Action (requires admin confirmation)")

    st.write(f"**Action:** {pending.get('action_name')}")
    st.write(f"**Target:** {pending.get('target')}")
    st.write(f"**Reason:** {pending.get('reason')}")

    if user_role != "admin":
        st.warning("Only an admin can confirm and execute this action.")
    else:
        confirm_col, cancel_col = st.columns(2)
        with confirm_col:
            if st.button("Confirm Action", type="primary"):
                action_name = pending.get("action_name")
                args = pending.get("arguments", {}) or {}
                success = False

                # Map action_name -> low-level write function
                try:
                    if action_name == "close_incident":
                        success = action_tools.close_incident(**args)
                    elif action_name == "update_incident":
                        # expects arguments: incident_id, updates
                        success = action_tools.update_incident(**args)
                    elif action_name == "create_incident":
                        new_id = action_tools.create_incident(**args)
                        success = new_id is not None
                    elif action_name == "close_ticket":
                        success = action_tools.close_ticket(**args)
                    elif action_name == "assign_ticket":
                        success = action_tools.assign_ticket(**args)
                    elif action_name == "update_ticket":
                        success = action_tools.update_ticket(**args)
                    elif action_name == "create_ticket":
                        new_ticket_id = action_tools.create_ticket(**args)
                        success = new_ticket_id is not None
                    else:
                        st.error(f"Unknown action name: {action_name}")
                except Exception as e:
                    success = False
                    st.error(f"Error executing action: {e}")

                if success:
                    st.success("Action executed successfully.")
                else:
                    st.error("Failed to execute the action.")

                # Clear pending action
                agent_memory.set_pending_action(None)
                st.experimental_rerun()

        with cancel_col:
            if st.button("Cancel Action"):
                agent_memory.set_pending_action(None)
                st.info("Pending action cancelled.")
                st.experimental_rerun()
                
                
from agent_v2.reporting import generate_cyber_ops_report

st.markdown("### Reporting")

if st.button("Generate Cybersecurity Operations Report (PDF)"):
    with st.spinner("Generating report..."):
        report_result = generate_cyber_ops_report()

    if report_result["success"]:
        st.success("Report generated successfully.")
        file_path = report_result["file_path"]

        # Offer download; Streamlit can read the file and send it
        with open(file_path, "rb") as f:
            pdf_bytes = f.read()

        st.download_button(
            label="Download report PDF",
            data=pdf_bytes,
            file_name=file_path.split(os.sep)[-1],
            mime="application/pdf",
        )
    else:
        st.error(f"Failed to generate report: {report_result['error']}")
                
                

# --- Reset / clear task button ---

st.markdown("---")
if st.button("Clear agent conversation and state"):
    memory.clear_agent_state()
    st.session_state["agent_v2_ui_messages"] = []
    st.success("Agent conversation and state cleared for this session.")
    st.experimental_rerun()
