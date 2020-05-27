import sqlite3
from sqlite3 import Error
import pandas as pd
from datetime import datetime as dt
import numpy as np
import json
from pprint import  pprint as pp
import os
import rasterio
from rasterio.plot import show

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

def stats_to_df(filename: str, timestamp, conn, cloud_dict):
    """Opens csv file into dataframe for writing to db"""
    file_df = pd.read_csv(f'../stats/votm/{filename}')
    file_df['date_time'] = timestamp.isoformat() # no datetime inside file, must pull from name

    file_df.rename(columns={'Unnamed: 0': 'georegion'}, inplace=True)

    stamp_str = timestamp.strftime('%Y%m%dT%H%M') # include try/except for missing dict key

    cld_df = pd.DataFrame(cloud_dict[stamp_str], index=np.arange(file_df.shape[0]), dtype=np.bool)

    with_cld_df = pd.concat([file_df, cld_df], axis=1)

    with_cld_df.to_sql('ndvi', conn, if_exists='append')

if __name__ == '__main__':
    c = create_connection('../db/test2.db')
    c.execute('pragma encoding=UTF8')

    with open('../stats/votm/cloud.json') as cld_file:
        cld_dict = json.load(cld_file)

    evi_filename = [filename for filename in os.listdir('../stats/votm') if filename.startswith('ndvi')]

    if c is not None:
        for filename in evi_filename:
            timestamp = filename_to_dt(filename)
            stats_to_df(filename, timestamp, c, cld_dict)

    else:
        print("Error! cannot create the database connection.")

    c.close()