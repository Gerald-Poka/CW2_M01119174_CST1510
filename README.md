# 🛡️ Cyber Intelligence Platform

> *AI-powered cybersecurity monitoring, incident management, and autonomous threat analysis*
>
> **Raised from the Agent Zero Hackathon — Built for the Real World**

---

## 🌟 Project Appreciation & Story

> *"A great project always starts with a great idea — and this one started with Anel Andrew."*

The **original concept** and **founding idea** behind this platform belongs to **Anel Andrew (her)**. What began as a vision — an intelligent, AI-driven cybersecurity platform — was brought to the competition group and became the seed of everything that followed.

From that idea, the team **fine-tuned the concept together** for the competition. **Gerald Ndyamukama** then took the lead on the **full architectural design and engineering** — refactoring and building the entire Django + PostgreSQL system from the ground up, aligning it with **real-world, industry-standard** software design. The architecture, the database schema, the agent loop, the monitoring subsystem, the modular feature design — all were architected and implemented by Gerald as part of an ambitious refactor and revamp.

This is **not an academic exercise**. This platform addresses **real-world cybersecurity problems** — autonomous threat detection, AI-assisted incident management, and agentic decision-making — and is built to the standards that real organisations require.

We celebrate and acknowledge:
- **Anel Andrew** — for the original idea and vision that started it all
- **The whole team** — for their collaborative input, fine-tuning, and competition spirit
- **Gerald Ndyamukama** — for the full-stack design, architecture, and engineering that brought it to life at world standard

---

## 👥 Contributors

| Name | Role |
|---|---|
| **Anel Andrew** | Original Idea & Concept · Project Co-founder |
| **Gerald Ndyamukama** | Lead Architect · Full-Stack · System Designer |
| **Anel Andres** | Group Contributor |
| **Grolia** | Group Contributor |
| **Passion** | Group Contributor |

We sincerely thank every contributor for their collaboration, ideas, and energy poured into this project.

---

## 🏆 Project Origin

This platform was **raised from the Agent Zero Hackathon Event** — a challenge to design systems where AI agents reason, act, and report autonomously. The group's collective ideas, fine-tuned through competition and then refactored into a world-class design, produced the Cyber Intelligence Platform.

> This is not an academic toy. It is a platform built to solve **real cybersecurity problems** at real-world scale.

---

## 📖 Introduction

The **Cyber Intelligence Platform** is a web-based cybersecurity management system built with **Python**, **Django 6**, and **PostgreSQL 18**. It provides an integrated environment for:

- Managing cybersecurity incidents, dataset metadata, and IT support tickets
- An **AI Assistant** powered by **Google Gemini** that converts natural-language questions into SQL and explains results
- A **Cyber Intelligence Agent** — a tool-based agentic system that reads live data and proposes write actions pending admin confirmation
- An **Automated AI Monitoring Subsystem** (headless) that continuously analyses an external application's 30,000+ event audit trail, surfaces threats, and stores analytical reports in near real-time

The platform showcases secure authentication, normalised database design with integrity constraints, interactive ECharts dashboards, role-based access control, AI-assisted querying, and scheduled autonomous monitoring — all in one cohesive, production-grade application.

---

## ✨ Features

### Core Platform

- 🔐 Secure user authentication using bcrypt password hashing
- 👤 Role-based access control (User / Admin)
- 🚨 Cybersecurity incident management
- 📊 Dataset metadata management
- 🎫 IT support ticket management
- 📈 Interactive dashboards with ECharts data visualisation
- 🤖 AI Assistant with conversational text-to-SQL querying (Google Gemini)
- 🗄️ PostgreSQL database with normalised tables, CHECK constraints, and indexes
- 📐 Modular feature-based architecture (one folder per page)

### Automated AI Monitoring — *Sentinel Audit Intelligence*

- 🔍 **Audit trail analysis** — continuously analyses a monitored application's audit log (30,000+ events) stored in the `audit_trail` table
- 🪟 **Sliding window analysis** — consumes the audit log in 100-row windows per scheduled run, simulating near-real-time monitoring
- ❓ **Large rotating question pool** — 100+ questions covering brute force, data exfiltration, privilege escalation, unauthorised access, malware/ransomware indicators, insider threat, reconnaissance, and overall security posture
- ⚠️ **Risk assessment** — every answer includes a severity verdict: **Normal / Suspicious / Incident**, plus recommended next actions
- 💾 **Analytical report storage** — each run's Q&A pairs are persisted to the `analytical_reports` table
- ⏱️ **Scheduled execution** — a Windows Task Scheduler job triggers the monitor every minute via `python manage.py run_ai_monitor`
- 📋 **Live report dashboard** — a dedicated page lists report runs and shows the latest answers as they are generated
- 🛡️ **Graceful degradation** — API rate limits and outages are logged and skipped without breaking the pipeline

### Cyber Intelligence Agent

- 🧠 **Tool-based agentic loop** — the agent reasons in steps, calling read tools and proposing write actions
- 📖 **Read-only by default** — the agent freely calls data tools (search incidents, query tickets, get statistics)
- ✋ **Admin-gated writes** — write actions (close incident, assign ticket, etc.) are stored as *pending actions* requiring admin confirmation before execution

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python 3 | Core language |
| Django 6.1 | Web framework |
| PostgreSQL 18 | Primary database |
| bcrypt 5.0 | Password hashing |
| Google Gemini API (`gemini-2.5-flash`) | AI reasoning, text-to-SQL, monitoring |
| psycopg 3 | PostgreSQL driver |
| ReportLab 5.0 | PDF generation (legacy module, preserved) |
| Bootstrap / ECharts | Front-end UI and charts |
| Windows Task Scheduler | Scheduled headless monitoring |

---

## 🏗️ Architectural Design

### High-Level Architecture

```
                    +--------------------------------------------+
                    |       EXTERNAL MONITORED SYSTEM            |
                    |        (Sentinel - fictional app)          |
                    |   audit log mirrored into audit_trail      |
                    +-------------------+------------------------+
                                        |  analysed in sliding 100-row windows
                                        v
+---------------------------------------------------------------------------+
|                         PYTHON / DJANGO PLATFORM                          |
|                                                                           |
|  +---------------------+     +----------------------------------------+  |
|  |  Django Web App     |     |  AI Monitor (manage.py run_ai_monitor) |  |
|  |  cyber/features/*   |     |  headless - scheduled every 1 minute   |  |
|  |  +- dashboard       |     |  1. Fetch next 100-row audit window    |  |
|  |  +- ai_assistant    |     |  2. Pick 3 rotating questions          |  |
|  |  +- analysis_reports|     |  3. Gemini analyses the window         |  |
|  |  +- cyber_agent     |     |  4. Save Q&A to analytical_reports     |  |
|  |  +- profile         |     +-----------------+-----------------------+  |
|  |  +- admin_management|                       |                          |
|  +----------+----------+                       |                          |
|             |                                  |                          |
|             v                                  v                          |
|  +--------------------- PostgreSQL (cyber_intel) ----------------------+  |
|  | users  cyber_incidents  datasets_metadata  it_tickets              |  |
|  | audit_trail  analytical_reports  ai_monitor_state                  |  |
|  +--------------------------------------------------------------------+  |
|                                                                           |
|  Gemini API  (text-to-SQL + analytical explanations, via GEMINI_API_KEY)  |
+---------------------------------------------------------------------------+
```

### Automated Monitoring Data Flow

```
[Windows Task Scheduler - every 1 minute]
     |
     v
Read scan cursor (ai_monitor_state -> last_audit_id, question_index)
     |
     v
Fetch next 100 audit events  (WHERE id > last_id  ORDER BY id  LIMIT 100)
     |  (wraps to id=0 when the full audit log has been consumed)
     v
Pick next 3 questions from the 100+ rotating question pool
     |
     v
For each question: build prompt = schema + 100-event window + question
     |
     v
Gemini analyses the window ->
  - Answer with exact users / IPs / sessions / endpoints involved
  - Risk verdict: Normal / Suspicious / Incident
  - Recommended next actions
     |
     v
Insert (run_id, question, answer) into analytical_reports
Append to reports/ai_monitor.log
     |
     v
Advance cursor -> next run starts at event 101, 201, ...
     |
     v
Analysis Reports page lists the latest run  (refresh to see new rows)
```

### Layered Design

| Layer | Components | Responsibility |
|---|---|---|
| **Presentation** | `templates/`, `cyber/features/*/view.html`, `static/` | Django templates: dashboards, assistant, reports, admin UI |
| **Web Controllers** | `cyber/features/*/index.py`, `cyber/urls.py` | Request routing, auth checks, session handling |
| **Application / Automation** | `cyber/management/commands/run_ai_monitor.py` | Headless scheduled monitoring loop |
| **Agent** | `cyber/agent/` | Tool-based Cyber Intelligence Agent (read + propose writes) |
| **Domain / Model** | `cyber/models.py`, `cyber/services.py` | ORM models, data access, business logic |
| **Infrastructure** | `config/settings.py`, `.env`, PostgreSQL | Settings, secrets, persistence |

---

## 📁 Project Structure

```
CW2_M01119174_CST1510/
|
+-- manage.py                            # Django CLI entry point
|
+-- config/                              # Project configuration package
|   +-- settings.py                      #   Global settings + built-in .env loader
|   +-- urls.py                          #   Root URL dispatcher
|   +-- wsgi.py                          #   WSGI entry point (production servers)
|   +-- asgi.py                          #   ASGI entry point (async servers)
|   +-- __init__.py
|
+-- cyber/                               # Main Django application package
|   +-- admin.py                         #   Django admin model registration
|   +-- apps.py                          #   App configuration (CyberConfig)
|   +-- decorators.py                    #   @login_required_custom / @admin_required
|   +-- gemini_service.py                #   Google Gemini API provider wrapper
|   +-- models.py                        #   7 normalised ORM models (see Database section)
|   +-- services.py                      #   Data access + business logic service layer
|   +-- validators.py                    #   Custom password strength validator
|   +-- urls.py                          #   Application-level URL routes
|   +-- tests.py                         #   Test suite
|   |
|   +-- migrations/                      #   Database schema migrations
|   |   +-- 0001_initial.py              #     Initial schema creation
|   |
|   +-- management/
|   |   +-- commands/
|   |       +-- run_ai_monitor.py        #   Headless AI monitoring runner (Django command)
|   |
|   +-- agent/                           #   Tool-based Cyber Intelligence Agent
|   |   +-- __init__.py                  #     Package init (exports run_agent)
|   |   +-- agent.py                     #     Core agentic loop (reason -> tool -> answer)
|   |   +-- tool_registry.py             #     Registry of all read & write tool functions
|   |   +-- tools.py                     #     All tool implementations (search, stats, CRUD)
|   |   +-- investigation.py             #     Investigation-oriented agent utilities
|   |   +-- monitoring.py                #     Monitoring-oriented agent utilities
|   |   +-- reporting.py                 #     PDF report generation via ReportLab (legacy)
|   |
|   +-- features/                        #   One folder per application page
|       +-- __init__.py
|       |
|       +-- auth/                        #   Login / Register / Logout
|       |   +-- index.py                 #     Controller (login, register, logout views)
|       |   +-- __init__.py
|       |
|       +-- dashboard/                   #   Analytics Dashboard
|       |   +-- index.py                 #     Controller (handles GET, applies filters)
|       |   +-- view.py                  #     Context builder (aggregates data for template)
|       |   +-- view.html                #     Dashboard template (ECharts, KPI cards)
|       |   +-- _js_index.py             #     Inline JavaScript source (chart logic)
|       |   +-- js_view.py               #     Inline JS builder (serialises Python -> JS)
|       |   +-- __init__.py
|       |
|       +-- ai_assistant/                #   Conversational Text-to-SQL AI Assistant
|       |   +-- index.py                 #     Controller (POST question -> Gemini -> answer)
|       |   +-- view.py                  #     Context builder
|       |   +-- view.html                #     Chat interface template
|       |   +-- _js_index.py             #     Inline JS source
|       |   +-- js_view.py               #     Inline JS builder
|       |   +-- __init__.py
|       |
|       +-- analysis_reports/            #   Live AI Monitor Report Viewer
|       |   +-- index.py                 #     Controller (fetches run list, selected run)
|       |   +-- view.py                  #     Context builder
|       |   +-- view.html                #     Report viewer template
|       |   +-- _js_index.py             #     Inline JS source
|       |   +-- js_view.py               #     Inline JS builder
|       |   +-- __init__.py
|       |
|       +-- cyber_agent/                 #   Tool-Based Agent UI
|       |   +-- index.py                 #     Controller (agent loop, pending actions)
|       |   +-- view.py                  #     Context builder
|       |   +-- view.html                #     Agent chat + action confirmation template
|       |   +-- _js_index.py             #     Inline JS source
|       |   +-- js_view.py               #     Inline JS builder
|       |   +-- __init__.py
|       |
|       +-- profile/                     #   User Profile Management
|       |   +-- index.py                 #     Controller (change password)
|       |   +-- view.py                  #     Context builder
|       |   +-- view.html                #     Profile template
|       |   +-- _js_index.py             #     Inline JS source
|       |   +-- js_view.py               #     Inline JS builder
|       |   +-- __init__.py
|       |
|       +-- admin_management/            #   Admin-Only User & Data Management
|           +-- index.py                 #     Controller (promote, demote, delete, add data)
|           +-- view.py                  #     Context builder
|           +-- view.html                #     Admin panel template
|           +-- _js_index.py             #     Inline JS source
|           +-- js_view.py               #     Inline JS builder
|           +-- __init__.py
|
+-- templates/                           # Global Django templates
|   +-- base.html                        #   Base layout (sidebar + topbar + content block)
|   +-- auth/
|   |   +-- login.html                   #     Login page
|   |   +-- register.html               #     Registration page
|   +-- partials/                        #   Reusable layout partials
|       +-- sidebar.html                 #     Navigation sidebar
|       +-- topbar.html                  #     Top navigation bar
|       +-- breadcrumb.html              #     Page breadcrumb
|       +-- footer.html                  #     Page footer
|
+-- static/                              # Static assets (Limitless Bootstrap theme)
|   +-- assets/
|       +-- css/                         #   Custom and vendor CSS
|       +-- js/                          #   App and vendor JavaScript
|       +-- scss/                        #   Bootstrap / theme SCSS source
|       +-- fonts/                       #   Icon and web fonts
|       +-- icons/                       #   Icon libraries
|       +-- images/                      #   Images and demo assets
|       +-- demo/                        #   Demo / sample data
|
+-- reports/                             # Generated PDF reports + ai_monitor.log (gitignored)
+-- requirements.txt                     # Python dependency list
+-- .env.example                         # Template for the git-ignored .env file
+-- .gitignore
```

> Every page folder under `cyber/features/*` follows the same consistent pattern:
> `index.py` (controller) -> `view.py` (data prep) -> `view.html` (template) -> `js_view.py` / `_js_index.py` (inline JavaScript).

---

## 🗄️ Database Design

The platform uses a **PostgreSQL** database named `cyber_intel`. The schema is fully normalised with single primary keys, `NOT NULL` constraints where required, `CHECK` constraints to enforce valid enum values, and indexes on frequently queried columns.

### `roles`

Lookup table of application roles.

| Column | Type | Notes |
|---|---|---|
| `id` | BigInt (PK) | Auto-increment |
| `role_name` | Varchar(50) | Unique — `Administrator`, `Normal Staff` |
| `created_at` | DateTime | Auto-set on create |
| `created_by` | FK → `user.id` | Nullable; who created the row |
| `updated_at` | DateTime | Auto-refreshed on update |
| `updated_by` | FK → `user.id` | Nullable; who last updated the row |

### `user`

Login credentials only — all profile details live in `staff`.

| Column | Type | Notes |
|---|---|---|
| `id` | BigInt (PK) | Auto-increment |
| `username` | Varchar(150) | Unique |
| `password_hash` | Varchar(255) | bcrypt hash |
| `role_id` | FK → `roles.id` | Role lookup (`Administrator` / `Normal Staff`) |
| `is_active` | Boolean | Account enabled flag |
| `last_login` | DateTime | Nullable |
| `created_at` | DateTime | Auto-set on create |
| `created_by` | FK → `user.id` | Nullable (self-referential audit) |
| `updated_at` | DateTime | Auto-refreshed on update |
| `updated_by` | FK → `user.id` | Nullable |

> The table is named `user`, which is a PostgreSQL reserved word, so it is
> always double-quoted (`"user"`) in generated SQL.

### `staff`

Complete user details, linked one-to-one with a login account.

| Column | Type | Notes |
|---|---|---|
| `id` | BigInt (PK) | Auto-increment |
| `user_id` | FK → `user.id` | Unique (one-to-one) |
| `full_name` | Varchar(200) | e.g. `Poka Machande` |
| `email` | Varchar(255) | Nullable |
| `phone` | Varchar(30) | Nullable |
| `position` | Varchar(100) | Job position, nullable |
| `created_at` / `created_by` / `updated_at` / `updated_by` | | Standard audit columns |

### `login_count`

Running login counter per user.

| Column | Type | Notes |
|---|---|---|
| `id` | BigInt (PK) | Auto-increment |
| `user_id` | FK → `user.id` | Unique (one-to-one) |
| `login_count` | Integer | Number of successful logins, default 0 |
| `last_login_at` | DateTime | Timestamp of the most recent login |
| `created_at` / `created_by` / `updated_at` / `updated_by` | | Standard audit columns |

### `auth`

Real authentication events — successful logins, failed attempts and logouts.

| Column | Type | Notes |
|---|---|---|
| `id` | BigInt (PK) | Auto-increment |
| `user_id` | FK → `user.id` | Nullable (unknown usernames keep the event) |
| `username` | Varchar(150) | Username used in the attempt |
| `auth_type` | Varchar(20) | `LOGIN`, `LOGOUT` or `FAILED` — CHECK constraint |
| `status` | Varchar(20) | `success` or `failure` — CHECK constraint |
| `ip_address` | Varchar(45) | Source IP of the attempt |
| `user_agent` | Varchar(500) | Client user agent, nullable |
| `created_at` / `created_by` / `updated_at` / `updated_by` | | Standard audit columns |

> Every table carries the same audit columns: `created_at` (auto-set on
> insert), `created_by`, `updated_at` (auto-refreshed) and `updated_by`.

### `cyber_incidents`

| Column | Type | Notes |
|---|---|---|
| `incident_id` | BigInt (PK) | |
| `timestamp` | DateTime | Incident occurrence time |
| `severity` | Varchar(20) | `Low / Medium / High / Critical` — CHECK |
| `category` | Varchar(50) | e.g. Malware, Phishing, Ransomware |
| `status` | Varchar(20) | `Open / In Progress / Resolved / Closed` — CHECK |
| `description` | Text | Nullable |
| `created_at` | DateTime | Auto-set |

*Indexes: `severity`, `status`, `category`*

### `datasets_metadata`

| Column | Type | Notes |
|---|---|---|
| `dataset_id` | BigInt (PK) | |
| `name` | Varchar(255) | |
| `row_count` | Integer | Non-negative — CHECK |
| `column_count` | Integer | Non-negative — CHECK |
| `uploaded_by` | Varchar(150) | Nullable |
| `upload_date` | Date | Nullable |
| `created_at` | DateTime | Auto-set |

*Index: `uploaded_by`*

### `it_tickets`

| Column | Type | Notes |
|---|---|---|
| `ticket_id` | BigInt (PK) | |
| `priority` | Varchar(20) | `Low / Medium / High / Critical` — CHECK |
| `description` | Text | |
| `status` | Varchar(20) | `Open / In Progress / Resolved / Closed / Waiting for User` — CHECK |
| `assigned_to` | Varchar(150) | Nullable |
| `created_at` | DateTime | |
| `resolution_time_hours` | Integer | Nullable, >= 0 — CHECK |

*Indexes: `priority`, `status`, `assigned_to`*

### `audit_trail`

Mirror of the external monitored system's audit log. **Contains no labels** — meaning is inferred by the AI from event sequences, volume, timing, and JSON metadata.

| Column | Type | Notes |
|---|---|---|
| `id` | BigInt (PK) | Auto-increment |
| `user_id` | Integer | 1-30; empty = unauthenticated activity |
| `action` | Varchar(50) | `LOGIN`, `FILE_ACCESS`, `EXPORT_DATA`, `OUTBOUND_CONNECTION`, ... |
| `resource` | Varchar(50) | `AUTHENTICATION`, `DOCUMENT`, `NETWORK`, ... |
| `method` | Varchar(10) | `GET / POST / PUT / PATCH / DELETE / SYSTEM` |
| `endpoint` | Varchar(255) | e.g. `/api/login` |
| `ip_address` | Varchar(45) | IPv4 or IPv6 |
| `user_agent` | Varchar(500) | Browser / device / process identifier |
| `session_id` | Varchar(64) | Groups events per session |
| `status_code` | Integer | HTTP status (200, 401, 429, ...) |
| `response_time_ms` | Integer | Response latency in milliseconds |
| `metadata` | JSONB | Device, location, file hashes, destination, `normal_activity` flag |
| `created_at` | DateTime | UTC timestamp |

*Indexes: `user_id`, `action`, `created_at`, `session_id`*

### `analytical_reports`

Output table of the AI monitor. Every scheduled run inserts one row per answered question.

| Column | Type | Notes |
|---|---|---|
| `id` | BigInt (PK) | Auto-increment |
| `run_id` | Varchar(50) | e.g. `2026-08-15_14-52-31_W1-100` |
| `question` | Text | Monitoring question asked |
| `answer` | Text | Gemini's analysis with risk verdict |
| `created_at` | DateTime | |

*Index: `run_id`*

### `ai_monitor_state`

Persists the monitor's scan cursor, making runs fully resumable after restarts.

| Column | Type | Notes |
|---|---|---|
| `key` | Varchar(100) (PK) | `last_audit_id`, `question_index` |
| `value` | Text | Current cursor value |
| `updated_at` | DateTime | Auto-updated |

---

## 🤖 Automated AI Monitoring Design

### How It Works

1. **Windows Task Scheduler** triggers `python manage.py run_ai_monitor` every **1 minute**
2. The script reads the scan cursor and fetches the **next 100 audit events** from `audit_trail`
3. It selects the **next 3 questions** from a rotating pool of **100+ monitoring questions**
4. Each question + the 100-event window is sent to **Google Gemini**, which answers with a risk verdict and recommendations
5. The Q&A pair is stored in `analytical_reports` and appended to `reports/ai_monitor.log`
6. The cursor advances. When the end of the audit trail is reached, it wraps to the beginning — simulating **continuous monitoring**

### Monitoring Question Categories

| Category | Coverage |
|---|---|
| Brute Force | Repeated LOGIN_FAILED patterns, account lockout thresholds |
| Data Exfiltration | High-volume EXPORT_DATA, DOWNLOAD_DOCUMENT bursts |
| Privilege Escalation | Unusual role/permission changes |
| Unauthorised Access | 401/403 chains, access to restricted resources |
| Malware / Ransomware | PROCESS_ACTIVITY anomalies, suspicious FILE_ACCESS |
| Insider Threat | Off-hours access, bulk data downloads by internal user IDs |
| Reconnaissance | Systematic endpoint scanning, sequential API probing |
| Security Posture | Overall error rate trends, slow-response patterns |

### Configuration Variables

| Variable | Default | Meaning |
|---|---|---|
| `AUDIT_WINDOW_SIZE` | `100` | Audit events analysed per run |
| `QUESTIONS_PER_RUN` | `3` | Questions asked per run (rotating) |
| `SLEEP_BETWEEN_QUESTIONS` | `3` | Seconds between Gemini calls (rate-limit protection) |
| `AI_MONITOR_VERBOSE` | `0` | Set to `1` to log the raw event window |

### Manual Run

```powershell
.\.venv\Scripts\python.exe manage.py run_ai_monitor
```

---


### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it:

- **Windows (PowerShell):** `.venv\Scripts\Activate.ps1`
- **macOS / Linux:** `source .venv/bin/activate`

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔧 Configuration

### Environment File (`.env`)

Copy `.env.example` to `.env` and fill in your values:

```env
# Django
DJANGO_SECRET_KEY=<your-long-random-secret>
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost,testserver

# Google Gemini AI
GEMINI_API_KEY=<your-gemini-api-key>

# PostgreSQL
POSTGRES_DB=cyber_intel
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<your-password>
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5545
```

> Never commit `.env` to version control. It is listed in `.gitignore`.

### Database Setup

```bash
python manage.py migrate
```

---

## 🚀 Running the Application

```bash
python manage.py runserver
```

Open **http://127.0.0.1:8000/** in your browser.

---

## 📄 Application Pages

| Page | Purpose |
|---|---|
| **Login / Register** | Account creation and authentication |
| **Dashboard** | KPI cards and ECharts for incidents, tickets, and datasets |
| **AI Assistant** | Natural language -> SQL -> Gemini explanation |
| **Analysis Reports** | Live viewer for AI monitor report runs |
| **Cyber Agent** | Tool-based agent chat + pending action confirmation |
| **Profile** | User account management (change password) |
| **Admin Management** | Admin-only: manage users and add data records |

---

## 🛡️ Administrator Access

**Default admin credentials:**

| Field | Value |
|---|---|
| Username | `poka` |
| Password | `Pok@12345` |

> `poka` is seeded as an **Administrator** (see the `roles` lookup table) with
> staff details in the `staff` table. The legacy `Manager` account also retains
> the Administrator role.

Administrators can promote/demote users, reset passwords, delete users, and add incidents, datasets, and tickets.

---

## 🤖 AI Assistant — How It Works

```
User submits a natural-language question
         |
         v
Gemini decides: Does this need SQL?
    +-- OUT_OF_SCOPE  -> polite refusal message
    +-- NO_SQL_NEEDED -> Gemini answers analytically from aggregate context
    +-- SQL query     -> Python executes query against PostgreSQL
                               |
                               v
                     Database returns exact results
                               |
                               v
              Gemini explains results in natural language
```

---

## 🧠 Cyber Intelligence Agent — How It Works

```
User submits a request
         |
         v
Gemini decides: call_tool | propose_action | final_answer
    |
    +-- call_tool (READ - auto-executed)
    |       +-- Execute tool -> feed result back -> repeat up to 5 steps
    |
    +-- propose_action (WRITE - NOT auto-executed)
    |       +-- Stored as pending_action
    |           Admin must explicitly confirm before execution
    |
    +-- final_answer -> Return result to user
```

**Read tools:** `search_incidents`, `get_incident`, `get_incident_statistics`, `search_tickets`, `get_ticket`, `get_ticket_statistics`, `search_datasets`, `get_dataset`, `get_dashboard_summary`, `get_incident_category_statistics`, `get_ticket_workload`

**Write tools (admin-gated):** `close_incident`, `update_incident`, `create_incident`, `close_ticket`, `assign_ticket`, `update_ticket`, `create_ticket`

---

## 🔒 Security

| Mechanism | Description |
|---|---|
| Password hashing | All passwords stored as bcrypt hashes |
| Secrets management | API keys and DB credentials in git-ignored `.env` |
| Parameterised queries | ORM queries are parameterised; AI-generated SQL is sandboxed |
| Session-based auth | Django sessions maintain login state |
| Role-based access | Admin-only routes protected by `@admin_required` decorator |
| Agent write safety | The AI monitor and agent never auto-execute write actions |
| Error logging | Gemini failures logged without exposing credentials |
| DB-level constraints | CHECK constraints enforce valid enum values at the database layer |

---

## 📦 Dependencies

```
bcrypt==5.0.0
Django==6.1
google-genai==2.18.1
psycopg==3.3.4
psycopg-binary==3.3.4
reportlab==5.0.0
tzdata==2026.2
```

---

## ✍️ Author

**Anel Andrew**

Original idea and project concept.

---

## 🏗️ Design & Engineering

**Gerald Ndyamukama**

Full-stack architectural design, Django + PostgreSQL implementation, system refactoring, and world-standard engineering.

---

## 🤝 Contributors

| Name | Contribution |
|---|---|
| **Anel Andres** | Group Contributor |
| **Grolia** | Group Contributor |
| **Passion** | Group Contributor |

---

## 🏁 Project Context

This project was **raised from the Agent Zero Hackathon Event**.

It addresses **real-world cybersecurity challenges** — not purely academic ones — and is built to the standards that real organisations need: autonomous AI monitoring, agentic reasoning, secure data management, and live threat analysis.

---

## 📜 Licence

This project was developed for competition and real-world application purposes.

All rights reserved by the authors and contributors.
