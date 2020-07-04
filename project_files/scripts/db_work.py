import sqlite3
from sqlite3 import Error
import pandas as pd
from datetime import datetime as dt
import json
from pprint import  pprint as pp
import os
import csv
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
    return tail.split('.')[0]


def stats_to_db(filename: str, timestamp, conn, veg_index):
    """Opens csv file into dataframe for writing to db"""
    file_df = pd.read_csv(f'../stats/votm/{filename}')
    file_df['date_time'] = timestamp # no datetime inside file, must pull from name

    file_df.rename(columns={'Unnamed: 0': 'georegion'}, inplace=True)

    file_df.to_sql(veg_index, conn, if_exists='append', index=False)

def merge_cld_data(conn):
    """Merges cloud data from SAFE file with cloud data from image classifier"""
    with open('../stats/votm/cloud.json') as cld_file:
        img_cld_dict = json.load(cld_file)

    img_cld_df = pd.DataFrame.from_dict(img_cld_dict).transpose()

    img_cld_df.sort_index(inplace=True)

    auto_dict = {}

    for date_stamp in list(img_cld_df.index):
        with open(f'../stats/votm/cloud_{date_stamp}.csv') as reader:
            csv_reader = csv.reader(reader)
            headers = next(csv_reader)[1:]
            values = next(csv_reader)[1:]
            safe_dict = dict(zip(headers, values))
        auto_dict.update({date_stamp: safe_dict})

    safe_df = pd.DataFrame.from_dict(auto_dict).transpose()

    safe_df.sort_index(inplace=True)

    combined_dv = pd.merge(img_cld_df, safe_df, left_index=True, right_index=True)

    combined_dv.to_sql('clouds', conn, if_exists='append')

if __name__ == '__main__':
    c = create_connection('../db/3_Jul_new.db')
    c.execute('pragma encoding=UTF8')

    for veg_index in ['ndvi', 'evi', 'lai']:

        index_filename = [filename for filename in os.listdir('../stats/votm') if filename.startswith(veg_index)]

        # before opening a file, check to see if it's already got data in the cloud dict.
        if c is not None:
            for filename in index_filename:
                timestamp = filename_to_dt(filename)
                stats_to_db(filename, timestamp, c, veg_index)

        else:
            print("Error! cannot create the database connection.")

    merge_cld_data(c)

    c.close()