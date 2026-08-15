from django.urls import path
from django.views.generic import RedirectView

from cyber.features.admin_management import index as admin_management
from cyber.features.ai_assistant import index as ai_assistant
from cyber.features.analysis_reports import index as analysis_reports
from cyber.features.auth import index as auth
from cyber.features.cyber_agent import index as cyber_agent
from cyber.features.dashboard import index as dashboard
from cyber.features.profile import index as profile

app_name = "cyber"

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="cyber:login", permanent=False),
         name="index"),
    path("login/", auth.login, name="login"),
    path("register/", auth.register, name="register"),
    path("logout/", auth.logout, name="logout"),
    path("dashboard/", dashboard.index, name="dashboard"),
    path("ai-assistant/", ai_assistant.index, name="ai_assistant"),
    path("profile/", profile.index, name="profile"),
    path("analysis-reports/", analysis_reports.index,
         name="analysis_reports"),
    path("admin-management/", admin_management.index,
         name="admin_management"),
    path("cyber-agent/", cyber_agent.index, name="cyber_agent"),
    path("cyber-agent/report/download/", cyber_agent.download_report,
         name="download_report"),
]
