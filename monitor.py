import socket
import psutil
from datetime import datetime
import subprocess

def check_port(host, port, timeout=2):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((host, port))
        sock.close()
        return True
    except Exception:
        return False

# System Info
hostname = socket.gethostname() 
# print("Host:", hostname) 
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
# print("Timestamp:", timestamp) 
cpu_usage = psutil.cpu_percent(interval=1) 
# print("CPU:", cpu_usage) 
ram_usage = psutil.virtual_memory().percent 
# print("RAM:", ram_usage) 
disk_usage = psutil.disk_usage('/').percent 
# print("Disk:", disk_usage)

# Ping Check
result = subprocess.run(
    ["ping", "-c", "1", "8.8.8.8"],
    capture_output=True,
    text=True
)

ping_output = result.stdout
ping_ms = None

for line in ping_output.splitlines():
    if "time=" in line:
        part = line.split("time=")[1]
        value_str = part.split(" ")[0] 
        ping_ms = float(value_str)
        break

if ping_ms is not None:
    ping_part = f" PING_MS={ping_ms}"
else:
    ping_part = " PING_MS=FAIL"
# Port Check (DNS port 53)
port_ok = check_port("8.8.8.8", 53)

if port_ok:
    port_part = " PORT_53=OK"
else:
    port_part = " PORT_53=FAIL"

dns_host = "google.com"
try:
    dns_ip = socket.gethostbyname(dns_host)
    dns_part = f" DNS={dns_ip}"
except Exception:
    dns_part = " DNS=FAIL"

# Create Log Line
log_line = (
    f"{timestamp} HOST={hostname} "
    f"CPU={cpu_usage} RAM={ram_usage} Disk={disk_usage}"
    f"{ping_part}{port_part}{dns_part}\n"
)

print(log_line)

with open("health.log", "a") as f:
    f.write(log_line) 
