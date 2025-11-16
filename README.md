# Server & Network Monitoring System (Python)

โปรเจกต์นี้เป็นสคริปต์สำหรับตรวจสอบสถานะของเครื่องเซิร์ฟเวอร์และเครือข่ายแบบเบื้องต้น  
สามารถเก็บข้อมูลการใช้งานของระบบ เช่น CPU, RAM, Disk  
รวมถึงตรวจสอบสถานะของเครือข่าย เช่น Ping, Port Health และ DNS Resolve

สคริปต์จะบันทึกเวลา (Timestamp) และชื่อเครื่อง (Hostname)  
จากนั้นรวบรวมผลทั้งหมดลงไฟล์ Log เพื่อใช้ตรวจสอบย้อนหลังได้

ระบบรองรับการตั้งค่า Cronjob สำหรับการรันอัตโนมัติทุก 5 นาที  
------------------------------------------------------------------------

## ฟีเจอร์

### Phase 1 — System Monitoring

-   ตรวจสอบการใช้งาน CPU
-   ตรวจสอบการใช้งาน RAM
-   ตรวจสอบการใช้งาน Disk
-   เก็บ Timestamp (รูปแบบ YYYY-MM-DD HH:MM:SS)
-   เก็บ Hostname (ชื่อเครื่อง)

### ระบบ Log

สคริปต์จะบันทึก Log ลงไฟล์ `health.log` ในรูปแบบ:

    2024-01-13 21:50:10 HOST=SERVER CPU=2.1 RAM=30 Disk=0.4
    
### Shell Script (run_monitor.sh)

ใช้สำหรับ: 
- เข้าโฟลเดอร์โปรเจกต์
- เปิดใช้งาน Virtual Environment (venv)
- รันสคริปต์ monitor.py
- ให้ cronjob เรียกใช้งานได้อย่างถูกต้อง

### Cronjob Automation

รันสคริปต์ทุก **5 นาที** อัตโนมัติ และเก็บผลลัพธ์ลง `cron.log`

------------------------------------------------------------------------

### Phase 2 — Network Monitoring

เพิ่มการตรวจสอบสถานะ Network เพื่อให้ระบบ Monitoring ครบวงจรมากขึ้น:

#### Ping Monitoring
- ping ไปที่ `8.8.8.8`
- ดึงค่า latency (ms)
- ใช้วิธี parse `time=xx.x ms` จากผลลัพธ์คำสั่ง `ping`

#### Port Health Check
- ตรวจสอบว่า port ยังเปิดให้เชื่อมต่อได้หรือไม่  
- ตัวอย่างในโปรเจกต์: DNS port `53` ของ `8.8.8.8`  
- หากเชื่อมต่อสำเร็จ → `OK`  
- หากเชื่อมต่อไม่ได้ → `FAIL`

#### DNS Resolve Check
- ตรวจสอบว่า DNS สามารถแปลงชื่อโดเมน เช่น `google.com` เป็น IP ได้หรือไม่  
- หาก resolve สำเร็จ → แสดง IP  
- หากล้มเหลว → `DNS=FAIL`

#### ตัวอย่าง Log (Phase 2)
    2025-11-17 00:07:01 HOST=LAPTOP-RSFDD4SJ CPU=0.5 RAM=31.8 Disk=0.4 PING_MS=9.35 PORT_53=OK DNS=142.250.204.142


------------------------------------------------------------------------
## การทำงานของระบบ (Phase 1)
1. **Cronjob** ทำการเรียกใช้งานทุก 5 นาที  
2. **run_monitor.sh** ทำหน้าที่:
   - เข้าโฟลเดอร์โปรเจกต์
   - เปิดใช้งาน Virtual Environment
   - รันสคริปต์ monitor.py  
3. **monitor.py** เก็บข้อมูล CPU, RAM, Disk, Timestamp, Hostname  
4. บันทึกผลลงไฟล์ **health.log** แบบ append  

------------------------------------------------------------------------

## โครงสร้างโปรเจกต์

    ops_project/
    │
    ├── monitor.py
    ├── run_monitor.sh
    ├── requirements.txt
    ├── .gitignore
    └── README.md

> หมายเหตุ: โฟลเดอร์ `venv/` และไฟล์ `.log` ไม่รวมใน Git

------------------------------------------------------------------------

## monitor.py ทำอะไรบ้าง?
### System Metrics (Phase 1)
-   อ่านข้อมูล CPU, RAM, Disk
-   อ่าน Timestamp ปัจจุบัน
-   อ่าน Hostname ของเครื่อง
-   สร้าง log line และบันทึกลงไฟล์ `health.log`

ตัวอย่าง:

    2024-01-13 21:50:10 HOST=SERVER CPU=2.1 RAM=30 Disk=0.4

###  Network Monitoring (Phase 2)
- **Ping Monitoring**: ping ไปยัง `8.8.8.8` และดึงค่า latency (ms)
- **Port Health Check**: ตรวจสอบว่า port `53` (DNS) ยังเปิดอยู่หรือไม่
- **DNS Resolve Check**: แปลงชื่อโดเมน เช่น `google.com` เป็น IP address

ตัวอย่าง Log (Phase 2):

    2025-11-17 00:07:01 HOST=LAPTOP-RSFDD4SJ CPU=0.5 RAM=31.8 Disk=0.4 PING_MS=9.35 PORT_53=OK DNS=142.250.204.142


------------------------------------------------------------------------

## Shell Script (run_monitor.sh)

ใช้โดย Cronjob:

``` bash
#!/bin/bash
cd /home/<your_user>/ops_project
source venv/bin/activate
python monitor.py
```

------------------------------------------------------------------------

## ตั้งค่า Cronjob (ทุก 5 นาที)

รันคำสั่ง:

    crontab -e

เพิ่มบรรทัดนี้:

    */5 * * * * cd /home/<your_user>/ops_project && ./run_monitor.sh >> cron.log 2>&1

------------------------------------------------------------------------

## การติดตั้ง (สำหรับผู้ใช้ที่ clone โปรเจกต์)

ติดตั้ง dependencies ด้วย:

    pip install -r requirements.txt

------------------------------------------------------------------------

## สิ่งที่อาจพัฒนาเพิ่มเติมในอนาคต

### Alerting (พื้นฐาน)
- ส่ง LINE Notify แบบง่าย เมื่อ CPU/Network มีปัญหา

### Dashboard (อาจพัฒนาเพิ่มเติม เป็นส่วนเสริม)
- หน้าเว็บเล็ก ๆ แสดงค่าต่าง ๆ

------------------------------------------------------------------------
