#import os for file location and import pandas
import pandas as pd
from configpath import DATASETS_METADATA_FILE

# a function to migrate from csv to sql
def migrate_datasets_metadata(conn):   
    data = pd.read_csv(DATASETS_METADATA_FILE)
    data.to_sql('datasets_metadata', conn, if_exists='replace', index=False)
#a function to get all meta data sets
def get_all_datasets_metadata(conn):
    sql = 'SELECT * FROM datasets_metadata'
    data = pd.read_sql(sql, conn)
    return(data)
#a function to add meta data information into the data base
def add_metadata(conn, name, rows, columns, uploaded_by, upload_date):
    cursor = conn.cursor()
    # Find the largest dataset_id
    cursor.execute("""
        SELECT MAX(dataset_id)
        FROM datasets_metadata
    """)
    result = cursor.fetchone()[0]
    # Generate next dataset ID
    if result is None:
        dataset_id = 1
    else:
        dataset_id = result + 1
    #Insert new metadata record
    cursor.execute("""INSERT INTO datasets_metadata(dataset_id, name, rows, columns, uploaded_by, upload_date) VALUES (?, ?, ?, ?, ?, ?)""",
    (dataset_id, name, rows, columns, uploaded_by, upload_date))
    return dataset_id