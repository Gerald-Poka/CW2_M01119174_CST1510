"""
Headless AI analysis runner (Sentinel audit monitoring) for Django.

Replaces the legacy Streamlit ``ai_monitor.py`` scheduler script. Every run
(typically triggered every minute by Windows Task Scheduler) does:

  1. Pulls the next 100-row window of audit events from the ``audit_trail``
     table (which mirrors the external Sentinel system's audit log).
  2. Asks Gemini a rotating subset of the monitoring question pool about the
     events in that window only.
  3. Stores each question/answer in the ``analytical_reports`` table, which the
     Analysis Reports page displays live.

This simulates near-real-time monitoring: each run analyses a new window and a
fresh report appears on the dashboard.

Usage:
    python manage.py run_ai_monitor
"""

import logging
import os
import time
import traceback
from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand

from cyber import gemini_service
from cyber import services

logger = logging.getLogger(__name__)

AUDIT_WINDOW_SIZE = int(os.environ.get("AUDIT_WINDOW_SIZE", "100"))
QUESTIONS_PER_RUN = int(os.environ.get("QUESTIONS_PER_RUN", "3"))
SLEEP_BETWEEN_QUESTIONS = float(os.environ.get("SLEEP_BETWEEN_QUESTIONS", "3"))

VERBOSE = os.environ.get("AI_MONITOR_VERBOSE", "0") == "1"

REPORT_DIR = settings.BASE_DIR / "reports"
LOG_FILE = settings.BASE_DIR / "gemini_errors.log"
RUN_LOG = REPORT_DIR / "ai_monitor.log"

# Large pool of monitoring questions covering the key cyber areas of the audit
# trail. A rotating subset is asked on every run.
MONITOR_QUESTIONS = [
    "How many failed logins (LOGIN_FAILED) appear in this window, and which user IDs and IPs are involved?",
    "How many HTTP 401 responses appear, and do they indicate repeated failed authentication?",
    "How many HTTP 429 rate-limited responses appear, and which users or IPs triggered them?",
    "Are there HTTP 500 or 503 server errors in this window that could indicate instability or attack?",
    "Which data exports (EXPORT_DATA) or bulk downloads appear, and are any of them suspicious?",
    "Which users performed privileged actions (UPDATE_USER, UPDATE_CONFIG, DELETE, PATCH on /api/users) in this window?",
    "Which outbound connections (OUTBOUND_CONNECTION) point to unexpected destinations?",
    "What file access (FILE_ACCESS) or system file activity occurred, and is any of it unusual?",
    "Which sessions show a login followed by mass access - a possible account takeover pattern?",
    "Which events in this window lack the normal_activity flag, and why might they be suspicious?",
    "Which endpoints were hit the most, and could the pattern indicate scanning or brute force?",
    "Is there evidence of a login flood or credential stuffing from a single IP or user?",
    "Which users accessed resources or locations outside their normal pattern (device/location changes in metadata)?",
    "Are there configuration changes (UPDATE_CONFIG) that could weaken security?",
    "Which users have abnormal request volume spikes compared to the rest of the window?",
    "Which IPs show the highest error rates (401/500/503) and could be hostile?",
    "Which process activities (PROCESS_ACTIVITY) look suspicious?",
    "Which sessions show very short-lived or unusual event sequences?",
    "Which user IDs appear with multiple IPs or device IDs (possible credential sharing or compromise)?",
    "Which events returned HTTP 422 and could indicate probing or malformed attack payloads?",
    "Which users performed updates (PATCH/PUT) that changed sensitive fields?",
    "What is the overall security posture of this window - normal, suspicious, or an incident? Explain.",
    "How many login (LOGIN) events succeeded in this window, and which users logged in?",
    "How many unauthenticated events (user_id empty) exist in this window, and what actions did they involve?",
    "Which endpoints were accessed with the DELETE method, and who performed them?",
    "Which users accessed /api/admin or internal endpoints?",
    "What is the average response time in this window, and which endpoints are the slowest?",
    "Which events have unusually high response times, and could they indicate scanning or heavy exports?",
    "How many unique IPs appear in this window, and which users share an IP?",
    "Which sessions lasted the longest, and what did they do?",
    "Which sessions performed actions across many different resources?",
    "How many unique sessions are in this window, and how does that compare to unique users?",
    "Which events have no session id (system-level activity)?",
    "Which events used the SYSTEM method, and what did they do?",
    "Which users uploaded documents (UPLOAD_DOCUMENT), and were any uploads unusual in size or timing?",
    "Which downloads (DOWNLOAD_DOCUMENT) occurred, and could any of them be data exfiltration?",
    "Which events reference file paths in metadata, and are any of them sensitive (system files, config)?",
    "Which events reference hashes in metadata, and which files are involved?",
    "Which outbound connections used uncommon ports, and to which destinations?",
    "Which process activities modified system files or network configuration?",
    "Which users accessed the API resource the most, and is that expected for them?",
    "Which users accessed the NETWORK resource, and what did they do?",
    "Which users accessed SYSTEM_FILE resources, and could it indicate tampering?",
    "Which events changed settings (UPDATE_SETTINGS), and were any security-related?",
    "Which metadata contains settings_changed, and are any security settings being weakened?",
    "Which users changed profile fields (fields_changed), and does any change look suspicious?",
    "Which events show a user operating from multiple locations?",
    "Which events show a user switching devices?",
    "Which users appear to be active at unusual hours in this window?",
    "What time range does this window cover, and is there activity clustering at night?",
    "Which minutes in this window had the highest event volume (burst detection)?",
    "Are there any bursts of many events from a single IP in this window?",
    "Which IP has the most events in this window, and is that normal?",
    "Which endpoint received the most 401 responses?",
    "Which endpoint received the most 429 responses?",
    "Which endpoint returned 500/503 the most, and could it be under attack?",
    "Are there any events pointing to undocumented or unusual endpoints?",
    "Which API endpoints were accessed with an unexpected HTTP method?",
    "How many events reference the /api/login endpoint, and what is the success/failure ratio?",
    "Which users have the most failed login attempts before a successful login?",
    "Which events have status_code 304, and are they related to caching only?",
    "How many 404 responses exist in this window, and could they be directory scanning?",
    "Which endpoints returned 404, and do they look like probing attempts?",
    "Which user agents appear in this window, and are any unusual or non-browser?",
    "Are there any automated or script user agents that could indicate bot activity?",
    "Which sessions use multiple user agents?",
    "Which users have response times that suddenly degrade?",
    "Which resources were accessed the most, and is the distribution suspicious?",
    "Which users accessed resources they have never touched before in this window?",
    "How many unique actions occur in this window, and which actions dominate?",
    "Are there any actions that appear out of the ordinary for the user performing them?",
    "Which events contain locations in metadata, and does any location mismatch the user's usual pattern?",
    "Which events contain device_id in metadata, and which users use multiple devices?",
    "Which metadata shows document file operations, and are they sensitive?",
    "Which events show records or fields in metadata (bulk operations), and how large are they?",
    "Which export events have high record counts that could be exfiltration?",
    "Are there any events where a user exported data and then deleted records?",
    "Which events show failed exports or downloads?",
    "Which users attempted to access a resource they were denied (401 or 404)?",
    "How many distinct endpoint-user combinations exist, and which pairs are repeated?",
    "Which users access /api/users endpoints, and are they doing so in bulk (enumeration)?",
    "Which IPs access multiple different user accounts?",
    "Which sessions contain both login success and login failure events?",
    "Are there sessions that start with failures and then succeed (password guessing)?",
    "Which events show a user being locked or rate-limited (429)?",
    "Which users were rate-limited and kept trying anyway?",
    "Which events have both high response time and 500 status (degradation plus errors)?",
    "Which users generated the most errors overall in this window?",
    "Which IPs are external (198.51.100.x or 203.0.113.x) and what did they do?",
    "Are there any external IPs accessing sensitive endpoints?",
    "Which events involve the DOCUMENT resource and could leak sensitive data?",
    "Which events involve the AUTHENTICATION resource other than login?",
    "Which users accessed /api/internal/process or other internal endpoints?",
    "Which events reference process names in metadata, and are any unusual?",
    "How many events reference the event field in process metadata, and what system events occurred?",
    "Which events show configuration key changes (key, old_value, new_value), and which keys are security-relevant?",
    "Which users performed configuration changes, and what did they change?",
    "Which events in this window would you flag as requiring immediate investigation?",
    "Which users should be put under watch based on this window's activity?",
    "What is the attack surface exposed in this window (external IPs, unusual endpoints, errors)?",
    "Which events indicate potential insider threat behaviour (off-hours activity, mass access, exports)?",
    "Which events could indicate reconnaissance (scanning, enumeration, probing)?",
    "Which events could indicate lateral movement between resources?",
    "Summarise the top 5 findings in this window and their recommended remediations.",
]


def format_window(events):
    lines = []
    for e in events:
        meta = str(e.metadata or "")[:160]
        sess = str(e.session_id or "")[:12]
        user_id = e.user_id
        if user_id is None:
            user_id = ""
        elif float(user_id).is_integer():
            user_id = str(int(user_id))
        else:
            user_id = str(user_id)
        lines.append(
            f"{e.id}|{e.created_at}|u={user_id}|{e.action}|"
            f"{e.method}|{e.endpoint}|ip={e.ip_address}|"
            f"sess={sess}|status={e.status_code}|ms={e.response_time_ms}|{meta}"
        )
    return "\n".join(lines)


DATABASE_SCHEMA = """
AUDIT TRAIL SCHEMA (the table being monitored is `audit_trail`, one row per event):

Columns:
  - id               : unique event ID (1, 2, 3, ...)
  - user_id          : synthetic application user ID (1-30); empty = unauthenticated activity
  - action           : what happened (e.g. LOGIN, LOGIN_FAILED, VIEW_USER, VIEW_DOCUMENT,
                       VIEW_PROFILE, VIEW_SETTINGS, DOWNLOAD_DOCUMENT, UPLOAD_DOCUMENT,
                       FILE_ACCESS, EXPORT_DATA, UPDATE_USER, UPDATE_PROFILE,
                       UPDATE_SETTINGS, UPDATE_CONFIG, SEARCH, API_REQUEST,
                       OUTBOUND_CONNECTION, PROCESS_ACTIVITY, etc.)
  - resource         : the resource involved (e.g. AUTHENTICATION, USER, DOCUMENT,
                       SYSTEM_FILE, NETWORK, API, USER_PROFILE)
  - method           : HTTP method (GET/POST/PUT/PATCH/DELETE) or SYSTEM for internal activity
  - endpoint         : the API endpoint (e.g. /api/login, /api/users/42)
  - ip_address       : source IP (private 10.x / 192.168.x or documentation ranges)
  - user_agent       : browser/device/process identifier
  - session_id       : events in one user session share this id
  - status_code      : HTTP status (200, 201, 204, 304, 401, 404, 422, 429, 500, 503)
  - response_time_ms : response time in milliseconds
  - metadata         : JSON string with extra evidence (device, location, file, hashes,
                       destination, records, fields, settings_changed, normal_activity flag)
  - created_at       : event timestamp (YYYY-MM-DD HH:MM:SS, UTC)

Normal events carry "normal_activity": true inside their metadata JSON. Events that are
merely unusual do NOT carry that flag - the absence is itself a signal. There are NO
labels or verdicts in the data: all meaning must be inferred from the event sequence,
volume, timing, and metadata.
"""


def ask_about_window(question, events):
    window_text = format_window(events)
    prompt = f"""
You are a cybersecurity analyst monitoring the audit trail of an application.

{DATABASE_SCHEMA}

WINDOW OF {len(events)} AUDIT EVENTS UNDER REVIEW (piped fields: id|created_at|user_id|action|method|endpoint|ip_address|session_id|status_code|response_time_ms|metadata):
{window_text}

MONITOR QUESTION:
{question}

Analyse ONLY the events in the window above. Respond with:
- A concise factual answer to the question, using the exact values present in the window.
- The specific user IDs, IPs, sessions, or endpoints involved, if any.
- A risk assessment for this window on this question: Normal, Suspicious, or Incident.
- Recommended next actions, if any.

Do not invent events, numbers, or values that are not present in the window.
"""
    return gemini_service.generate_content(prompt)


class Command(BaseCommand):
    help = "Run one AI monitor cycle over the next audit_trail window."

    def handle(self, *args, **options):
        try:
            self.run_monitor()
        except Exception as e:
            logger.error(traceback.format_exc())
            self.stderr.write(f"AI monitor failed: {e}")
            raise SystemExit(1)

    def run_monitor(self):
        if not settings.GEMINI_API_KEY:
            self.stderr.write(
                "GEMINI_API_KEY not set. Set the GEMINI_API_KEY environment "
                "variable before running the AI monitor."
            )
            return

        REPORT_DIR.mkdir(parents=True, exist_ok=True)

        last_audit_id = int(services.get_state_value("last_audit_id", 0) or 0)
        question_index = int(services.get_state_value("question_index", 0) or 0)

        events = list(
            services.get_audit_window(after_id=last_audit_id, limit=AUDIT_WINDOW_SIZE)
        )
        if not events:
            # end of the audit reached - wrap around to simulate ongoing monitoring
            events = list(
                services.get_audit_window(after_id=0, limit=AUDIT_WINDOW_SIZE)
            )

        if not events:
            self.stdout.write("Audit trail is empty. Nothing to monitor.")
            return

        window_start = events[0].id
        window_end = events[-1].id

        questions = [
            MONITOR_QUESTIONS[(question_index + i) % len(MONITOR_QUESTIONS)]
            for i in range(QUESTIONS_PER_RUN)
        ]
        new_question_index = (question_index + QUESTIONS_PER_RUN) % len(MONITOR_QUESTIONS)

        run_time = datetime.now()
        run_id = f"{run_time.strftime('%Y-%m-%d_%H-%M-%S')}_W{window_start}-{window_end}"
        header = (
            f"\n{'=' * 70}\nAI Monitor run {run_id} "
            f"(events {window_start} to {window_end}, {len(events)} rows)\n{'=' * 70}"
        )

        with open(RUN_LOG, "a", encoding="utf-8") as log:
            log.write(header + "\n")
            if VERBOSE:
                log.write("WINDOW:\n" + format_window(events) + "\n")

            for question in questions:
                log.write(f"\n--- QUESTION: {question}\n")
                try:
                    answer = ask_about_window(question, events)
                    if answer is None:
                        answer = "AI assistant could not produce an answer. Please check the Gemini API key and quota."
                    log.write("ANSWER:\n" + answer + "\n")
                    services.add_analytical_report(run_id, question, answer)
                except Exception as e:
                    logger.error(traceback.format_exc())
                    log.write(f"ERROR: {e}\n")
                time.sleep(SLEEP_BETWEEN_QUESTIONS)

        services.set_state_value("last_audit_id", window_end)
        services.set_state_value("question_index", new_question_index)

        self.stdout.write(
            f"AI monitor finished. Analysed events {window_start}-{window_end} "
            f"({len(events)} rows). Results appended to {RUN_LOG}"
        )
