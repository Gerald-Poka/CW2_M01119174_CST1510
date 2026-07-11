#import os for file location and import pandas
import pandas as pd
from configpath import DATASETS_METADATA_FILE


def migrate_datasets_metadata(conn):   
    data = pd.read_csv(DATASETS_METADATA_FILE)
    data.to_sql('datasets_metadata', conn, if_exists='replace', index=False)

def get_all_datasets_metadata(conn):
    sql = 'SELECT * FROM datasets_metadata'
    data = pd.read_sql(sql, conn)
    return(data)