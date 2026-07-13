#import packages
import streamlit as st
from app_model.users import promote_user, demote_user, delete_user, admin_change_password
from app_model.db import get_connection
from app_model.cyber_incidents import add_cyber_incident
from app_model.metadata import add_metadata
from app_model.it_tickets import add_it_ticket
#check if the user is logged in
if not st.session_state.get("logged_in", False):
    st.error("Please log in first.")
    st.stop()
    
st.title("ADMINISTRATOR MANAGEMENT SYSTEM")
st.header("For Authorized personels only")
#request for admin password input
admin_password = st.text_input("Enter Administrator Password", type="password", key="admin_password")


# a function for users management
def user_management():
    st.header("You are authorised to promote, demote, delete or change users password")
    #request for username
    username = st.text_input("Enter username")
    #call the connection
    conn = get_connection()
    if st.button("Promote User"):
        promote_user(conn, username)
    if st.button("Demote user"):
        demote_user(conn, username)
    if st.button("Delete User"):
        delete_user(conn, username)
    if st.button("Change pasword"):
        admin_change_password(conn, username)


 #a function to manage cyber incidences 
def cyber_management():
    st.header("Create Cyber Incident")
    st.write("Enter details for a new cyber security incident.")
    #request user input for all variables
    timestamp = st.datetime_input("Incident Timestamp, Format: year-month-date HR.MIN.SEC.000000")
    severity = st.selectbox("Severity",["Low","Medium","High","Critical"])
    category = st.selectbox("Category",["Malware","Phishing","DDoS","Misconfiguration","Unauthorized Access"])
    status = st.selectbox("Status",["Open","In Progress","Resolved","Closed"])
    description = st.text_area("Description")
    if st.button("Add Cyber Incident"):
        conn = get_connection()
        success = add_cyber_incident(conn, timestamp, severity, category, status, description)
        if success:
            st.success("Cyber incident added successfully.")
        else:
            st.error("Failed to add incident.")
     
 

 #adding meta data,
def metadata_management():
    name = st.text_input("Dataset Name")
    rows = st.number_input("Number of Rows", min_value=0)
    columns = st.number_input("Number of Columns",min_value=0)
    uploaded_by = st.text_input("Uploaded By")
    upload_date = st.date_input("Upload Date")
    if st.button("Add Dataset"):
        conn = get_connection()
        dataset_id = add_metadata(conn, name, rows, columns, uploaded_by, upload_date)
        st.success(f"Dataset added successfully. Dataset ID: {dataset_id}")
    
#function to manage It tickets data 
def it_ticket_management():
    st.header("Add IT Ticket")
    # Get user inputs
    priority = st.selectbox("Select Priority",["Low", "Medium", "High", "Critical"])
    description = st.text_area("Ticket Description")
    status = st.selectbox("Select Status",["Open", "In Progress", "Resolved", "Closed"])
    assigned_to = st.text_input("Assigned To eg: IT_Support_A/B/C")
    created_at = st.date_input("Created Date Format: year-month-date HR.MIN.SEC ")
    resolution_time = st.text_input( "Resolution Time",placeholder="Example: 2 hours, 1 day")
    # Submit button
    if st.button("Add IT Ticket"):
        # Check required fields
        if description == "" or assigned_to == "":
            st.warning("Please fill in all required fields")
        else:
            conn = get_connection()
            ticket_id = add_it_ticket(conn,priority,description,status,assigned_to,str(created_at),resolution_time)
            st.success(f"IT Ticket added successfully. Ticket ID: {ticket_id}")

 
 

#verify admin password and provide access to authorised functionalities
if st.button("Verify"):
    if admin_password == st.secrets["ADMIN_PASSWORD"]:
        st.session_state.admin_logged_in = True
        st.success("Administrator access granted")
        users_tab, cyber_tab, metadata_tab, IT_tickets_tab = st.tabs(["User Management", "Cyber Incidents Management", "Metadata Management", "IT Tickets Management"])
        with users_tab:
            user_management()

        with cyber_tab:
            cyber_management()

        with metadata_tab:
            metadata_management()

        with IT_tickets_tab:
            it_ticket_management()
    else:
        if admin_password != "":
            st.error("Incorrect administrator password.")
            st.stop()