#import sqlite3 and os
#importing os to locate files sqlite3

import sqlite3
from configpath import USERS_FILE
from app_model.db import get_connection
from hashing import generate_hash_password, verify_password
import re

#Function to register a new user.


def register_user(conn, username, password):
    # Password validation using regex
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
        

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
        

    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
        

    if not re.search(r"\d", password):
        return False,"Password must contain at least one digit."
        
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False,"Password must contain at least one special character."

    # Hash the password
    hashed_password = generate_hash_password(password)

    try:
        add_user(conn, username, hashed_password)
        return True, "user registered successfully."

    except Exception as e:
        return False, f"Error registering user: {e}"

#store the username and hashed password in a txt file
def write_to_users_file(username,hashed_passord):
    with open(USERS_FILE, "a") as f:
        f.write(f"{username}, {hashed_passord}\n")
   
    

    
#Function to login user.
def login_user(conn, username_input, password_input):
    print("Welcome back!")

    #username_input = input("Enter your username: ")
    #password_input = input("Enter your password: ")

    user = get_user(conn, username_input)
    #check if user exists
    if user is None:
        return False, "User not found.", None
        
    #unpack user details
    user_id, username, hashed_password, role = user
    print(f"Welcome {username_input} !!")
    #verify password validity
    if verify_password(password_input, hashed_password):
        return True, "Login successful.", user
    else:
        return False, "Incorrect password.", None

def verify_using_user_txt_file (): 
    username_input = input("Enter your username: ")
    password_input = input("Enter your password: ")  
    #read the users.txt file to get the stored username and hashed password
    try:
        with open(USERS_FILE, "r") as f:
           users = f.readlines()
    #iterate through the users list to find the username and hashed password
        for user in users:
            stored_username, stored_hashed_password = user.strip().split(", ", 1)
            if stored_username == username_input:
                if verify_password(password_input, stored_hashed_password):
                  print("Login successful!")
                return
            else:
                 print("Invalid username or password.")
            return
    except FileNotFoundError:
        print("No users found. Please register first.")
        
#function to change users password
def change_password(conn, user_id,current_password, new_password ):
    cursor = conn.cursor()
    #get the saved hasged password
    cursor.execute("SELECT password_hash FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()
    if user is None:
        return False, "User not found."
    stored_hash = user[0]
    # Check current password
    if not verify_password(current_password, stored_hash):
        return False, "Current password is incorrect."

    # Prevent using the same password again
    if verify_password(new_password, stored_hash):
        return False, "New password cannot be the same as the current password."

    # Password validation
    if len(new_password) < 8:
        return False, "Password must be at least 8 characters."

    if not re.search(r"[A-Z]", new_password):
        return False, "Password must contain an uppercase letter."

    if not re.search(r"[a-z]", new_password):
        return False, "Password must contain a lowercase letter."

    if not re.search(r"\d", new_password):
        return False, "Password must contain a digit."

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", new_password):
        return False, "Password must contain a special character."

    # Hash the new password
    new_hash = generate_hash_password(new_password)

    cursor.execute(
        """
        UPDATE users
        SET password_hash = ?
        WHERE id = ?
        """,
        (new_hash, user_id)
    )

    conn.commit()

    return True, "Password changed successfully."


#function to add a new user to the database   
def add_user(conn, username, hashed_passord):
    cursor = conn.cursor()
    sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
    parameters = (username, hashed_passord)
    cursor.execute(sql, parameters)
    conn.commit()
    
# move user data from the users.txt file to the database    
def migrate_users(conn):
    try:
      with open(USERS_FILE, 'r') as f:
        users = f.readlines()
        print("number of users to migrate:", len(users))
        for user in users:
            print("Processing user:", user.strip().split(", ", 1)[0])
            username,hashed_passord= user.strip().split(", ", 1)
            try:
                add_user(conn, username, hashed_passord)
            except sqlite3.IntegrityError:
                print(f"User {username} already exists in the database. Skipping migration for this user.")
    except FileNotFoundError:
            print("users.txt file not found.")
    

def get_all_users(conn):
   cursor = conn.cursor()
   sql = """SELECT * FROM users"""
   cursor.execute(sql)
   users = cursor.fetchall()
   return(users)

def get_user(conn, username):
    cursor = conn.cursor()
    sql = """SELECT * FROM users WHERE username = ?"""
    parameters = (username,)
    cursor.execute(sql, parameters)
    user = cursor.fetchone()
    return(user)

def update_user(conn, old_username, new_username):     
    cursor = conn.cursor()
    sql = "UPDATE users SET username = ? WHERE username = ?"
    parameters = (new_username, old_username)
    cursor.execute(sql, parameters)
    conn.commit()


def delete_user(conn, username):     
    cursor = conn.cursor()
    sql = "DELETE FROM users WHERE username = ?"
    parameters = (username,)
    cursor.execute(sql, parameters)
    conn.commit()
