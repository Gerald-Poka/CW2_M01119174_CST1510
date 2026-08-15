"""Analysis Reports controller."""

from django.shortcuts import render

from cyber import services
from cyber.decorators import login_required_custom
from cyber.features.analysis_reports import js_view


@login_required_custom
def index(request):
    runs = services.get_report_runs()
    selected_run = request.GET.get("run_id", runs[0] if runs else None)
    reports = services.get_reports(run_id=selected_run) if selected_run else []
    return render(request, "analysis_reports/view.html", {
        "runs": runs,
        "selected_run": selected_run,
        "reports": reports,
        "is_latest": bool(runs and selected_run == runs[0]),
        "active": "analysis_reports",
        "js_view": js_view.build_js({}),
    })
