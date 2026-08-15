# Cyber Intelligence Platform

## Introduction

The Cyber Intelligence Platform is a web-based application developed using **Python** and **Streamlit**. It provides an integrated environment for managing cybersecurity incidents, dataset metadata, IT support tickets, and user accounts while incorporating an AI assistant powered by the **Google Gemini API**.

Beyond the interactive UI, the platform includes an **automated AI monitoring subsystem** (headless) that continuously analyses an external application's audit trail, surfaces cyber issues, stores the resulting analytical reports, and delivers them to the dashboard in near real time.

The platform demonstrates secure authentication, database management, interactive dashboards, role-based access control, AI-assisted querying of organisational data, and scheduled autonomous monitoring.

---

## Features

### Core Platform
- Secure user authentication using bcrypt password hashing
- Role-based access control for administrators
- Cybersecurity incident management
- Dataset metadata management
- IT ticket management
- Interactive dashboards and data visualisation
- AI assistant capable of answering questions using organisational data
- SQLite database integration
- Modular application architecture

### Automated AI Monitoring (Sentinel Audit Intelligence)
- **External audit trail ingestion** — imports the monitored application's audit log (Sentinel `sentinel_monitoring.db`, 30,000+ events) into the platform database
- **Window-based analysis** — the audit is consumed in sliding 100-row windows, one window per scheduled run, simulating near-real-time monitoring of the external system
- **Large monitoring question pool** — 100+ rotating questions covering the key cyber areas: brute force, data exfiltration, privilege escalation, unauthorised access, malware/ransomware indicators, insider threat, reconnaissance, and overall security posture
- **Risk assessment** — every answer includes a severity verdict (Normal / Suspicious / Incident) plus recommended actions
- **Analytical report storage** — each run's question/answer pairs are persisted in the `analytical_reports` table
- **Scheduled execution** — a Windows Task Scheduler job (`CyberOps_AIMonitor`) triggers the monitor every minute
- **Live report dashboard** — a dedicated page queries the reports table and auto-refreshes, so new analysis appears as soon as it is generated
- **Graceful degradation** — API rate limits and outages are logged and skipped without breaking the pipeline

---

## Technologies Used

- Python 3
- Streamlit
- SQLite
- Pandas
- bcrypt
- Google Gemini API (gemini-2.5-flash)
- reportlab (PDF reporting)
- Windows Task Scheduler (automation)

---

## Architectural Design

### High-Level Architecture

```
                         ┌────────────────────────────────────────────┐
                         │         EXTERNAL MONITORED SYSTEM          │
                         │        (Sentinel – fictional app)          │
                         │     sentinel_monitoring.db                 │
                         │     Table: audit_trails (30k+ events)      │
                         └──────────────────┬─────────────────────────┘
                                            │ imported on first run
                                            ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                         PYTHON / STREAMLIT PLATFORM                        │
│                                                                            │
│  ┌────────────────────┐    ┌───────────────────────────────────────────┐   │
│  │  Streamlit UI      │    │  AI Monitor (ai_monitor.py – headless)    │   │
│  │  (pages/*)         │    │                                          │   │
│  │  Home / Dashboard  │    │ 1. Next 100-row audit window             │   │
│  │  AI Assistant      │    │ 2. Rotating questions (100+ pool)        │   │
│  │  Analysis Reports  │    │ 3. Gemini analyses the window            │   │
│  │  Profile / Admin   │    │ 4. Save Q&A to analytical_reports        │   │
│  └────────┬───────────┘    └───────────────┬───────────────────────────┘   │
│           │                                │  scheduled every 1 min       │
│           │                                │  (Task Scheduler job)         │
│           ▼                                ▼                              │
│  ┌─────────────────────────── SQLite (DATA/project_data.db) ──────────┐   │
│  │ users · cyber_incidents · datasets_metadata · it_tickets           │   │
│  │ audit_trail · analytical_reports · ai_monitor_state                │   │
│  └────────────────────────────────────────────────────────────────────┘   │
│                                                                            │
│  Gemini API (text-to-SQL + analytical explanations, via st.secrets)        │
└────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow (Automated Monitoring Cycle)

```
[1 min timer]
     │
     ▼
Read scan cursor (ai_monitor_state.last_audit_id)
     │
     ▼
Fetch next 100 audit events (audit_trail WHERE id > last_id ORDER BY id LIMIT 100)
     │  (wraps to id=0 when the whole log has been scanned)
     ▼
Pick next 3 questions from the 100+ question pool (rotating)
     │
     ▼
For each question: build prompt = schema + 100-event window + question
     │
     ▼
Gemini analyses the window → answer with risk verdict + recommendations
     │
     ▼
Insert (run_id, question, answer) into analytical_reports
     │
     ▼
Advance cursor → next run starts at event 101, 201, ...
     │
     ▼
Analysis Reports page (auto-refreshes every 10 s) displays the latest run
```

### Layered Design

| Layer | Components | Responsibility |
|---|---|---|
| Presentation | `Home.py`, `pages/*` | Streamlit UI: dashboards, assistant, reports, admin |
| Application / Automation | `ai_monitor.py`, `setup_ai_monitor_scheduler.ps1` | Headless monitoring loop + scheduler registration |
| Domain / Model | `app_model/*` | Data access and business logic for every table |
| Agent (optional) | `agent_v2/*` | Tool-based Cyber Intelligence Agent (read tools + pending admin actions) |
| Infrastructure | `DATA/project_data.db`, `.streamlit/secrets.toml`, `configpath.py` | Persistence, secrets, central path configuration |

---

## Project Structure

```
CW2_M01119174_CST1510/
│
├── app_model/
│   ├── audit_trail.py        # Sentinel audit import + window queries
│   ├── cyber_incidents.py
│   ├── db.py                 # SQLite connection
│   ├── it_tickets.py
│   ├── metadata.py
│   ├── reports.py            # analytical_reports store/retrieve
│   ├── schema.py             # table creation (users, analytical_reports)
│   └── users.py
│
├── agent_v2/                 # optional tool-based agent
│   ├── agent.py, investigation.py, monitoring.py, memory.py,
│   ├── reporting.py, tool_registry.py
│   └── tools/                # analytics/incident/ticket/metadata/action tools
│
├── pages/
│   ├── 1_Dashboard.py
│   ├── 2_AI_Assistant.py
│   ├── 3_PROFILE.py
│   ├── 4_Cyber_Agent.py
│   ├── 5_ADMIN_MANAGEMENT.py
│   └── 6_Analysis_Reports.py # live view of AI monitor output
│
├── DATA/
│   ├── project_data.db       # SQLite database (all tables)
│   ├── users.txt
│   ├── cyber_incidents.csv
│   ├── datasets_metadata.csv
│   ├── it_tickets.csv
│   └── audit_trail.csv
│
├── reports/
│   ├── ai_monitor.log        # rolling log of every monitor run
│   └── cyber_ops_report_*.pdf
│
├── .streamlit/
│   └── secrets.toml          # GEMINI_API_KEY (gitignored)
│
├── ai_monitor.py             # headless AI analysis runner
├── setup_ai_monitor_scheduler.ps1
├── configpath.py             # central path configuration
├── hashing.py
├── Home.py
├── main.py                   # CLI entry point + DB setup/migrations
├── test_tools.py
├── text_gemini.py
└── requirements.txt
```

---

## Database Design

The SQLite database (`DATA/project_data.db`) contains the following tables.

### users
Stores registered user accounts.
- `id` (PK, auto-increment)
- `username` (unique)
- `password_hash`
- `role` (`user` / `admin`)

### cyber_incidents
Stores cybersecurity incident records.
- `incident_id` (PK)
- `timestamp`
- `severity` (Low / Medium / High / Critical)
- `category`
- `status` (Open / Resolved / Closed)
- `description`

### datasets_metadata
Stores metadata describing uploaded datasets.
- `dataset_id` (PK)
- `name`
- `rows`
- `columns`
- `uploaded_by`
- `upload_date`

### it_tickets
Stores IT support ticket information.
- `ticket_id` (PK)
- `priority` (High / Medium / Low)
- `description`
- `status` (Open / Resolved / Closed)
- `assigned_to`
- `created_at`
- `resolution_time_hours`

### audit_trail
Mirror of the external (Sentinel) monitored system's audit log. Imported from `sentinel_monitoring.db`. **Contains no labels** — meaning is inferred by the AI from event sequences, volume, timing, and the JSON `metadata`.
- `id` (PK)
- `user_id` (1–30, empty = unauthenticated)
- `action` (e.g. LOGIN, LOGIN_FAILED, VIEW_DOCUMENT, EXPORT_DATA, FILE_ACCESS, OUTBOUND_CONNECTION, PROCESS_ACTIVITY, UPDATE_CONFIG)
- `resource` (AUTHENTICATION, USER, DOCUMENT, SYSTEM_FILE, NETWORK, API, ...)
- `method` (GET / POST / PUT / PATCH / DELETE / SYSTEM)
- `endpoint` (e.g. /api/login)
- `ip_address`
- `user_agent`
- `session_id`
- `status_code` (200/201/401/404/422/429/500/503/...)
- `response_time_ms`
- `metadata` (JSON: device, location, file, hashes, destination, records, normal_activity flag)
- `created_at`

### analytical_reports
Output table of the AI monitor. Every scheduled run inserts one row per answered question.
- `id` (PK, auto-increment)
- `run_id` (timestamp + window, e.g. `2026-08-15_14-52-31_W1-100`)
- `question`
- `answer`
- `created_at`

### ai_monitor_state
Persists the monitor's scan cursor so runs are resumable.
- `key` (PK) — `last_audit_id`, `question_index`
- `value`

---

## Automated AI Monitoring Design

### How the monitor works
1. The scheduled task (`CyberOps_AIMonitor`, every 1 minute) launches `ai_monitor.py` using the project virtual environment.
2. The script reads the scan cursor, fetches the **next 100 audit events** from `audit_trail`.
3. It picks the **next 3 questions** from a rotating pool of **100+ monitoring questions**.
4. Each question is sent to Gemini together with the 100-event window. Gemini:
   - answers the question using only the events in the window,
   - names the users, IPs, sessions, and endpoints involved,
   - gives a risk verdict (**Normal / Suspicious / Incident**),
   - recommends next actions.
5. The question/answer pair is stored in `analytical_reports` and appended to `reports/ai_monitor.log`.
6. The cursor advances. When the end of the audit is reached, it wraps to the beginning, simulating continuous monitoring.

### Tuning
The monitor is configurable through environment variables:

| Variable | Default | Meaning |
|---|---|---|
| `AUDIT_WINDOW_SIZE` | `100` | Audit events analysed per run |
| `QUESTIONS_PER_RUN` | `3` | Questions asked per run (rotating) |
| `SLEEP_BETWEEN_QUESTIONS` | `3` | Seconds between Gemini calls (rate-limit protection) |
| `AI_MONITOR_VERBOSE` | `0` | Set to `1` to log the raw window |

### Scheduler
`setup_ai_monitor_scheduler.ps1` registers the Windows Task Scheduler job:

```
powershell -ExecutionPolicy Bypass -File .\setup_ai_monitor_scheduler.ps1
```

Useful commands:

```
schtasks /Query /TN "CyberOps_AIMonitor"            # check status
schtasks /End /TN "CyberOps_AIMonitor"              # stop current run
schtasks /Change /TN "CyberOps_AIMonitor" /DISABLE  # pause scheduling
schtasks /Change /TN "CyberOps_AIMonitor" /ENABLE   # resume scheduling
schtasks /Delete /TN "CyberOps_AIMonitor" /F        # remove the task
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/anel-andrew/CW2_M01119174_CST1510.git
cd CW2_M01119174_CST1510
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment:

- Windows (PowerShell): `.venv\Scripts\Activate.ps1`
- macOS/Linux: `source .venv/bin/activate`

Install the required packages:

```bash
pip install -r requirements.txt streamlit pandas google-genai
```

> `google-genai` is required by the AI features. `vnv` and `virtualenv` are optional helper tools for environment management.

---

## Configuration

### Gemini API Key
Create the file `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "YOUR_API_KEY"
```

Do **not** commit this file to GitHub (it is gitignored). The AI monitor can alternatively read the key from the `GEMINI_API_KEY` environment variable.

### Sentinel Audit Database (optional)
The `audit_trail` table is populated automatically from `C:\Users\poka\Downloads\sentinel\sentinel_monitoring.db` (path defined in `configpath.py`). If the file is present, the monitor imports all audit events on first run.

---

## Running the Application

Launch the Streamlit application:

```bash
streamlit run Home.py
```

or with the venv interpreter:

```bash
.\.venv\Scripts\streamlit run Home.py
```

The application opens automatically in your default web browser.

---

## Application Pages

| Page | Purpose |
|---|---|
| Home | Login / Register |
| Dashboard | Analytics for cyber incidents, IT tickets, and dataset metadata |
| AI Assistant | Chat interface that converts natural-language questions into SQL, runs them, and explains results (Gemini) |
| Analysis Reports | Live view of the AI monitor's latest reports (auto-refreshes every 10 s) |
| Profile | User account management |
| Cyber Agent | Tool-based agent with read tools and admin-confirmed write actions |
| Admin Management | Admin-only user and data management |

---

## Register yourself as user
- enter your username of choice
- enter your password of choice (Password must be at least 8 characters long and include an uppercase letter, a lowercase letter, a number, and a special character.)
- click the register button

## User Login
- enter your username
- enter your password

---

## Administrator Access

Only users with the **admin** role can access the Administrator Management page.

Admin username : Manager
Admin password : Admin1!Admin1!

Administrators can:

- Promote users
- Demote users
- Reset user passwords
- Delete users
- Add cyber incidents
- Delete cyber incidents
- Add dataset metadata
- Delete dataset metadata
- Add IT tickets
- Delete IT tickets

---

## AI Assistant

The AI Assistant uses the Google Gemini API.

When a user submits a question:

1. Gemini determines whether the question requires database access.
2. If required, Gemini generates a SQLite SQL query.
3. Python executes the SQL query.
4. The database returns the results.
5. Gemini explains the results in natural language.

This approach ensures calculations are performed by SQLite rather than by the language model.

---

## Security

The platform incorporates several security mechanisms:

- Passwords are hashed using bcrypt.
- API keys are stored securely using Streamlit Secrets.
- Parameterised SQL queries reduce SQL injection risks.
- Session State maintains authenticated user sessions.
- Role-based authorisation protects administrator functions.
- The AI monitor runs headless and only reads data; it never executes write actions automatically.
- All Gemini failures are logged to `gemini_errors.log` without exposing credentials.

---

## Author

Anel Andrew Temu

BSc Computer Science (Systems Engineering)

Middlesex University Mauritius

---

## Licence

This project was developed for academic coursework purposes.
