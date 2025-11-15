import socket
import psutil
from datetime import datetime

hostname = socket.gethostname()
print("Host:", hostname)

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print("Timestamp:", timestamp)

cpu_usage = psutil.cpu_percent(interval=1)
print("CPU:", cpu_usage)

ram_usage = psutil.virtual_memory().percent
print("RAM:", ram_usage)

disk_usage = psutil.disk_usage('/').percent
print("Disk:", disk_usage)

log_line = f"{timestamp} HOST={hostname} CPU={cpu_usage} RAM={ram_usage} Disk={disk_usage}\n"
print(log_line)
with open("health.log", "a") as f:
    f.write(log_line)