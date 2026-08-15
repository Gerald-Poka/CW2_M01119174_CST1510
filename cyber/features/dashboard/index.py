"""Dashboard controller."""

from django.shortcuts import render

from cyber.decorators import login_required_custom
from cyber.features.dashboard import js_view
from cyber.features.dashboard import view as dashboard_view


@login_required_custom
def index(request):
    context = dashboard_view.build_context(request)
    context["js_view"] = js_view.build_js(context)
    return render(request, "dashboard/view.html", context)
