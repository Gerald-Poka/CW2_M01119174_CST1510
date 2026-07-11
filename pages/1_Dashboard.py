import streamlit as st
from app_model.cyber_incidents import get_all_cyber_incidents
from app_model.metadata import get_all_datasets_metadata
from app_model.it_tickets import get_all_it_tickets
from app_model.db import get_connection
import pandas as pd


st.set_page_config(
    page_title="Home", 
    page_icon=":house:", 
    layout="wide")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.write("Please log in to access the dashboard.")
    if st.button("Go to Login Page"):
        st.session_state.logged_in = False
        st.switch_page("Home.py")
    st.stop()
else:
    st.write("Welcome to the dashboard!")


#Display the welcome message and platform description    
st.title(" IT AND SECURITY ANALYSIS ")       
st.subheader("Welcome to your IT & Security Analytics Platform for exploring pre-analyzed cyber incidents, IT tickets, and metadata insights.") 
 

   
# Function to deal with cyber incidents data and display the dashboard metrics and visualisations
def display_cyber_incidents_dashboard():
    data = get_all_cyber_incidents(get_connection())
    st.title(" CYBER INCIDENTS ANALYSIS")

    with st.sidebar:
        st.header("Navigation Bar for Cyber Incidents Analysis")
        selected_severity = st.selectbox('Severity Level', data['severity'].unique())

    # Convert timestamp column
    data['timestamp'] = pd.to_datetime(data['timestamp'])

    # Filter data by selected severity
    filtered_data = data[data['severity'] == selected_severity]

    # Checking for empty data frames to avoid crashing the dashboard
    if filtered_data.empty:
        st.info(f"No incidents found for the {selected_severity} severity level.")
        st.stop()

    # Create 2 columns for dashboard metrics
    col1, col2 = st.columns(2)

    # Total incidents for the selected severity
    with col1:
        st.metric(label=f"{selected_severity} Severity Incidents", value=len(filtered_data) )

    # Highest category of the selected severity
    with col2:
        st.metric(
            label="Top Category",
            value=filtered_data['category'].mode()[0]
        )

    # Fetch the number of selected severity incidents by status
    status_counts = filtered_data["status"].value_counts()

    # Display the status metrics in 4 columns
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Open Incidents", status_counts.get("Open", 0))

    with col2:
        st.metric("In Progress Incidents", status_counts.get("In Progress", 0))

    with col3:
        st.metric("Resolved Incidents", status_counts.get("Resolved", 0))

    with col4:
        st.metric("Closed Incidents", status_counts.get("Closed", 0))

    # Charts section
    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"Cyber Incidents with Severity Level: {selected_severity}")
        st.bar_chart(filtered_data['category'].value_counts())

    with col2:
        st.subheader("Category Trends over Time")
        st.line_chart(filtered_data, x='timestamp', y='category')

    # Filter incidents that require immediate action
    action_required_incidents = filtered_data[
        filtered_data["status"].isin(["Open", "In Progress"])
    ]

    st.subheader(
        f"Incidents Requiring Immediate Action for {selected_severity} Severity Level"
    )

    st.metric(
        "Incidents Requiring Immediate Action",
        len(action_required_incidents)
    )

    # Empty data frame check to avoid crashing the dashboard
    if action_required_incidents.empty:
        st.info(
            f"No incidents requiring immediate action for the {selected_severity} severity level."
        )
        st.stop()
    else:
        st.dataframe(action_required_incidents)

    # Display the filtered data in a table format
    st.subheader(f"{selected_severity} Severity Incidents")
    st.dataframe(filtered_data)
    
    
#Function to deal with metadata data and display the dashboard metrics and visualisations   
def display_metadata_analysis_dashboard():
    data = get_all_datasets_metadata(get_connection())
    st.title(" METADATA ANALYSIS")
    
    #create the navigation bar for metadata analysis in the sidebar
    with st.sidebar:
        st.header("Navigation Bar for Metadata Analysis")
        selected_uploaded_by = st.selectbox('Uploaded by', data['uploaded_by'].unique())

    
    
    # Filter data by selected priority
    filtered_data = data[data['uploaded_by'] == selected_uploaded_by]
    
    
    
    #Display in collumns
    col1, col2, col3 = st.columns(3)
     
    #Display the number of datasets uploaded by selected user
    with col1:
      st.metric(f"Datasets uploaded by {selected_uploaded_by}",len(filtered_data))
    
    #Total rows uploaded by the user
    with col2:
        st.metric("Total Rows",f"{filtered_data['rows'].sum():,}")
    
    #Average data set size uploaded by the user
    with col3:
        st.metric("Average Dataset Size",int(filtered_data["rows"].mean()))
    
    #largest dataset uploaded by the user
    largest = filtered_data.loc[filtered_data["rows"].idxmax()]
    st.write("### Largest Dataset")
    st.write(largest[["name", "rows"]])
    
    
    # Charts section
    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"Dataset Size Comaparison for {selected_uploaded_by}")
        st.bar_chart(filtered_data.set_index("name")["columns"])

    with col2:
        st.subheader(f"Dataset Upload Timeline for {selected_uploaded_by}")
        filtered_data["upload_date"] = pd.to_datetime(filtered_data["upload_date"])
        st.line_chart(filtered_data.set_index('upload_date')["rows"])

   

    # Display the filtered data in a table format
    st.subheader(" Metadata Uploads")
    st.dataframe(filtered_data)
    
    
#Function to deal with IT tickets data and display the dashboard metrics and visualisations    
def display_it_tickets_dashboard():
    data = get_all_it_tickets(get_connection())
    st.title(" IT TICKETS ANALYSIS")

    with st.sidebar:
        st.header("Navigation Bar for IT Tickets Analysis")
        selected_priority = st.selectbox('Ticket priority', data['priority'].unique())

    # Convert timestamp column
    data['created_at'] = pd.to_datetime(data['created_at'], errors='coerce')

    # Filter data by selected priority
    filtered_data = data[data['priority'] == selected_priority]

    # Checking for empty data frames to avoid crashing the dashboard
    if filtered_data.empty:
        st.info(f"No tickets found for {selected_priority} priority.")
        st.stop()

    # Create 2 columns for dashboard metrics
    col1, col2 = st.columns(2)

    # Total tickets for the selected priority
    with col1:
        st.metric(
            label=f"{selected_priority} Priority Tickets",
            value=len(filtered_data)
        )

    # Highest assigned_to of the selected priority
    with col2:
        st.metric(
            label="Top Assigned IT Support",
            value=filtered_data['assigned_to'].mode()[0]
        )

    # Fetch the number of assigned to IT support  by assigned_to
    assigned_to_counts = filtered_data["assigned_to"].value_counts()

    # Display the priority metrics in 4 columns
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Tickets assigned to IT_Support_A", assigned_to_counts.get("IT_Support_A", 0))

    with col2:
        st.metric("Tickets assigned to IT_Support_B", assigned_to_counts.get("IT_Support_B", 0))

    with col3:
        st.metric("Tickets assigned to IT_Support_C", assigned_to_counts.get("IT_Support_C", 0))



    # Charts section
    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"IT Tickets status with Priority: {selected_priority}")
        st.bar_chart(filtered_data['status'].value_counts())

    with col2:
        st.subheader("Category Trends over Time")
        st.line_chart(filtered_data, x='created_at', y='status')
        
        
        
    # Filter IT tickets that require immediate action
    action_required_it_tickets = filtered_data[filtered_data["status"].isin(["Open", "In Progress"])]

    st.subheader(f" IT Tickets Requiring Immediate Action for {selected_priority} Priority")

    st.metric( "IT Tickets Requiring Immediate Action",len(action_required_it_tickets))

    # Empty data frame check to avoid crashing the dashboard
    if action_required_it_tickets.empty:
        st.info(f"No IT tickets requiring immediate action for the {selected_priority} priority.")
        st.stop()
    else:
        st.dataframe(action_required_it_tickets)    
     
    # Display the filtered data in a table format
    st.subheader(f"{selected_priority} Priority IT Tickets")
    st.dataframe(filtered_data)  
    

#tabs to diplay the data sets analytics
tab_cyber, tab_IT_tickets, tab_Metadata = st.tabs([" Cyber Incidents Analytics", " IT Tickets Analytics"," Metadata Analytics"])

with tab_cyber:
    display_cyber_incidents_dashboard()

with tab_IT_tickets:
    display_it_tickets_dashboard()

with tab_Metadata:
    display_metadata_analysis_dashboard()
