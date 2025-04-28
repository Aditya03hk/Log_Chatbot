import sqlite3
import pandas as pd

# CSV files
access_csv = "access_logs.csv"
execution_csv = "execution_logs.csv"
vpc_csv = "vpc_logs.csv"

# SQLite DB file
db_file = "logs.db"

# Read CSVs using pandas
access_df = pd.read_csv(access_csv)
execution_df = pd.read_csv(execution_csv)
vpc_df = pd.read_csv(vpc_csv)

# Connect to SQLite DB (or create if it doesn't exist)
conn = sqlite3.connect(db_file)

# Save each DataFrame as a table in the database
access_df.to_sql("access_logs", conn, if_exists="replace", index=False)
execution_df.to_sql("execution_logs", conn, if_exists="replace", index=False)
vpc_df.to_sql("vpc_logs", conn, if_exists="replace", index=False)

# Close connection
conn.close()

print("✅ Logs successfully imported into 'logs.db' with tables:")
print("   - access_logs")
print("   - execution_logs")
print("   - vpc_logs")
