"""Cyber Intelligence Agent controller.

Three modes: incident investigation, security monitoring and open chat with the
tool-based agent. A PDF report is generated after every successful run.
"""

import os

from django.http import FileResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from cyber.agent import agent as agent_core
from cyber.agent import investigation as agent_investigation
from cyber.agent import monitoring as agent_monitoring
from cyber.agent import reporting as agent_reporting
from cyber.decorators import login_required_custom
from cyber.features.cyber_agent import js_view


@login_required_custom
def index(request):
    error = None
    agent_text = request.session.get("agent_text")
    report_available = bool(request.session.get("latest_report_path"))

    if request.method == "POST":
        mode = request.POST.get("mode")

        if mode == "new":
            request.session.pop("agent_text", None)
            request.session.pop("agent_messages", None)
            request.session.pop("agent_pending_action", None)
            request.session.pop("investigation_result", None)
            request.session.pop("monitoring_summary", None)
            request.session.pop("latest_report_path", None)
            return HttpResponseRedirect(reverse("cyber:cyber_agent"))

        if mode == "investigate":
            try:
                incident_id = int(request.POST.get("incident_id"))
                result = agent_investigation.investigate_incident(incident_id)
                request.session["investigation_result"] = result
                if result.get("incident") is None:
                    agent_text = result.get("summary_insights")
                else:
                    lines = [result.get("summary_insights", "")]
                    lines.append("\nInvestigation activity log:")
                    lines.extend(f"- {log}" for log in result.get("activity_log", []))
                    agent_text = "\n".join(lines)
                request.session["agent_text"] = agent_text
            except (ValueError, TypeError):
                error = "Please enter a valid incident ID."

        elif mode == "monitoring":
            summary = agent_monitoring.generate_monitoring_summary(threshold=5)
            request.session["monitoring_summary"] = summary
            totals = summary.get("totals", {})
            lines = ["Security monitoring scan completed.\n"]
            lines.append(f"- New critical incidents: {totals.get('new_critical_incidents', 0)}")
            lines.append(f"- Unresolved critical incidents: {totals.get('unresolved_critical_incidents', 0)}")
            lines.append(f"- High priority open tickets: {totals.get('high_priority_tickets', 0)}")
            lines.append(f"- Category spikes: {totals.get('category_spikes', 0)}")
            alerts = summary.get("alerts", [])
            if alerts:
                lines.append("\nAlerts:")
                for a in alerts:
                    subject = a.get("incident_id") or a.get("ticket_id") or a.get("category")
                    lines.append(f"- [{a.get('alert_type')}] {subject}: {a.get('recommended_action')}")
            else:
                lines.append("\nNo alerts triggered.")
            agent_text = "\n".join(lines)
            request.session["agent_text"] = agent_text

        elif mode == "chat":
            question = request.POST.get("question", "").strip()
            if question:
                history = request.session.get("agent_messages", [])
                result = agent_core.run_agent(question, history=history[-10:])
                agent_text = result.get("final_answer", "")
                request.session["agent_text"] = agent_text
                if result.get("pending_action"):
                    request.session["agent_pending_action"] = result["pending_action"]
                request.session["agent_last_trace"] = result.get("tool_trace", [])
                request.session["agent_messages"] = (
                    history + [{"role": "user", "content": question},
                               {"role": "assistant", "content": agent_text}])[-30:]
            else:
                error = "Please enter a question."

        if agent_text and not error:
            report = agent_reporting.generate_cyber_ops_report()
            if report.get("success"):
                request.session["latest_report_path"] = report["file_path"]
            report_available = bool(request.session.get("latest_report_path"))

    return render(request, "cyber_agent/view.html", {
        "agent_text": request.session.get("agent_text"),
        "report_available": report_available,
        "pending": request.session.get("agent_pending_action"),
        "role": request.session.get("role"),
        "active": "cyber_agent",
        "error": error,
        "js_view": js_view.build_js({}),
    })


@login_required_custom
def download_report(request):
    path = request.session.get("latest_report_path")
    if not path or not os.path.exists(path):
        return HttpResponseRedirect(reverse("cyber:cyber_agent"))
    return FileResponse(open(path, "rb"), content_type="application/pdf",
                        as_attachment=True, filename=os.path.basename(path))
