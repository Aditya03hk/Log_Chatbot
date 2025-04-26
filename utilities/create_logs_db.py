import sqlite3

conn = sqlite3.connect('logs.db')
cursor = conn.cursor()

#VPC Logs Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS vpc_logs (
    timestamp TEXT,
    src_ip TEXT,
    dst_ip TEXT,
    action TEXT,
    bytes_sent INTEGER,
    request_id TEXT
);
""")



# Access Logs Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS access_logs (
    timestamp TEXT,
    user_id TEXT,
    endpoint TEXT,
    method TEXT,
    status_code INTEGER,
    request_id TEXT
);
""")

# Execution Logs Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS execution_logs (
    timestamp TEXT,
    function_name TEXT,
    duration_ms INTEGER,
    status TEXT,
    request_id TEXT
);
""")


# Commit and close
conn.commit()
conn.close()



print("Database setup complete.")



