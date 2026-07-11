import streamlit as st

from app_model.db import get_connection
from app_model.users import register_user, login_user

conn = get_connection()

st.set_page_config(page_title="Home")

st.title("Home")

st.write("Welcome Home!")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    
tab_login, tab_register = st.tabs(["Login", "Register"])
#create the login tab
with tab_login:
    login_username = st.text_input("Username", key="login_username")
    login_password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        success, message, user = login_user(conn, login_username, login_password)
        if success:
            user_id, username, hashed_password, role = user
            st.balloons()
            st.success(f"Welcome {username}!")
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = role
            st.session_state.user_id = user_id
            st.switch_page("pages/1_Dashboard.py")
        else:
            st.error(f"Login failed: {login_username}")
  
#create the register tab  
with tab_register:
    register_username = st.text_input("Username", key="register_username")
    register_password = st.text_input("Password", type="password", key="register_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="register_password2")
    if st.button("Register"):
        if not register_username or not register_password or not confirm_password:
            st.error("Please fill in all fields.")  
        elif register_password != confirm_password:
            st.error("Passwords do not match")
        else:
            success, message = register_user(conn, register_username, register_password)

            if success:
              st.success(f"{register_username} Registered successfully! Move to Login to access the dashboard. ")
            else:
                st.error(message)
            