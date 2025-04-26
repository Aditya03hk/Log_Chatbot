import csv
import sqlite3
import pandas as pd
import os
import sys


conn = sqlite3.connect('logs.db')

vpc_df = pd.read_csv("vpc_logs.csv")
access_df = pd.read_csv("access_logs.csv")
execution_df = pd.read_csv("execution_logs.csv")

# Insert into respective tables
vpc_df.to_sql('vpc_logs', conn, if_exists='append', index=False)
access_df.to_sql('access_logs', conn, if_exists='append', index=False)
execution_df.to_sql('execution_logs', conn, if_exists='append', index=False)
conn.commit()   
conn.close()
print("Data inserted into database successfully.")
# db_to_csv.py      