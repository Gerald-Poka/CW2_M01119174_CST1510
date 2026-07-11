#import os for file location and import pandas
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
