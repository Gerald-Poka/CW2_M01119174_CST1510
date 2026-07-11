#importing os to locate files sqlite3
from configpath import DB_FILE
import sqlite3


#get connection function
def get_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    return conn