#import path for file location and import pandas
from configpath import IT_TICKETS_FILE
import pandas as pd

#A function to migrate it tickets csv to sql
def migrate_it_tickets(conn):   
    data = pd.read_csv(IT_TICKETS_FILE)
    data.to_sql('it_tickets', conn, if_exists='replace', index=False)

#a function to get all it tickets
def get_all_it_tickets(conn):
    sql = 'SELECT * FROM it_tickets'
    data = pd.read_sql(sql, conn)
    return(data)

#a function to add it tickets
def add_it_ticket(conn, priority, description, status, assigned_to, created_at, resolution_time):
    cursor = conn.cursor()
    # Find the highest ticket ID currently in the table
    cursor.execute("""SELECT MAX(ticket_id) FROM it_tickets""")
    result = cursor.fetchone()[0]
    # Generate the next ticket ID
    if result is None:
        ticket_id = 2000
    else:
        ticket_id = result + 1
    # Insert new ticket
    cursor.execute("""INSERT INTO it_tickets(ticket_id,priority,description,status,assigned_to,created_at,resolution_time)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",(ticket_id,priority,description,status,assigned_to,created_at,resolution_time))
    return ticket_id