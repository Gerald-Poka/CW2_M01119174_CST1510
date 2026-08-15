# import all packages and functions
import streamlit as st
from google import genai
import pandas as pd
import logging
from app_model.db import get_connection
from app_model.cyber_incidents import get_all_cyber_incidents
from app_model.metadata import get_all_datasets_metadata
from app_model.it_tickets import get_all_it_tickets

#call the API key from secrets
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# Load all data for establishing context
conn = get_connection()
cyber_incidents_data = get_all_cyber_incidents(conn)
metadata_data = get_all_datasets_metadata(conn)
it_tickets_data = get_all_it_tickets(conn)

#cinfigure error logging
logging.basicConfig(filename="gemini_errors.log",level=logging.ERROR,format="%(asctime)s - %(levelname)s - %(message)s")


#Telling the LLM what the data base looks like
database_schema = """
You have access to a SQLite database with these exact tables and columns:

TABLE: cyber_incidents
Columns:
  - incident_id   : unique ID for each incident (e.g. 1000, 1001)
  - timestamp     : date and time of the incident (e.g. 2024-04-12 19:00:00)
  - severity      : severity level - values are exactly: Low, Medium, High, Critical
  - category      : type of incident (e.g. Malware, Phishing, Ransomware)
  - status        : current status - values are exactly: Open, Resolved, Closed
  - description   : text description of the incident

TABLE: it_tickets
Columns:
  - ticket_id             : unique ID for each ticket (e.g. 2000, 2001)
  - priority              : priority level - values are exactly: High, Medium, Low
  - description           : text description of the ticket problem
  - status                : current status - values are exactly: Open, Resolved, Closed
  - assigned_to           : who the ticket is assigned to (e.g. IT_Support_A)
  - created_at            : date and time ticket was created
  - resolution_time_hours : how many hours it took to resolve

TABLE: datasets_metadata
Columns:
  - dataset_id  : unique ID for each dataset
  - name        : name of the dataset (e.g. Customer_Churn)
  - rows        : number of rows in the dataset
  - columns     : number of columns in the dataset
  - uploaded_by : who uploaded it (e.g. data_scientist, cyber_admin)
  - upload_date : date it was uploaded

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

#A function that takes the question asked and converts it into an SQL query
def generate_sql(user_question: str) -> str:
    sql_prompt = f"""
You are a SQL expert working with a SQLite database.

{database_schema}

Conversation History:
{get_chat_history()}

The user has asked this question:
{user_question}

Your job:
1. Decide if this question requires a database query to answer accurately.
2. If yes, write a single valid SQLite SQL query that answers the question.
3. If the question is about cybersecurity, cyber incidents, IT tickets, dataset metadata, or the organisation's data but does not require SQL, respond with: NO_SQL_NEEDED
4. If the question is unrelated to the database or these domains, respond with: OUT_OF_SCOPE
Rules:
- Only return the raw SQL query or NO_SQL_NEEDED.
- Do not include any explanation.
- Do not include markdown formatting like ```sql
- Do not include semicolons at the end.
- Only use tables and columns that exist in the schema above.
"""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=sql_prompt,
        )
        return response.text.strip()
    
    except Exception as e:
        logging.error(e)
        return "SERVER_ERROR"


# a function that takes up the SQL query that gemini wrote and runs it against the database
def execute_sql(sql_query: str) -> pd.DataFrame:
    conn = get_connection()
    try:
        result = pd.read_sql_query(sql_query, conn)
        return result
    except Exception as e:
        logging.error(e)
        return pd.DataFrame({"Error": [str(e)]})


# a function that returns the result from the database and asks gemini to explain it
def explain_results(user_question: str, sql_query: str, results: pd.DataFrame) -> str:
    explain_prompt = f"""
You are a cybersecurity intelligence assistant.

Conversation History:
{get_chat_history()}

The user asked:
{user_question}

To answer this accurately, the following SQL query was executed against the database:
{sql_query}

The database returned these exact results:
{results.to_string()}

Your job:
- Explain these results clearly to the user.
- Use the exact numbers from the results above.
- Do not guess or estimate any values.
- Provide relevant insights or recommendations if appropriate.
"""
    # Return a generator that yields text chunks
    def stream_response():
        try:
            for chunk in client.models.generate_content_stream(
              model="gemini-2.5-flash",
            contents=explain_prompt,
        ):
                if hasattr(chunk, "text") and chunk.text:
                    yield chunk.text

        except Exception as e:
            logging.error(e)
            if "RESOURCE_EXHAUSTED" in str(e):
                yield "AI assistant API quota exceeded. Please wait a while."
            else:
                yield "An unexpected error occurred while contacting AI."
    return stream_response()
#A function to keep history of the conversation and foe the AI to use the history as it answers other questions
def get_chat_history():
    history = ""
    for message in st.session_state.messages[-6:]:
        history += f"{message['role']}: {message['content']}\n"
    return history

#Function that handles questions that do not need the database
def answer_analytical(user_question: str) -> str:
    analytical_prompt = f"""
You are a cybersecurity intelligence assistant for this organisation.

Context about the organisation data:
- Total cyber incidents : {len(cyber_incidents_data)}
- Critical incidents    : {len(cyber_incidents_data[cyber_incidents_data['severity'] == 'Critical'])}
- High incidents        : {len(cyber_incidents_data[cyber_incidents_data['severity'] == 'High'])}
- Open incidents        : {len(cyber_incidents_data[cyber_incidents_data['status'] == 'Open'])}
- Total IT tickets      : {len(it_tickets_data)}

Converstion History:
{get_chat_history()}

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
    # Return a generator that yields text chunks
    def stream_response():
        try:
            for chunk in client.models.generate_content_stream(
                model="gemini-2.5-flash",
                contents=analytical_prompt,
               ):
                if hasattr(chunk, 'text') and chunk.text:
                    yield chunk.text
        except Exception as e:
            logging.error(e)
            if "RESOURCE_EXHAUSTED" in str(e):
                yield "AI assistant API quota exceeded. Please wait a while."
            else:
                yield "An unexpected error occurred while contacting AI."
    return stream_response()


# Streamlit chat page
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.write("Please log in to access the dashboard.")
    if st.button("Go to Login Page"):
        st.session_state.logged_in = False
        st.switch_page("Home.py")
    st.stop()

st.title("Chat with your assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    if message["role"] == "user":
        st.chat_message("user").write(message["content"])
    else:
        st.chat_message("assistant").write(message["content"])

prompt = st.chat_input("Ask your assistant a question:")

if prompt:

    # Save and display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    #set a limit to the number of chats messages stored per session
    MAX_HISTORY = 20
    if len(st.session_state.messages) > MAX_HISTORY:
        st.session_state.messages = st.session_state.messages[-MAX_HISTORY:]
    st.chat_message("user").write(prompt)

    # shows a spinning animation while the code is working
    with st.spinner("Thinking..."):
        sql_query = generate_sql(prompt)

    # handle api errors
    if sql_query == "SERVER_ERROR":
        with st.chat_message("assistant"):
            st.error("Gemini is currently busy. Please try again in a moment.")
        st.stop()
    elif sql_query == "OUT_OF_SCOPE":
        with st.chat_message("assistant"):
            gemini_reply = (
            "I'm only able to answer questions related to the "
            "Cyber Intelligence Platform database, cybersecurity, "
            "IT tickets, and dataset metadata."
        )
        st.write(gemini_reply)
    elif sql_query == "NO_SQL_NEEDED":
        with st.chat_message("assistant"):
            #capture the full text that write_stream returns
            gemini_reply = st.write_stream(answer_analytical(prompt))

    else:
        query_results = execute_sql(sql_query)

        if "Error" in query_results.columns:
            with st.chat_message("assistant"):
                #capture the full text that write_stream returns
                gemini_reply = st.write_stream(answer_analytical(prompt))

        else:
            with st.chat_message("assistant"):
                #capture the full text that write_stream returns
                gemini_reply = st.write_stream(explain_results(prompt, sql_query, query_results))

            with st.expander("View raw query results"):
                st.code(sql_query, language="sql")
                st.dataframe(query_results)

    # Save assistant reply to history
    if sql_query != "SERVER_ERROR":
        st.session_state.messages.append({"role": "assistant", "content": gemini_reply})
    MAX_HISTORY = 10
    if len(st.session_state.messages) > MAX_HISTORY:
        st.session_state.messages = st.session_state.messages[-MAX_HISTORY:]