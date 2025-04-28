import csv
import random
import uuid
from datetime import datetime, timedelta

# Config
start_time = datetime(2025, 4, 13, 12, 0, 0)
num_entries = 5000

# Extended endpoint and status code lists
endpoints = [
    "/api/login", "/api/logout", "/api/data", "/api/upload", "/api/profile",
    "/api/delete", "/api/update", "/api/health"
]
methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
status_codes = [200, 201, 202, 204, 301, 302, 400, 401, 403, 404, 500, 502, 503]

functions_map = {
    "/api/login": "login_handler",
    "/api/logout": "auth_user",
    "/api/data": "get_data",
    "/api/upload": "upload_file",
    "/api/profile": "update_profile",
    "/api/delete": "delete_account",
    "/api/update": "update_profile",
    "/api/health": "health_check"
}

function_statuses = ["SUCCESS", "FAILED"]
actions = ["ACCEPT", "REJECT"]
src_ips = [f"192.168.1.{i}" for i in range(1, 255)]
dst_ips = [f"10.0.0.{i}" for i in range(1, 255)]

# File names
access_log_file = "access_logs.csv"
execution_log_file = "execution_logs.csv"
vpc_log_file = "vpc_logs.csv"

# Headers
access_headers = ["timestamp", "user_id", "endpoint", "method", "status_code", "request_id"]
execution_headers = ["timestamp", "function_name", "duration_ms", "status", "request_id"]
vpc_headers = ["timestamp", "src_ip", "dst_ip", "action", "bytes_sent", "request_id"]

# Generate master shared log entries
entries = []
for i in range(num_entries):
    timestamp = start_time + timedelta(seconds=i)
    request_id = f"req-{uuid.uuid4().hex[:8]}"
    user_id = f"user_{i+1}"
    entries.append((timestamp.isoformat(), request_id, user_id))

# Build individual logs
access_data = []
execution_data = []
vpc_data = []

for timestamp, request_id, user_id in entries:
    endpoint = random.choice(endpoints)
    method = random.choice(methods)
    status_code = random.choice(status_codes)

    # Access log
    access_data.append([timestamp, user_id, endpoint, method, status_code, request_id])

    # Execution log
    function_name = functions_map.get(endpoint, random.choice(list(functions_map.values())))
    duration_ms = random.randint(100, 2000)
    exec_status = random.choice(function_statuses)
    execution_data.append([timestamp, function_name, duration_ms, exec_status, request_id])

    # VPC log
    src_ip = random.choice(src_ips)
    dst_ip = random.choice(dst_ips)
    action = "ACCEPT" if status_code < 400 else "REJECT"
    bytes_sent = random.randint(500, 10000)
    vpc_data.append([timestamp, src_ip, dst_ip, action, bytes_sent, request_id])

# Shuffle each log independently
random.shuffle(access_data)
random.shuffle(execution_data)
random.shuffle(vpc_data)

# Save to CSV
def save_to_csv(filename, headers, data):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data)

# Write all logs
save_to_csv(access_log_file, access_headers, access_data)
save_to_csv(execution_log_file, execution_headers, execution_data)
save_to_csv(vpc_log_file, vpc_headers, vpc_data)

print("✅ 5000 diversified & shuffled logs saved to:")
print(f" - {access_log_file}")
print(f" - {execution_log_file}")
print(f" - {vpc_log_file}")
