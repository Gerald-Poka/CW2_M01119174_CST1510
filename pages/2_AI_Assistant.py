# import all packages and functions
import streamlit as st
from google import genai
import pandas as pd
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
"""

#A function that takes the question asked and converts it into an SQL query
def generate_sql(user_question: str) -> str:
    sql_prompt = f"""
You are a SQL expert working with a SQLite database.

{database_schema}

The user has asked this question:
{user_question}

Your job:
1. Decide if this question requires a database query to answer accurately.
2. If yes, write a single valid SQLite SQL query that answers the question.
3. If no (e.g. the question is conceptual or about recommendations), respond with: NO_SQL_NEEDED

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
        return "SERVER_ERROR"


# a function that takes up the SQL query that gemini wrote and runs it against the database
def execute_sql(sql_query: str) -> pd.DataFrame:
    conn = get_connection()
    try:
        result = pd.read_sql_query(sql_query, conn)
        return result
    except Exception as e:
        return pd.DataFrame({"Error": [str(e)]})


# a function that returns the result from the database and asks gemini to explain it
def explain_results(user_question: str, sql_query: str, results: pd.DataFrame) -> str:
    explain_prompt = f"""
You are a cybersecurity intelligence assistant.

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
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=explain_prompt,
    )
    return response.text.strip()


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

User Question:
{user_question}

Provide a clear and helpful answer.
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=analytical_prompt,
    )
    return response.text.strip()


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
    st.chat_message("user").write(prompt)

    # shows a spinning animation while the code is working
    with st.spinner("Thinking..."):
        sql_query = generate_sql(prompt)

    # handle api errors
    if sql_query == "SERVER_ERROR":
        with st.chat_message("assistant"):
            st.error("Gemini is currently busy. Please try again in a moment.")
        st.stop()

    elif sql_query == "NO_SQL_NEEDED":
        # No SQL needed, answer analytically
        gemini_reply = answer_analytical(prompt)
        with st.chat_message("assistant"):
            st.write(gemini_reply)

    else:
        # Execute the SQL against the database
        query_results = execute_sql(sql_query)

        if "Error" in query_results.columns:
            # SQL failed, fall back to analytical
            gemini_reply = answer_analytical(prompt)
            with st.chat_message("assistant"):
                st.write(gemini_reply)

        else:
            # Ask Gemini to explain the real results
            gemini_reply = explain_results(prompt, sql_query, query_results)
            with st.chat_message("assistant"):
                st.write(gemini_reply)

            # Show the raw results
            with st.expander("View raw query results"):
                st.code(sql_query, language="sql")
                st.dataframe(query_results)

    # Save assistant reply to history
    if sql_query != "SERVER_ERROR":
        st.session_state.messages.append({"role": "assistant", "content": gemini_reply})


    