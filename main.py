import sys
import os
from constants import *
import pandas as pd
import glob
import time
import duckdb

def connect_duckdb():
    conn = duckdb.connect()
    return conn

def main():
    print("Hello")

def load_datasets(path):

    df = pd.concat([pd.read_csv(f, delimiter=';', decimal=',') for f in glob.glob(path)])
    return df


def chek_columns_types(path, conn):
    df = conn.execute("""
        SELECT *
        FROM 'dataset/*.csv'
    """).df()
    conn.register("df_view", df)
    conn.execute("DESCRIBE df_view").df() # doesn't work if you don't register df as a virtual table


if __name__ == '__main__':
    conn = duckdb.connect()

    res = conn.execute("""
    SELECT COUNT(*)
    FROM read_csv('stock_market_data/nasdaq/csv/*.csv', header=True, dateformat='%d-%m-%Y', columns={'Date': 'DATE', 'Low': 'DOUBLE', 'Open': 'DOUBLE', 'Volume': 'BIGINT', 'High': 'DOUBLE', 'Close': 'DOUBLE', 'AdjustedClose': 'DOUBLE'}, filename=True)
    """).fetchall()
    print(res)


    PATH = 'stock_market_data/nasdaq'
    for filename in glob.iglob(f'{PATH}/csv/*.csv'):
        dest = f'{PATH}/parquet/{filename.split("/")[-1][:-4]}.parquet'
        conn.execute(f"""
        COPY (SELECT * FROM read_csv('{filename}', header=True, dateformat='%d-%m-%Y', columns={{'Date': 'DATE', 'Low': 'DOUBLE', 'Open': 'DOUBLE', 'Volume': 'BIGINT', 'High': 'DOUBLE', 'Close': 'DOUBLE', 'AdjustedClose': 'DOUBLE'}}, filename=True)) 
        TO '{dest}' (FORMAT 'parquet')""")
