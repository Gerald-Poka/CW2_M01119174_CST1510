from configpath import (DB_FILE, USERS_FILE,BASE_DIR, DATA_DIR)

# Print paths on startup so you can confirm they are correct
print("BASE_DIR:", BASE_DIR)
print("DATA_DIR:", DATA_DIR)
print("USERS_FILE:", USERS_FILE)
print("DB_FILE:", DB_FILE)



from app_model.db import get_connection
from app_model.users import (register_user, login_user, migrate_users, verify_password, get_user,)
from app_model.schema import create_user_table
from app_model.metadata import migrate_datasets_metadata
from app_model.cyber_incidents import migrate_cyber_incidents
from app_model.it_tickets import migrate_it_tickets 
from hashing import generate_hash_password
import re
    

#main function to run the program
def main():
   #set up database on first run.
   try:
     conn = get_connection()
     create_user_table(conn)
     migrate_users(conn)
    #migrate the data from the csv files to the database
     migrate_cyber_incidents(conn)
     migrate_datasets_metadata(conn)
     migrate_it_tickets(conn)
   except Exception as e:
        print("Error setting up the database:", e)
        return
   while True:
        #display the menu options to the user
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        #read the user input and call the appropriate function based on the user's choice
        choice = input("Enter your choice: ")
        if choice == "1":
            register_user(conn)
        elif choice == "2":
            login_user(conn)
        elif choice == "3":
            print("Good Bye!")
            break
        else:
            print("Invalid choice. Please try again.")
#run the main function when the script is executed
if __name__ == "__main__":
    main()
