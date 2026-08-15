# Cyber Intelligence Platform

## Introduction

The Cyber Intelligence Platform is a web-based application developed using
**Python**, **Django** and **PostgreSQL**. It provides an integrated environment
for managing cybersecurity incidents, dataset metadata, IT support tickets, and
user accounts while incorporating an AI assistant powered by the **Google
Gemini API**.

Beyond the interactive UI, the platform includes an **automated AI monitoring
subsystem** (headless) that continuously analyses an external application's
audit trail, surfaces cyber issues, stores the resulting analytical reports, and
delivers them to the dashboard in near real time.

The platform demonstrates secure authentication, database normalisation and
integrity constraints, interactive dashboards, role-based access control,
AI-assisted querying of organisational data, and scheduled autonomous
monitoring.

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
- PostgreSQL database with normalised tables, CHECK constraints and indexes
- Modular feature-based architecture

### Automated AI Monitoring (Sentinel Audit Intelligence)
- **Audit trail analysis** — continuously analyses the monitored application's
  audit log (30,000+ events) held in the `audit_trail` table
- **Window-based analysis** — the audit is consumed in sliding 100-row windows,
  one window per scheduled run, simulating near-real-time monitoring of the
  external system
- **Large monitoring question pool** — 100+ rotating questions covering the key
  cyber areas: brute force, data exfiltration, privilege escalation,
  unauthorised access, malware/ransomware indicators, insider threat,
  reconnaissance, and overall security posture
- **Risk assessment** — every answer includes a severity verdict (Normal /
  Suspicious / Incident) plus recommended actions
- **Analytical report storage** — each run's question/answer pairs are persisted
  in the `analytical_reports` table
- **Scheduled execution** — a Windows Task Scheduler job triggers the monitor
  every minute (`python manage.py run_ai_monitor`)
- **Live report dashboard** — a dedicated page queries the reports table and
  auto-refreshes, so new analysis appears as soon as it is generated
- **Graceful degradation** — API rate limits and outages are logged and skipped
  without breaking the pipeline

---

## Technologies Used

- Python 3
- Django 6
- PostgreSQL 18
- bcrypt
- Google Gemini API (gemini-2.5-flash)
- psycopg 3 (PostgreSQL driver)
- reportlab (PDF reporting)
- Bootstrap / ECharts (front end)
- Windows Task Scheduler (automation)

---

## Architectural Design

### High-Level Architecture

```
                    ┌────────────────────────────────────────────┐
                    │       EXTERNAL MONITORED SYSTEM           │
                    │        (Sentinel – fictional app)         │
                    │   audit log mirrored into audit_trail     │
                    └───────────────────┬────────────────────────┘
                                        │ analysed in sliding 100-row windows
                                        ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                         PYTHON / DJANGO PLATFORM                          │
│                                                                           │
│  ┌─────────────────────┐     ┌────────────────────────────────────────┐   │
│  │  Django web app     │     │  AI Monitor (manage.py run_ai_monitor) │   │
│  │  cyber/features/*   │     │  headless – scheduled every 1 min      │   │
│  │  dashboard          │     │  1. Next 100-row audit window          │   │
│  │  ai_assistant       │     │  2. Rotating questions (100+ pool)     │   │
│  │  analysis_reports   │     │  3. Gemini analyses the window         │   │
│  │  profile / admin    │     │  4. Save Q&A to analytical_reports     │   │
│  │  cyber_agent        │     └─────────────────┬──────────────────────┘   │
│  └─────────┬───────────┘                       │                          │
│            │                                   │                          │
│            ▼                                   ▼                          │
│  ┌─────────────────────────── PostgreSQL (cyber_intel) ─────────────────┐   │
│  │ users · cyber_incidents · datasets_metadata · it_tickets            │   │
│  │ audit_trail · analytical_reports · ai_monitor_state                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  Gemini API (text-to-SQL + analytical explanations, via .env GEMINI_API_KEY)│
└───────────────────────────────────────────────────────────────────────────┘
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
| Presentation | `templates/`, `cyber/features/*/view.html`, `static/` | Django templates: dashboards, assistant, reports, admin |
| Web controllers | `cyber/features/*/index.py`, `cyber/urls.py` | Request routing, auth, session handling |
| Application / Automation | `cyber/management/commands/run_ai_monitor.py` | Headless monitoring loop |
| Agent | `cyber/agent/*` | Tool-based Cyber Intelligence Agent (read tools + pending admin actions) |
| Domain / Model | `cyber/models.py`, `cyber/services.py` | ORM models, data access, business logic |
| Infrastructure | `config/settings.py`, `.env`, PostgreSQL | Settings, secrets, persistence |

---

## Project Structure

```
CW2_M01119174_CST1510/
│
├── manage.py                        # Django CLI entry point
│
├── config/                          # Project configuration package
│   ├── settings.py                  #   settings + built-in .env loader
│   ├── urls.py                      #   root URL configuration
│   ├── wsgi.py                      #   WSGI entry point
│   ├── asgi.py                      #   ASGI entry point
│   └── __init__.py
│
├── cyber/                           # Main application package
│   ├── admin.py                     #   Django admin registration
│   ├── apps.py                      #   app configuration
│   ├── decorators.py                #   @login_required_custom / @admin_required
│   ├── gemini_service.py            #   Google Gemini provider wrapper
│   ├── models.py                    #   7 normalised ORM models
│   ├── services.py                  #   data access + business logic
│   ├── tests.py
│   ├── urls.py                      #   application routes
│   ├── validators.py                #   custom password validator
│   ├── migrations/                  #   database schema migrations
│   │   └── 0001_initial.py
│   ├── management/
│   │   └── commands/
│   │       └── run_ai_monitor.py    #   headless AI monitoring runner
│   ├── agent/                       #   tool-based Cyber Intelligence Agent
│   │   ├── agent.py
│   │   ├── investigation.py
│   │   ├── monitoring.py
│   │   ├── reporting.py             #     PDF generation (reportlab)
│   │   ├── tool_registry.py
│   │   ├── tools.py
│   │   └── __init__.py
│   └── features/                    #   one folder per page
│       ├── auth/                    #     login / register / logout
│       │   ├── index.py
│       │   └── __init__.py
│       │
│       ├── dashboard/               #     analytics dashboard
│       │   ├── index.py             #       controller
│       │   ├── view.py              #       page data
│       │   ├── view.html            #       template
│       │   ├── _js_index.py         #       inline JS source
│       │   ├── js_view.py           #       inline JS builder
│       │   └── __init__.py
│       │
│       ├── ai_assistant/            #     text-to-SQL assistant
│       │   ├── index.py
│       │   ├── view.py
│       │   ├── view.html
│       │   ├── _js_index.py
│       │   ├── js_view.py
│       │   └── __init__.py
│       │
│       ├── analysis_reports/        #     live AI monitor reports
│       │   ├── index.py  view.py  view.html
│       │   ├── _js_index.py  js_view.py  __init__.py
│       │
│       ├── cyber_agent/             #     tool-based agent UI + PDF download
│       │   ├── index.py  view.py  view.html
│       │   ├── _js_index.py  js_view.py  __init__.py
│       │
│       ├── profile/                 #     user profile
│       │   ├── index.py  view.py  view.html
│       │   ├── _js_index.py  js_view.py  __init__.py
│       │
│       └── admin_management/        #     admin-only user/data management
│           ├── index.py  view.py  view.html
│           ├── _js_index.py  js_view.py  __init__.py
│
├── templates/                       # Django templates
│   ├── base.html                    #   base layout (sidebar + topbar + content)
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   └── partials/                    #   reusable layout partials
│       ├── sidebar.html
│       ├── topbar.html
│       ├── breadcrumb.html
│       └── footer.html
│
├── static/                          # Static assets (Limitless Bootstrap theme)
│   └── assets/
│       ├── css/                     #   app.js, custom.js, animate.min.css
│       ├── js/                      #   application + vendor scripts
│       ├── scss/                    #   Bootstrap / theme stylesheets
│       ├── fonts/                   #   icon and web fonts
│       ├── icons/                   #   icon libraries
│       ├── images/                  #   images / demo assets
│       └── demo/                    #   demo data
│
├── reports/                         # Generated PDFs + monitor log (gitignored)
├── requirements.txt
├── .env.example                     # Template for the git-ignored .env file
└── .gitignore
```

> `.git/`, `.venv/` and `__pycache__/` are omitted for brevity. Each page folder
> (`cyber/features/*`) follows the same pattern: `index.py` (controller),
> `view.py` (data preparation), `view.html` (template), and
> `js_view.py`/`_js_index.py` (inline JavaScript).

---

## Database Design

The platform runs on a **PostgreSQL** database named `cyber_intel`. The schema
is normalised: every table has a single primary key, appropriate column types,
NOT NULL where required, CHECK constraints to enforce valid enum values, and
indexes on frequently filtered/grouped columns. `audit_trail` deliberately has
no foreign key to `users` (its `user_id` refers to synthetic identities in the
source audit log).

### users
Stores registered user accounts.
- `id` (PK, auto-increment)
- `username` (unique)
- `password_hash`
- `role` (`user` / `admin` — CHECK constraint)

### cyber_incidents
Stores cybersecurity incident records.
- `incident_id` (PK)
- `timestamp`
- `severity` (Low / Medium / High / Critical — CHECK constraint)
- `category`
- `status` (Open / In Progress / Resolved / Closed — CHECK constraint)
- `description`
- `created_at`
- Indexes on `severity`, `status`, `category`

### datasets_metadata
Stores metadata describing uploaded datasets.
- `dataset_id` (PK)
- `name`
- `row_count` (non-negative — CHECK constraint)
- `column_count` (non-negative — CHECK constraint)
- `uploaded_by`
- `upload_date`
- `created_at`
- Index on `uploaded_by`

### it_tickets
Stores IT support ticket information.
- `ticket_id` (PK)
- `priority` (Low / Medium / High / Critical — CHECK constraint)
- `description`
- `status` (Open / In Progress / Resolved / Closed / Waiting for User — CHECK constraint)
- `assigned_to`
- `created_at`
- `resolution_time_hours` (integer, nullable, >= 0 — CHECK constraint)
- Indexes on `priority`, `status`, `assigned_to`

### audit_trail
Mirror of the external (Sentinel) monitored system's audit log. **Contains no
labels** — meaning is inferred by the AI from event sequences, volume, timing,
and the JSON metadata.
- `id` (PK)
- `user_id` (1–30, empty = unauthenticated; no FK by design)
- `action` (e.g. LOGIN, LOGIN_FAILED, VIEW_DOCUMENT, EXPORT_DATA, FILE_ACCESS, OUTBOUND_CONNECTION, PROCESS_ACTIVITY, UPDATE_CONFIG)
- `resource` (AUTHENTICATION, USER, DOCUMENT, SYSTEM_FILE, NETWORK, API, ...)
- `method` (GET / POST / PUT / PATCH / DELETE / SYSTEM)
- `endpoint` (e.g. /api/login)
- `ip_address`
- `user_agent`
- `session_id`
- `status_code` (200/201/401/404/422/429/500/503/...)
- `response_time_ms`
- `metadata` (JSONB: device, location, file, hashes, destination, records, normal_activity flag)
- `created_at`
- Indexes on `user_id`, `action`, `created_at`, `session_id`

### analytical_reports
Output table of the AI monitor. Every scheduled run inserts one row per answered question.
- `id` (PK, auto-increment)
- `run_id` (timestamp + window, e.g. `2026-08-15_14-52-31_W1-100`)
- `question`
- `answer`
- `created_at`
- Index on `run_id`

### ai_monitor_state
Persists the monitor's scan cursor so runs are resumable.
- `key` (PK) — `last_audit_id`, `question_index`
- `value`
- `updated_at`

---

## Automated AI Monitoring Design

### How the monitor works
1. The scheduled task (`CyberOps_AIMonitor`, every 1 minute) runs `python manage.py run_ai_monitor` using the project virtual environment.
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

### Running manually
```
.\.venv\Scripts\python.exe manage.py run_ai_monitor
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/anel-andrew/CW2_M01119174_CST1510.git
cd CW2_M01119174_CST1510
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

- Windows (PowerShell): `.venv\Scripts\Activate.ps1`
- macOS/Linux: `source .venv/bin/activate`

Install the required packages:

```bash
pip install -r requirements.txt
```

---

## Configuration

### Configuration file (.env)
Create the file `.env` (git-ignored, copy from `.env.example`):

```
DJANGO_SECRET_KEY=<your-secret>
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost,testserver
GEMINI_API_KEY=<your-api-key>
POSTGRES_DB=cyber_intel
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<your-password>
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5545
```

Do **not** commit `.env` to GitHub (it is gitignored).

### Database setup
With the PostgreSQL server running, apply the schema migrations:

```bash
python manage.py migrate
```

The database is already populated with the full dataset (users, cyber
incidents, datasets, IT tickets, audit trail, and analytical reports).

---

## Running the Application

Launch the Django development server:

```bash
python manage.py runserver
```

Then open <http://127.0.0.1:8000/> in your browser. You are redirected to the
login page.

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
- Add dataset metadata
- Add IT tickets

---

## AI Assistant

The AI Assistant uses the Google Gemini API.

When a user submits a question:

1. Gemini determines whether the question requires database access.
2. If required, Gemini generates a PostgreSQL SQL query.
3. Python executes the SQL query against PostgreSQL.
4. The database returns the results.
5. Gemini explains the results in natural language.

This approach ensures calculations are performed by PostgreSQL rather than by the language model.

---

## Security

The platform incorporates several security mechanisms:

- Passwords are hashed using bcrypt.
- API keys and database credentials are stored in the git-ignored `.env` file.
- Parameterised SQL queries reduce SQL injection risks.
- Django sessions maintain authenticated user sessions.
- Role-based authorisation protects administrator functions.
- The AI monitor runs headless and only reads data; it never executes write actions automatically.
- All Gemini failures are logged to `gemini_errors.log` without exposing credentials.
- Database-level CHECK constraints enforce valid enum values at the source.

---

## Author

Anel Andrew Temu

BSc Computer Science (Systems Engineering)

Middlesex University Mauritius

---

## Licence

This project was developed for academic coursework purposes.
