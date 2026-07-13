#importing os to locate files sqlite3
from configpath import DB_FILE
import sqlite3
import streamlit as st


#get connection function
@st.cache_resource
def get_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    return conn