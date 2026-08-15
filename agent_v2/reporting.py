# agent_v2/reporting.py

"""
Automated cybersecurity operations reporting.

This module collects metrics from the existing tools, optionally uses
Gemini to help generate a narrative, and then produces a PDF report
using reportlab.

The AI does NOT write files directly. All file I/O is controlled here.
"""

from typing import Dict, Any
import os
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from google import genai
import streamlit as st

from agent_v2.tools import analytics_tools, incident_tools, ticket_tools, metadata_tools

# Use the same Gemini client configuration as elsewhere
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])


def _collect_raw_metrics() -> Dict[str, Any]:
    """
    Collect raw statistics from existing tools.

    Returns:
        A dict with various incident/ticket/dataset metrics.
    """
    dashboard = analytics_tools.get_dashboard_summary()
    incident_stats = incident_tools.get_incident_statistics()
    ticket_stats = ticket_tools.get_ticket_statistics()

    # Simple dataset summary
    all_datasets = metadata_tools.search_datasets()
    dataset_summary = {
        "total_datasets": len(all_datasets),
        "by_uploader": {},
    }
    for ds in all_datasets:
        who = ds.get("uploaded_by", "unknown")
        dataset_summary["by_uploader"].setdefault(who, 0)
        dataset_summary["by_uploader"][who] += 1

    return {
        "dashboard": dashboard,
        "incident_stats": incident_stats,
        "ticket_stats": ticket_stats,
        "dataset_summary": dataset_summary,
    }


def _generate_report_text(metrics: Dict[str, Any]) -> Dict[str, str]:
    """
    Use Gemini to generate structured report sections (as text) from metrics.

    Returns:
        {
          "executive_summary": str,
          "incident_overview": str,
          "critical_incidents": str,
          "incident_categories": str,
          "it_operations": str,
          "outstanding_issues": str,
          "recommended_actions": str,
        }
    """
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

For each section, write 1–3 concise paragraphs. Be factual based on the metrics; do not invent specific numbers not present in the metrics. Use plain text, no markdown or bullet points.

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

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    raw_text = response.text.strip()

    import json
    try:
        sections = json.loads(raw_text)
    except json.JSONDecodeError:
        # Fallback: put everything in executive_summary if JSON parsing fails
        sections = {
            "executive_summary": raw_text,
            "incident_overview": "",
            "critical_incidents": "",
            "incident_categories": "",
            "it_operations": "",
            "outstanding_issues": "",
            "recommended_actions": "",
        }

    # Ensure all expected keys exist
    default_keys = [
        "executive_summary",
        "incident_overview",
        "critical_incidents",
        "incident_categories",
        "it_operations",
        "outstanding_issues",
        "recommended_actions",
    ]
    for key in default_keys:
        sections.setdefault(key, "")

    return sections


def _write_pdf_report(
    sections: Dict[str, str],
    metrics: Dict[str, Any],
    output_dir: str = "reports",
) -> str:
    """
    Create a PDF report using reportlab and return the file path.

    The AI does not write files directly; all file operations are here.
    """
    os.makedirs(output_dir, exist_ok=True)

    # Build filename with timestamp
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"cyber_ops_report_{date_str}.pdf"
    filepath = os.path.join(output_dir, filename)

    # Basic PDF setup
    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4
    margin = 20 * mm
    y = height - margin

    def draw_heading(text: str, size: int = 16):
        nonlocal y
        c.setFont("Helvetica-Bold", size)
        c.drawString(margin, y, text)
        y -= 8 * mm

    def draw_paragraph(text: str, size: int = 11, leading: int = 14):
        """
        Very simple paragraph writer. For more complex layouts,
        reportlab.platypus would be better, but this keeps it simple.
        """
        nonlocal y
        c.setFont("Helvetica", size)
        max_width = width - 2 * margin

        # Naive wrapping
        from textwrap import wrap
        lines = []
        for paragraph in text.split("\n"):
            wrapped = wrap(paragraph, width=90)  # approximate characters per line
            if not wrapped:
                lines.append("")
            else:
                lines.extend(wrapped)

        for line in lines:
            if y < margin:
                c.showPage()
                y = height - margin
                c.setFont("Helvetica", size)
            c.drawString(margin, y, line)
            y -= leading

        y -= 4  # small extra spacing

    # Title and date
    draw_heading("Cybersecurity Operations Report", size=20)
    c.setFont("Helvetica", 10)
    c.drawString(margin, y, f"Generated on: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    y -= 10 * mm

    # Executive summary
    draw_heading("1. Executive Summary")
    draw_paragraph(sections.get("executive_summary", ""))

    # Incident overview
    draw_heading("2. Incident Overview")
    draw_paragraph(sections.get("incident_overview", ""))

    # Critical incidents
    draw_heading("3. Critical Incidents")
    draw_paragraph(sections.get("critical_incidents", ""))

    # Incident categories and trends
    draw_heading("4. Incident Categories and Trends")
    draw_paragraph(sections.get("incident_categories", ""))

    # IT operations
    draw_heading("5. IT Operations and Ticket Handling")
    draw_paragraph(sections.get("it_operations", ""))

    # Outstanding issues
    draw_heading("6. Outstanding Issues and Risks")
    draw_paragraph(sections.get("outstanding_issues", ""))

    # Recommended actions
    draw_heading("7. Recommended Actions")
    draw_paragraph(sections.get("recommended_actions", ""))

    c.showPage()
    c.save()

    return filepath


def generate_cyber_ops_report() -> Dict[str, Any]:
    """
    High-level function to generate a cybersecurity operations report.

    Steps:
      1. Collect metrics using read-only tools.
      2. Ask Gemini to generate structured section texts.
      3. Build a PDF file with those sections.
      4. Return paths and some metadata.

    Returns:
        {
          "success": bool,
          "file_path": str | None,
          "metrics": dict,
          "sections": dict,
          "error": str | None,
        }
    """
    try:
        metrics = _collect_raw_metrics()
        sections = _generate_report_text(metrics)
        file_path = _write_pdf_report(sections, metrics)
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
