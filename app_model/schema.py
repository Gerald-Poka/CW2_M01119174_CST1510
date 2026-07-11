#creating the user table in the database to store the user information
def create_user_table(conn):
    #create a cursor object to execute SQL commands
    cursor = conn.cursor()
    #create a table to store the user information
    sql = '''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user'
    )'''
    cursor.execute(sql)
    conn.commit()