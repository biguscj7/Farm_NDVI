import sqlite3
from sqlite3 import Error
import pandas as pd
from datetime import datetime as dt
from pprint import  pprint as pp
import os

def create_connection(dbfile: str):
    """Create a database connection for use in the script"""
    conn = None
    try:
        conn = sqlite3.connect(dbfile)
        print(sqlite3.version)
    except Error as e:
        print(e)

    return conn

def filename_to_dt(filename: str):
    """Parse the filename to pull datetime from it"""
    tail = filename.split('_')[1]
    dt_str = tail.split('.')[0]

    return dt.strptime(dt_str, '%Y%m%dT%H%M')

def stats_to_df(filename: str, timestamp, conn):
    """Opens csv file into dataframe for writing to db"""
    file_df = pd.read_csv(f'../stats/votm/{filename}')
    file_df['date_time'] = timestamp.isoformat()

    file_df.set_index('date_time', inplace=True)
    file_df.rename(columns={'Unnamed: 0': 'georegion'}, inplace=True)

    file_df.to_sql('evi', conn, if_exists='append')

if __name__ == '__main__':
    c = create_connection('../db/test.db')

    evi_filename = [filename for filename in os.listdir('../stats/votm') if filename[0:3] == 'clo']

    if c is not None:
        for filename in evi_filename:
            timestamp = filename_to_dt(filename)
            stats_to_df(filename, timestamp, c)

    else:
        print("Error! cannot create the database connection.")

    c.close()