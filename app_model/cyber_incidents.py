#import paths for file location and import pandas
import pandas as pd
from configpath import CYBER_INCIDENTS_FILE


#function to migrate csv file 
def migrate_cyber_incidents(conn):
    data = pd.read_csv(CYBER_INCIDENTS_FILE)
    data.to_sql('cyber_incidents', conn, if_exists='replace', index=False)
    
#function to get all cyber incidents
def get_all_cyber_incidents(conn):
    sql = 'SELECT * FROM cyber_incidents'
    data = pd.read_sql(sql, conn)
    return(data)

#function to add cyber incidences
def add_cyber_incident(conn, timestamp, severity, category, status, description):
    cursor = conn.cursor()
    # Find the current largest incident_id
    cursor.execute("""SELECT MAX(incident_id) FROM cyber_incidents""")
    result = cursor.fetchone()[0]
    # Generate the next incident ID
    if result is None:
        incident_id = 1000
    else:
        incident_id = result + 1
    # Insert the new cyber incident
    cursor.execute("""
        INSERT INTO cyber_incidents
        (
            incident_id,
            timestamp,
            severity,
            category,
            status,
            description
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """,
    (
        incident_id,
        timestamp,
        severity,
        category,
        status,
        description
    ))


    conn.commit()

    return incident_id