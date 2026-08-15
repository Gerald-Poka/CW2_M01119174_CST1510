"""AI Assistant controller: conversational text-to-SQL assistant.

The Gemini-backed pipeline (``gemini_service``) decides whether a question needs
SQL, analyses the database, and explains the results. Swapping to a different
provider (e.g. Ollama) later only requires changing ``gemini_service``.
"""

import json

from django.shortcuts import render

from cyber import gemini_service, services
from cyber.decorators import login_required_custom
from cyber.features.ai_assistant import js_view

DATABASE_SCHEMA = """
You have access to a PostgreSQL database with these exact tables and columns:

TABLE: cyber_incidents
Columns:
  - incident_id   : unique ID for each incident (e.g. 1000, 1001)
  - timestamp     : date and time of the incident (e.g. 2024-04-12 19:00:00)
  - severity      : severity level - values are exactly: Low, Medium, High, Critical
  - category      : type of incident (e.g. Malware, Phishing, Ransomware)
  - status        : current status - values are exactly: Open, In Progress, Resolved, Closed
  - description   : text description of the incident

TABLE: it_tickets
Columns:
  - ticket_id             : unique ID for each ticket (e.g. 2000, 2001)
  - priority              : priority level - values are exactly: Low, Medium, High, Critical
  - description           : text description of the ticket problem
  - status                : current status - values are exactly: Open, In Progress, Resolved, Closed, Waiting for User
  - assigned_to           : who the ticket is assigned to (e.g. IT_Support_A)
  - created_at            : date and time ticket was created
  - resolution_time_hours : how many hours it took to resolve (integer, nullable)

TABLE: datasets_metadata
Columns:
  - dataset_id  : unique ID for each dataset
  - name        : name of the dataset (e.g. Customer_Churn)
  - row_count   : number of rows in the dataset
  - column_count: number of columns in the dataset
  - uploaded_by : who uploaded it (e.g. data_scientist, cyber_admin)
  - upload_date : date it was uploaded

TABLE: roles
Columns:
  - id         : role ID (e.g. 1, 2)
  - role_name  : values are exactly: Administrator, Normal Staff

TABLE: user  (IMPORTANT: always quote this table as "user" in SQL, because user is a reserved word)
Columns:
  - id            : unique user ID
  - username      : login username (unique)
  - password_hash : bcrypt hash - never expose or display this value
  - role_id       : foreign key to roles.id
  - is_active     : whether the account is active (true/false)
  - last_login    : timestamp of the last successful login
  - created_at    : when the login account was created

TABLE: staff
Columns:
  - id         : unique staff record ID
  - user_id    : foreign key to user.id (one login account per staff member)
  - full_name  : complete staff name (e.g. Poka Machande)
  - email      : staff email address
  - phone      : staff phone number
  - position   : job position or title

TABLE: login_count
Columns:
  - id            : unique row ID
  - user_id       : foreign key to user.id
  - login_count   : number of successful logins
  - last_login_at : timestamp of the most recent login

TABLE: auth
Columns:
  - id         : unique authentication event ID
  - user_id    : foreign key to user.id (null when the username does not exist)
  - username   : username used in the attempt
  - auth_type  : values are exactly: LOGIN, LOGOUT, FAILED
  - status     : values are exactly: success, failure
  - ip_address : source IP of the attempt
  - created_at : when the authentication event happened

TABLE: audit_trail
Columns:
  - id               : unique event ID (1, 2, 3, ...)
  - user_id          : synthetic application user ID (1-30); empty = unauthenticated activity
  - action           : what happened (e.g. LOGIN, LOGIN_FAILED, VIEW_USER, VIEW_DOCUMENT, DOWNLOAD_DOCUMENT, FILE_ACCESS, EXPORT_DATA, UPDATE_USER, UPDATE_CONFIG, SEARCH, API_REQUEST, OUTBOUND_CONNECTION, PROCESS_ACTIVITY)
  - resource         : the resource involved (e.g. AUTHENTICATION, USER, DOCUMENT, SYSTEM_FILE, NETWORK, API)
  - method           : HTTP method (GET/POST/PUT/PATCH/DELETE) or SYSTEM for internal activity
  - endpoint         : the API endpoint (e.g. /api/login, /api/users/42)
  - ip_address       : source IP (private 10.x / 192.168.x or documentation ranges)
  - user_agent       : browser/device/process identifier
  - session_id       : events in one user session share this id
  - status_code      : HTTP status (200, 201, 204, 304, 401, 404, 422, 429, 500, 503)
  - response_time_ms : response time in milliseconds
  - metadata         : JSON string with extra evidence (device, location, file, destination, records, settings_changed, normal_activity flag)
  - created_at       : event timestamp (YYYY-MM-DD HH:MM:SS, UTC)
"""


def _generate_sql(user_question, history):
    sql_prompt = f"""
You are a SQL expert working with a PostgreSQL database.

{DATABASE_SCHEMA}

Conversation History:
{history}

The user has asked this question:
{user_question}

Your job:
1. Decide if this question requires a database query to answer accurately.
2. If yes, write a single valid PostgreSQL SQL query that answers the question.
3. If the question is about cybersecurity, cyber incidents, IT tickets, dataset metadata, or the organisation's data but does not require SQL, respond with: NO_SQL_NEEDED
4. If the question is unrelated to the database or these domains, respond with: OUT_OF_SCOPE
Rules:
- Only return the raw SQL query or NO_SQL_NEEDED.
- Do not include any explanation.
- Do not include markdown formatting like ```sql
- Do not include semicolons at the end.
- Only use tables and columns that exist in the schema above.
"""
    result = gemini_service.generate_content(sql_prompt)
    return result if result is not None else "SERVER_ERROR"


def _execute_sql(sql_query):
    from django.db import connection
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql_query)
            columns = [d[0] for d in cursor.description]
            rows = [list(r) for r in cursor.fetchall()]
        return columns, rows
    except Exception as e:
        return None, str(e)


def _answer_analytical(user_question, history):
    cyber_incidents = services.get_all_cyber_incidents()
    it_tickets = services.get_all_it_tickets()
    critical = sum(1 for i in cyber_incidents if i.severity == "Critical")
    high = sum(1 for i in cyber_incidents if i.severity == "High")
    open_inc = sum(1 for i in cyber_incidents if i.status == "Open")

    prompt = f"""
You are a cybersecurity intelligence assistant for this organisation.

Context about the organisation data:
- Total cyber incidents : {len(cyber_incidents)}
- Critical incidents    : {critical}
- High incidents        : {high}
- Open incidents        : {open_inc}
- Total IT tickets      : {len(it_tickets)}

Conversation History:
{history}

Current User Question:
{user_question}

You are an AI assistant for this Cyber Intelligence Platform.

You may ONLY answer questions about:
- cyber incidents
- IT tickets
- dataset metadata
- cybersecurity
- information contained in this organisation's database

If the user's question is unrelated to these topics, respond exactly with:

"I'm only able to answer questions related to the Cyber Intelligence Platform database, cybersecurity, IT tickets, and dataset metadata."
"""
    return gemini_service.generate_content(prompt) or (
        "I'm only able to answer questions related to the Cyber Intelligence "
        "Platform database, cybersecurity, IT tickets, and dataset metadata."
    )


def _explain_results(user_question, sql_query, columns, rows, history):
    prompt = f"""
You are a cybersecurity intelligence assistant.

Conversation History:
{history}

The user asked:
{user_question}

To answer this accurately, the following SQL query was executed against the database:
{sql_query}

The database returned these exact results:
{json.dumps({"columns": columns, "rows": rows}, indent=2, default=str)}

Your job:
- Explain these results clearly to the user.
- Use the exact numbers from the results above.
- Do not guess or estimate any values.
- Provide relevant insights or recommendations if appropriate.
"""
    return gemini_service.generate_content(prompt) or "I could not generate an explanation."


@login_required_custom
def index(request):
    messages = request.session.get("chat_messages", [])
    error = None

    if request.method == "POST":
        question = request.POST.get("question", "").strip()
        if not question:
            error = "Please enter a question."
        else:
            messages.append({"role": "user", "content": question})
            history_for_prompt = "\n".join(
                f"{m['role']}: {m['content']}" for m in messages[-6:-1]
            )

            sql_query = _generate_sql(question, history_for_prompt)

            if sql_query == "SERVER_ERROR":
                answer = "Gemini is currently busy. Please try again in a moment."
            elif sql_query == "OUT_OF_SCOPE":
                answer = ("I'm only able to answer questions related to the "
                          "Cyber Intelligence Platform database, cybersecurity, "
                          "IT tickets, and dataset metadata.")
            elif sql_query == "NO_SQL_NEEDED":
                answer = _answer_analytical(question, history_for_prompt)
            else:
                columns, result = _execute_sql(sql_query)
                if result is None or isinstance(result, str):
                    answer = _answer_analytical(question, history_for_prompt)
                else:
                    answer = _explain_results(question, sql_query, columns, result,
                                              history_for_prompt)

            messages.append({"role": "assistant", "content": answer})
            messages = messages[-10:]
            request.session["chat_messages"] = messages

    return render(request, "ai_assistant/view.html",
                  {"messages": messages, "error": error,
                   "active": "ai_assistant",
                   "js_view": js_view.build_js({})})
