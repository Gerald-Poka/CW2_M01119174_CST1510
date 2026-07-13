#import packages
import streamlit as st
from app_model.users import promote_user, demote_user, delete_user, admin_change_password, get_all_users
from app_model.db import get_connection
from app_model.cyber_incidents import add_cyber_incident
from app_model.metadata import add_metadata
from app_model.it_tickets import add_it_ticket
#check if the user is logged in
if not st.session_state.get("logged_in", False):
    st.error("Please log in first.")
    if st.button("Go to Login Page"):
        st.session_state.logged_in = False
        st.switch_page("Home.py")
    st.stop()
    
st.title("ADMINISTRATOR MANAGEMENT SYSTEM")
st.header("For Authorized personels only")
#request for admin password input
admin_password = st.text_input("Enter Administrator Password", type="password", key="admin_password")


# a function for users management       
def user_management():
    import pandas as pd
    #call the connection
    conn = get_connection()
    # Heading of the page
    st.title(" User Management")
    st.markdown("Manage user roles, delete accounts or reset passwords.")
    st.divider()
    
    #a table to desplay all users
    st.markdown(" Registered Users")
    users = get_all_users(conn)
    if users:
        df = pd.DataFrame(users, columns=["ID", "Username", "Password Hash", "Role"])
        st.dataframe(
            df[["ID", "Username", "Role"]], use_container_width=True, hide_index=True)
    else:
        st.warning("No users found.")
    
    st.divider()
    
    # a search bar for users
    st.markdown(" Search User")
    search = st.text_input("Search by username", placeholder="Type to search...", key="search_username")
    
    if users:
        df = pd.DataFrame(users, columns=["ID", "Username", "Password Hash", "Role"])
        
        # Filter table based on search
        if search:
            filtered_df = df[df["Username"].str.contains(search, case=False, na=False)]
        else:
            filtered_df = df
            
        st.dataframe( filtered_df[["ID", "Username", "Role"]], use_container_width=True, hide_index=True)
    
    st.divider()
    
    # section that helps the admin manage the user
    st.markdown(" Manage a User")
    
    usernames = [user[1] for user in users] if users else []
    
    username = st.selectbox( "Select a User", options=usernames, key="user_mgmt_username")
    
    st.divider()
    
    # buttons to manage user
    st.markdown(" Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Promote", key="promote_btn", use_container_width=True):
            if username:
                promote_user(conn, username)
                conn.commit()
                st.success(f"{username} promoted to Admin successfully.")
                st.rerun()
            else:
                st.warning("Please select a user.")
    
    with col2:
        if st.button("Demote", key="demote_btn", use_container_width=True):
            if username:
                demote_user(conn, username)
                conn.commit()
                st.success(f"{username} demoted to User successfully.")
                st.rerun()
            else:
                st.warning("Please select a user.")
    
    with col3:
        if st.button("Reset Password", key="change_pwd_btn", use_container_width=True):
            if username:
                admin_change_password(conn, username)
                conn.commit()
                st.success(f"Password reset for {username} successfully.")
                st.rerun()
            else:
                st.warning("Please select a user.")
    
    with col4:
        if st.button("Delete", key="delete_btn", use_container_width=True):
            if username:
                delete_user(conn, username)
                conn.commit()
                st.success(f"{username} deleted successfully.")
                st.rerun()
            else:
                st.warning("Please select a user.")
    
    st.divider()
    
    # desplay users and adminst statistics
    st.markdown(" Registration Statistics")
    
    if users:
        df_stats = pd.DataFrame(users, columns=["ID", "Username", "Password Hash", "Role"])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Users", len(df_stats))
        
        with col2:
            admin_count = len(df_stats[df_stats["Role"] == "admin"])
            st.metric("Total Admins", admin_count)
        
        with col3:
            user_count = len(df_stats[df_stats["Role"] == "user"])
            st.metric("Total Regular Users", user_count)




#a function to manage cyber incidences database
def cyber_management():
    st.title("Add a Cyber Incident")
    st.write("Enter details for a new cyber security incident.")
    
    # Wrap everything in a form - prevents rerun on every widget change
    with st.form("cyber_form"):
        timestamp = st.date_input("Incident Timestamp", key="cyber_timestamp")
        severity = st.selectbox("Severity", ["Low","Medium","High","Critical"], key="cyber_severity")
        category = st.selectbox("Category", ["Malware","Phishing","DDoS","Misconfiguration","Unauthorized Access"], key="cyber_category")
        status = st.selectbox("Status", ["Open","In Progress","Resolved","Closed"], key="cyber_status")
        description = st.text_area("Description", key="cyber_description")
        
        submitted = st.form_submit_button("Add Cyber Incident") 
        
        if submitted:
            conn = get_connection()
            formatted_timestamp = str(timestamp) + " 00:00:00"
            success = add_cyber_incident(conn, formatted_timestamp, severity, category, status, description)
            conn.commit()
            if success:
                st.success("Cyber incident added successfully.")
            else:
                st.error("Failed to add incident.")

#a function to manage metadata sets
def metadata_management():
    st.title("Add to Metadata database")
    st.write("Fill the details required")
    
    #Wrap everything in a form
    with st.form("metadata_form"):
        name = st.text_input("Dataset Name", key="meta_name")
        rows = st.number_input("Number of Rows", min_value=0, key="meta_rows")
        columns = st.number_input("Number of Columns", min_value=0, key="meta_columns")
        uploaded_by = st.text_input("Uploaded By", key="meta_uploaded_by")
        upload_date = st.date_input("Upload Date", key="meta_upload_date")
        
        submitted = st.form_submit_button("Add Dataset")  
        
        if submitted:
            conn = get_connection()
            dataset_id = add_metadata(conn, name, rows, columns, uploaded_by, upload_date)
            conn.commit()
            st.success(f"Dataset added successfully. Dataset ID: {dataset_id}")

#a function to manage it tickets datasets
def it_ticket_management():
    st.title("Add IT Ticket")
    
    #Wrap everything in a form
    with st.form("ticket_form"):
        priority = st.selectbox("Select Priority", ["Low", "Medium", "High", "Critical"], key="ticket_priority")
        description = st.text_area("Ticket Description", key="ticket_description")
        status = st.selectbox("Select Status", ["Open", "In Progress", "Resolved", "Closed"], key="ticket_status")
        assigned_to = st.text_input("Assigned To eg: IT_Support_A/B/C", key="ticket_assigned_to")
        created_at = st.date_input("Created Date", key="ticket_created_at")
        resolution_time = st.text_input("Resolution Time", placeholder="Example: 2 hours, 1 day", key="ticket_resolution_time")
        
        submitted = st.form_submit_button("Add IT Ticket") 
        
        if submitted:
            if description == "" or assigned_to == "":
                st.warning("Please fill in all required fields")
            else:
                conn = get_connection()
                ticket_id = add_it_ticket(conn, priority, description, status, assigned_to, str(created_at), resolution_time)
                conn.commit()
                st.success(f"IT Ticket added successfully. Ticket ID: {ticket_id}")

 
 

#verify admin password and provide access to authorised functionalities
# Verify button
if st.button("Verify"):
    if admin_password == st.secrets["ADMIN_PASSWORD"]:
        st.session_state.admin_logged_in = True
        st.success("Administrator access granted")
    else:
        if admin_password != "":
            st.session_state.admin_logged_in = False
            st.error("Incorrect administrator password.")

# Tabs persist across reruns because we use session_state
if st.session_state.get("admin_logged_in", False):
    user_management()
    cyber_management()
    metadata_management()
    it_ticket_management()
