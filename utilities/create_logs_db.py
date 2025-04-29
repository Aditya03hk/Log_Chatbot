# # import csv
# # import random
# # import uuid
# # from datetime import datetime, timedelta

# # # Config
# # start_time = datetime(2025, 4, 13, 12, 0, 0)
# # num_entries = 5000

# # # Extended endpoint and status code lists
# # endpoints = [
# #     "/api/login", "/api/logout", "/api/data", "/api/upload", "/api/profile",
# #     "/api/delete", "/api/update", "/api/health"
# # ]
# # methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
# # status_codes = [200, 201, 202, 204, 301, 302, 400, 401, 403, 404, 500, 502, 503]

# # functions_map = {
# #     "/api/login": "login_handler",
# #     "/api/logout": "auth_user",
# #     "/api/data": "get_data",
# #     "/api/upload": "upload_file",
# #     "/api/profile": "update_profile",
# #     "/api/delete": "delete_account",
# #     "/api/update": "update_profile",
# #     "/api/health": "health_check"
# # }

# # function_statuses = ["SUCCESS", "FAILED"]
# # actions = ["ACCEPT", "REJECT"]
# # src_ips = [f"192.168.1.{i}" for i in range(1, 255)]
# # dst_ips = [f"10.0.0.{i}" for i in range(1, 255)]

# # # File names
# # access_log_file = "access_logs.csv"
# # execution_log_file = "execution_logs.csv"
# # vpc_log_file = "vpc_logs.csv"

# # # Headers
# # access_headers = ["timestamp", "user_id", "endpoint", "method", "status_code", "request_id"]
# # execution_headers = ["timestamp", "function_name", "duration_ms", "status", "request_id"]
# # vpc_headers = ["timestamp", "src_ip", "dst_ip", "action", "bytes_sent", "request_id"]

# # # Generate master shared log entries
# # entries = []
# # for i in range(num_entries):
# #     timestamp = start_time + timedelta(seconds=i)
# #     request_id = f"req-{uuid.uuid4().hex[:8]}"
# #     user_id = f"user_{i+1}"
# #     entries.append((timestamp.isoformat(), request_id, user_id))

# # # Build individual logs
# # access_data = []
# # execution_data = []
# # vpc_data = []

# # for timestamp, request_id, user_id in entries:
# #     endpoint = random.choice(endpoints)
# #     method = random.choice(methods)
# #     status_code = random.choice(status_codes)

# #     # Access log
# #     access_data.append([timestamp, user_id, endpoint, method, status_code, request_id])

# #     # Execution log
# #     function_name = functions_map.get(endpoint, random.choice(list(functions_map.values())))
# #     duration_ms = random.randint(100, 2000)
# #     exec_status = random.choice(function_statuses)
# #     execution_data.append([timestamp, function_name, duration_ms, exec_status, request_id])

# #     # VPC log
# #     src_ip = random.choice(src_ips)
# #     dst_ip = random.choice(dst_ips)
# #     action = "ACCEPT" if status_code < 400 else "REJECT"
# #     bytes_sent = random.randint(500, 10000)
# #     vpc_data.append([timestamp, src_ip, dst_ip, action, bytes_sent, request_id])

# # # Shuffle each log independently
# # random.shuffle(access_data)
# # random.shuffle(execution_data)
# # random.shuffle(vpc_data)

# # # Save to CSV
# # def save_to_csv(filename, headers, data):
# #     with open(filename, "w", newline="") as f:
# #         writer = csv.writer(f)
# #         writer.writerow(headers)
# #         writer.writerows(data)

# # # Write all logs
# # save_to_csv(access_log_file, access_headers, access_data)
# # save_to_csv(execution_log_file, execution_headers, execution_data)
# # save_to_csv(vpc_log_file, vpc_headers, vpc_data)

# # print("✅ 5000 diversified & shuffled logs saved to:")
# # print(f" - {access_log_file}")
# # print(f" - {execution_log_file}")
# # print(f" - {vpc_log_file}")


import csv
import random
import uuid
from datetime import datetime, timedelta
import math

# Config
end_date = datetime.now()
start_date = end_date - timedelta(days=90)  # 3 months of data
num_entries = 5000

# Extended endpoint and status code lists
endpoints = [
    "/api/login", "/api/logout", "/api/data", "/api/upload", "/api/profile",
    "/api/delete", "/api/update", "/api/health", "/api/payment", "/api/admin",
    "/api/config", "/api/backup", "/api/reset", "/api/token"
]
methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
status_codes = [200, 201, 202, 204, 301, 302, 400, 401, 403, 404, 500, 502, 503]

functions_map = {
    "/api/login": "login_handler",
    "/api/logout": "auth_handler",
    "/api/data": "data_processor",
    "/api/upload": "file_uploader",
    "/api/profile": "profile_manager",
    "/api/delete": "data_cleaner",
    "/api/update": "update_service",
    "/api/health": "health_checker",
    "/api/payment": "payment_processor",
    "/api/admin": "admin_console",
    "/api/config": "config_manager",
    "/api/backup": "backup_service",
    "/api/reset": "reset_handler",
    "/api/token": "token_generator"
}

function_statuses = ["SUCCESS", "FAILED", "TIMEOUT", "ERROR"]
actions = ["ACCEPT", "REJECT", "DROP"]

# IP ranges with some suspicious IPs mixed in
normal_ips = [f"192.168.1.{i}" for i in range(1, 255)] + \
              [f"10.0.0.{i}" for i in range(1, 255)]
suspicious_ips = ["45.227.253.109", "185.143.223.15", "62.210.180.94", 
                 "192.168.1.100", "10.0.0.15"]  # Internal IPs behaving badly

admin_users = ["admin", "superuser", "root"]
regular_users = [f"user_{i}" for i in range(1, 501)]  # 500 regular users
all_users = admin_users + regular_users

# File names
access_log_file = "access_logs.csv"
execution_log_file = "execution_logs.csv"
vpc_log_file = "vpc_logs.csv"

# Headers
access_headers = ["timestamp", "user_id", "endpoint", "method", "status_code", "request_id"]
execution_headers = ["timestamp", "function_name", "duration_ms", "status", "request_id"]
vpc_headers = ["timestamp", "src_ip", "dst_ip", "action", "bytes_sent", "request_id"]

def generate_timestamps(start, end, count):
    """Generate realistic timestamps with bursts of activity"""
    timestamps = []
    for _ in range(count):
        # Create time bias - more activity during business hours
        hour = random.randint(0, 23)
        if 9 <= hour <= 17:  # Business hours
            if random.random() < 0.7:  # 70% of logs during business hours
                base_date = start + (end - start) * random.random() ** 2  # More recent bias
        else:
            base_date = start + (end - start) * random.random()
        
        # Add some bursts of activity
        if random.random() < 0.05:  # 5% chance of burst
            burst_count = random.randint(5, 20)
            burst_time = base_date
            for _ in range(burst_count):
                timestamps.append(burst_time)
                burst_time += timedelta(seconds=random.uniform(0.1, 2))
        
        # Add random second offset
        base_date += timedelta(seconds=random.randint(0, 86400))
        timestamps.append(base_date)
    
    # Trim to exact count and sort
    timestamps = sorted(timestamps[:count])
    return timestamps

def generate_realistic_user():
    """Generate users with some having more activity"""
    if random.random() < 0.8:  # 80% chance regular user
        user = random.choice(regular_users)
        if random.random() < 0.2:  # 20% of regulars are more active
            return user, random.randint(1, 5)
        return user, random.randint(1, 2)
    else:  # 20% chance admin user
        return random.choice(admin_users), random.randint(1, 10)

# Generate master shared log entries with realistic distribution
timestamps = generate_timestamps(start_date, end_date, num_entries)
entries = []

for i, timestamp in enumerate(timestamps):
    request_id = f"req-{uuid.uuid4().hex[:8]}"
    user_id, user_entries = generate_realistic_user()
    
    for _ in range(user_entries):
        entries.append((timestamp.isoformat(), request_id, user_id))
        # Add slight time variation for same-user entries
        timestamp += timedelta(seconds=random.uniform(0.1, 1))

# Build individual logs with anomalies
access_data = []
execution_data = []
vpc_data = []

for timestamp, request_id, user_id in entries:
    # Determine if this is an anomalous entry (5% chance)
    is_anomaly = random.random() < 0.05
    is_suspicious_user = user_id in admin_users and random.random() < 0.1
    
    # Endpoint selection with anomalies
    if is_anomaly or is_suspicious_user:
        endpoint = random.choice(["/api/admin", "/api/config", "/api/backup", "/api/login"])
        method = random.choice(["POST", "PUT", "DELETE"])
    else:
        endpoint = random.choice(endpoints)
        method = random.choice(methods)
    
    # Status code with anomalies
    if is_anomaly:
        status_code = random.choice([401, 403, 404, 500])
    elif is_suspicious_user:
        status_code = random.choice([200, 201, 403])
    else:
        status_code = random.choice(status_codes)
        if status_code >= 400 and random.random() < 0.7:  # Retry success
            status_code = random.choice([200, 201])
    
    # Access log
    access_data.append([timestamp, user_id, endpoint, method, status_code, request_id])
    
    # Execution log with anomalies
    function_name = functions_map.get(endpoint, random.choice(list(functions_map.values())))
    
    if is_anomaly:
        duration_ms = random.randint(5000, 30000)  # Very long duration
        exec_status = random.choice(["FAILED", "TIMEOUT", "ERROR"])
    else:
        duration_ms = random.randint(50, 2000)
        if duration_ms > 1500 and random.random() < 0.3:  # Some long but successful
            exec_status = "SUCCESS"
        else:
            exec_status = random.choice(function_statuses)
    
    execution_data.append([timestamp, function_name, duration_ms, exec_status, request_id])
    
    # VPC log with anomalies
    if is_anomaly or is_suspicious_user:
        src_ip = random.choice(suspicious_ips)
        action = random.choice(["REJECT", "DROP"])
        bytes_sent = random.randint(10000, 500000)  # Large data transfer
    else:
        src_ip = random.choice(normal_ips)
        action = "ACCEPT" if status_code < 400 else random.choice(["REJECT", "ACCEPT"])
        bytes_sent = random.randint(500, 10000)
    
    dst_ip = random.choice(normal_ips)
    vpc_data.append([timestamp, src_ip, dst_ip, action, bytes_sent, request_id])

# Add some brute force attack patterns
def add_attack_patterns():
    """Inject some attack patterns into the logs"""
    # Choose a random time for the attack
    attack_time = start_date + (end_date - start_date) * random.random()
    attack_user = random.choice(["attacker", "hacker", "anonymous"])
    attack_ip = random.choice(suspicious_ips)
    
    for i in range(random.randint(50, 100)):  # Attack sequence
        timestamp = (attack_time + timedelta(seconds=i*0.3)).isoformat()
        request_id = f"req-{uuid.uuid4().hex[:8]}"
        
        # Access log - brute force login attempts
        access_data.append([
            timestamp,
            attack_user,
            "/api/login",
            "POST",
            401,
            request_id
        ])
        
        # Execution log - failed attempts
        execution_data.append([
            timestamp,
            "login_handler",
            random.randint(100, 500),
            "FAILED",
            request_id
        ])
        
        # VPC log - rejected connections
        vpc_data.append([
            timestamp,
            attack_ip,
            random.choice(normal_ips),
            "REJECT",
            random.randint(100, 500),
            request_id
        ])

# Add some data exfiltration pattern
def add_exfiltration():
    """Inject data exfiltration pattern"""
    exfiltration_time = start_date + (end_date - start_date) * random.random()
    malicious_user = random.choice(admin_users)  # Insider threat
    malicious_ip = random.choice(["192.168.1.100", "10.0.0.15"])  # Internal malicious
    
    for i in range(random.randint(10, 30)):  # Data exfiltration
        timestamp = (exfiltration_time + timedelta(minutes=i*5)).isoformat()
        request_id = f"req-{uuid.uuid4().hex[:8]}"
        
        # Access log - data access
        access_data.append([
            timestamp,
            malicious_user,
            "/api/data",
            "GET",
            200,
            request_id
        ])
        
        # Execution log
        execution_data.append([
            timestamp,
            "data_processor",
            random.randint(2000, 5000),
            "SUCCESS",
            request_id
        ])
        
        # VPC log - large data transfers
        vpc_data.append([
            timestamp,
            malicious_ip,
            random.choice(suspicious_ips),
            "ACCEPT",  # Might not be caught
            random.randint(100000, 500000),  # Large transfers
            request_id
        ])

# Inject attack patterns
add_attack_patterns()
add_exfiltration()

# Shuffle each log independently but keep related entries together
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

print(f"✅ {len(access_data)} diversified & realistic logs saved to:")
print(f" - {access_log_file}")
print(f" - {execution_log_file}")
print(f" - {vpc_log_file}")
print("\nIncludes:")
print("- 3 months of historical data with recent bias")
print("- Realistic user activity patterns")
print("- Anomalies (5% of entries)")
print("- Attack patterns (brute force, data exfiltration)")
print("- Suspicious internal behavior")
print("- Business hours traffic patterns")