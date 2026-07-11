import streamlit as st

from app_model.db import get_connection
from app_model.users import change_password

st.set_page_config(page_title="Profile", page_icon="👤", layout="wide")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.write("Please log in to access the Profile.")
    if st.button("Go to Login Page"):
        st.session_state.logged_in = False
        st.switch_page("Home.py")
    st.stop()

conn = get_connection()

col1, col2 = st.columns([1, 5])

with col1:
    st.markdown("# 👤")

with col2:
    st.subheader(st.session_state.username)
    st.caption(st.session_state.role.capitalize())


#Change password code
st.divider()
st.subheader("🔒  Change Password")
current_username = st.text_input("Username", key="profile_username")
current_password = st.text_input("Current Password",type="password")

new_password = st.text_input("New Password",type="password")

confirm_password = st.text_input("Confirm New Password",type="password")
#cange password buttopn calling the change password function
if st.button("Change Password"):
    #make sure that all requirements are filled
    if current_password == "" or new_password == "" or confirm_password == "":
        st.error("Please complete all fields.")
    #checks of the new password is equal to the confirmed password
    elif new_password != confirm_password:
        st.error("New passwords do not match.")

    else:
        
        success, message = change_password(
            conn,
            st.session_state.user_id,
            current_password,
            new_password
        )

        if success:
            st.success(message)

        else:
            st.error(message)
#The logout button            
st.divider()

st.subheader("ACCOUNT LOGOUT")

if st.button("🚪 LOGOUT", use_container_width=True):

    # Clear session state
    st.session_state.clear()
    # Return to Home
    st.switch_page("Home.py")
            
            
            
