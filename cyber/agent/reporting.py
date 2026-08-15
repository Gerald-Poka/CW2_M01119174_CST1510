import json
import os
from datetime import datetime
from textwrap import wrap

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from django.conf import settings

from cyber import gemini_service
from cyber.agent import tools

REPORT_DIR = settings.BASE_DIR / "reports"


def _collect_raw_metrics():
    dashboard = tools.get_dashboard_summary()
    incident_stats = tools.get_incident_statistics()
    ticket_stats = tools.get_ticket_statistics()

    all_datasets = tools.search_datasets()
    dataset_summary = {"total_datasets": len(all_datasets), "by_uploader": {}}
    for ds in all_datasets:
        who = ds.get("uploaded_by", "unknown")
        dataset_summary["by_uploader"][who] = dataset_summary["by_uploader"].get(who, 0) + 1

    return {
        "dashboard": dashboard,
        "incident_stats": incident_stats,
        "ticket_stats": ticket_stats,
        "dataset_summary": dataset_summary,
    }


def _generate_report_text(metrics):
    prompt = f"""
You are a cybersecurity operations analyst.

You have the following metrics from a cyber intelligence platform:

METRICS (JSON-like):
{metrics}

Please generate a professional cybersecurity operations report broken into the following SECTIONS:

1. Executive summary
2. Incident overview
3. Critical incidents
4. Incident categories and trends
5. IT operations and ticket handling
6. Outstanding issues / risks
7. Recommended actions

For each section, write 1-3 concise paragraphs. Be factual based on the metrics; do not invent specific numbers not present in the metrics. Use plain text, no markdown or bullet points.

Return your answer as a JSON object with EXACT keys:
{{
  "executive_summary": "...",
  "incident_overview": "...",
  "critical_incidents": "...",
  "incident_categories": "...",
  "it_operations": "...",
  "outstanding_issues": "...",
  "recommended_actions": "..."
}}

Do not include any text outside the JSON. Do not include comments.
"""
    raw_text = gemini_service.generate_content(prompt)
    if raw_text is None:
        raw_text = "Unable to generate report narrative (AI service error)."

    try:
        sections = json.loads(raw_text)
    except (json.JSONDecodeError, TypeError):
        sections = {"executive_summary": raw_text}

    default_keys = [
        "executive_summary", "incident_overview", "critical_incidents",
        "incident_categories", "it_operations", "outstanding_issues",
        "recommended_actions",
    ]
    for key in default_keys:
        sections.setdefault(key, "")
    return sections


def _write_pdf_report(sections, output_dir=REPORT_DIR):
    output_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    filename = f"cyber_ops_report_{now.strftime('%Y-%m-%d_%H-%M-%S')}.pdf"
    filepath = output_dir / filename

    c = canvas.Canvas(str(filepath), pagesize=A4)
    width, height = A4
    margin = 20 * mm
    y = height - margin

    def draw_heading(text, size=16):
        nonlocal y
        c.setFont("Helvetica-Bold", size)
        c.drawString(margin, y, text)
        y -= 8 * mm

    def draw_paragraph(text, size=11, leading=14):
        nonlocal y
        c.setFont("Helvetica", size)
        lines = []
        for paragraph in text.split("\n"):
            wrapped = wrap(paragraph, width=90)
            lines.extend(wrapped or [""])
        for line in lines:
            if y < margin:
                c.showPage()
                y = height - margin
                c.setFont("Helvetica", size)
            c.drawString(margin, y, line)
            y -= leading
        y -= 4

    draw_heading("Cybersecurity Operations Report", size=20)
    c.setFont("Helvetica", 10)
    c.drawString(margin, y, f"Generated on: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    y -= 10 * mm

    draw_heading("1. Executive Summary")
    draw_paragraph(sections.get("executive_summary", ""))
    draw_heading("2. Incident Overview")
    draw_paragraph(sections.get("incident_overview", ""))
    draw_heading("3. Critical Incidents")
    draw_paragraph(sections.get("critical_incidents", ""))
    draw_heading("4. Incident Categories and Trends")
    draw_paragraph(sections.get("incident_categories", ""))
    draw_heading("5. IT Operations and Ticket Handling")
    draw_paragraph(sections.get("it_operations", ""))
    draw_heading("6. Outstanding Issues and Risks")
    draw_paragraph(sections.get("outstanding_issues", ""))
    draw_heading("7. Recommended Actions")
    draw_paragraph(sections.get("recommended_actions", ""))

    c.showPage()
    c.save()
    return str(filepath)


def generate_cyber_ops_report():
    try:
        metrics = _collect_raw_metrics()
        sections = _generate_report_text(metrics)
        file_path = _write_pdf_report(sections)
        return {
            "success": True,
            "file_path": file_path,
            "metrics": metrics,
            "sections": sections,
            "error": None,
        }
    except Exception as e:
        return {
            "success": False,
            "file_path": None,
            "metrics": {},
            "sections": {},
            "error": str(e),
        }
