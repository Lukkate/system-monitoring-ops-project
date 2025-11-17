import os
import socket
import psutil
from datetime import datetime
import subprocess
import requests

def check_port(host, port, timeout=2):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((host, port))
        sock.close()
        return True
    except Exception:
        return False
    
# Thresholds สำหรับ Alerting (Phase 3)
# Thresholds สำหรับ Alerting (Phase 3 + Severity)
CPU_WARN = 80.0      # WARNING เริ่มที่ 80%
CPU_CRIT = 90.0      # CRITICAL ถ้าเกิน 90%
# CPU_WARN = 0.01      # TESTING
# CPU_CRIT = 0.10      # CRITICAL ถ้าเกิน 90%

RAM_WARN = 80.0
RAM_CRIT = 90.0
# RAM_WARN = 1.0     # TESTING

DISK_WARN = 85.0
DISK_CRIT = 95.0
# DISK_WARN = 0.01   # TESTING

PING_WARN = 100.0    # ms
PING_CRIT = 300.0    # ms
# PING_WARN = 5      # TESTING


# Telegram config
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")
TG_API_URL = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage" if TG_BOT_TOKEN else None

def send_telegram_alert(message: str):
    """ส่งข้อความแจ้งเตือนไปยัง Telegram chat ที่กำหนด"""
    if not TG_BOT_TOKEN or not TG_CHAT_ID or not TG_API_URL:
        return  # ถ้ายังไม่ได้ตั้งค่า env ครบ ก็ไม่ต้องส่งอะไร

    data = {
        "chat_id": TG_CHAT_ID,
        "text": message,
    }

    try:
        requests.post(TG_API_URL, data=data, timeout=5)
    except Exception as e:
        print("[TELEGRAM ERROR]", e)

# ======================
# System Info
# ======================
hostname = socket.gethostname()
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

cpu_usage = psutil.cpu_percent(interval=1)
ram_usage = psutil.virtual_memory().percent
disk_usage = psutil.disk_usage('/').percent

# ======================
# Ping Check
# ======================
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

# ======================
# Port Check (DNS port 53)
# ======================
port_ok = check_port("8.8.8.8", 53)

if port_ok:
    port_part = " PORT_53=OK"
else:
    port_part = " PORT_53=FAIL"

# ======================
# DNS Resolve
# ======================
dns_host = "google.com"
try:
    dns_ip = socket.gethostbyname(dns_host)
    dns_part = f" DNS={dns_ip}"
except Exception:
    dns_part = " DNS=FAIL"

# ======================
# Create Log Line (health.log)
# ======================
log_line = (
    f"{timestamp} HOST={hostname} "
    f"CPU={cpu_usage} RAM={ram_usage} Disk={disk_usage}"
    f"{ping_part}{port_part}{dns_part}\n"
)

print(log_line)

with open("health.log", "a") as f:
    f.write(log_line)

# ======================
# Alerting Logic (Phase 3)
# ======================
alerts = []  # เก็บเป็น list ของ (level, message)

# CPU
if cpu_usage > CPU_CRIT:
    alerts.append(("CRITICAL", f"CPU high: {cpu_usage:.1f}% > {CPU_CRIT}%"))
elif cpu_usage > CPU_WARN:
    alerts.append(("WARNING", f"CPU high: {cpu_usage:.1f}% > {CPU_WARN}%"))

# RAM
if ram_usage > RAM_CRIT:
    alerts.append(("CRITICAL", f"RAM high: {ram_usage:.1f}% > {RAM_CRIT}%"))
elif ram_usage > RAM_WARN:
    alerts.append(("WARNING", f"RAM high: {ram_usage:.1f}% > {RAM_WARN}%"))

# Disk
if disk_usage > DISK_CRIT:
    alerts.append(("CRITICAL", f"Disk usage high: {disk_usage:.1f}% > {DISK_CRIT}%"))
elif disk_usage > DISK_WARN:
    alerts.append(("WARNING", f"Disk usage high: {disk_usage:.1f}% > {DISK_WARN}%"))

# Ping
if ping_ms is None:
    alerts.append(("CRITICAL", "Ping failed: cannot reach 8.8.8.8"))
else:
    if ping_ms > PING_CRIT:
        alerts.append(("CRITICAL", f"High latency: {ping_ms:.2f} ms > {PING_CRIT} ms"))
    elif ping_ms > PING_WARN:
        alerts.append(("WARNING", f"High latency: {ping_ms:.2f} ms > {PING_WARN} ms"))

# Port 53
if not port_ok:
    alerts.append(("CRITICAL", "Port 53 (DNS) is not reachable"))

# DNS resolve
if "DNS=FAIL" in dns_part:
    alerts.append(("CRITICAL", "DNS resolve failed for google.com"))


if alerts:
    # เขียนลง alerts.log + print
    with open("alerts.log", "a") as af:
        for level, msg in alerts:
            alert_line = f"{timestamp} HOST={hostname} LEVEL={level} {msg}\n"
            af.write(alert_line)
            print(f"[ALERT][{level}] {msg}")
    # ส่ง Telegram alert
    lines = []
    lines.append(f"🚨 ALERT on {hostname}")
    lines.append(f"🕒 {timestamp}")
    lines.append("")  # เว้นบรรทัด

    for level, msg in alerts:
        if level == "CRITICAL":
            emoji = "🔴"
        elif level == "WARNING":
            emoji = "🟠"
        else:
            emoji = "ℹ️"
        lines.append(f"{emoji} [{level}] {msg}")

    alert_text = "\n".join(lines)
    send_telegram_alert(alert_text)
