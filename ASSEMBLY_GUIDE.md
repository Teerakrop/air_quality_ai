# 🔧 คู่มือการประกอบระบบ Air Quality AI

## 📋 รายการอุปกรณ์ที่ต้องใช้

### ฮาร์ดแวร์หลัก
- **NVIDIA Jetson Nano** (4GB Developer Kit)
- **ESP32 Development Board**
- **SDS011 PM2.5/PM10 Sensor** (เซ็นเซอร์ฝุ่นละออง)
- **DHT22** (เซ็นเซอร์อุณหภูมิและความชื้น)
- **MQ-135** (เซ็นเซอร์แก๊สคุณภาพอากาศ)
- **Breadboard Power Supply Module** (3.3V/5V)

### อุปกรณ์เสริม
- **Jumper Wires** (สายไฟต่อ)
- **USB Cable** (Micro USB สำหรับ ESP32)
- **Breadboard** (ถ้าต้องการ)
- **ตัวต้านทาน 10kΩ** (สำหรับ DHT22)

### เครื่องมือ
- ไขควงขนาดเล็ก
- คีมปอกสาย
- มัลติมิเตอร์ (สำหรับตรวจสอบ)

---

## 🔌 แผนผังการเชื่อมต่อ

### 📐 Schematic Diagram

```
                    JETSON NANO
                  ┌─────────────────┐
                  │  Pin 2 (5V)     │──┐
                  │  Pin 6 (GND)    │──┼──┐
                  │  USB Port       │  │  │
                  └─────────┬───────┘  │  │
                           │          │  │
                           │ USB      │  │
                           │          │  │
                  ┌────────▼──────────┐ │  │
                  │      ESP32        │ │  │
                  │ ┌───────────────┐ │ │  │
                  │ │ GPIO4    VIN  │◄┼─┘  │
                  │ │ GPIO16   GND  │◄┼────┘
                  │ │ GPIO17        │ │
                  │ │ GPIO36        │ │
                  │ └───────────────┘ │
                  └─┬─┬─┬─┬───────────┘
                    │ │ │ │
        ┌───────────┘ │ │ └─────────────┐
        │             │ │               │
        ▼             │ │               ▼
   ┌─────────┐        │ │        ┌──────────┐
   │  DHT22  │        │ │        │  MQ-135  │
   │ ┌─────┐ │        │ │        │ ┌──────┐ │
   │ │ VCC │◄┼────────┼─┼────────┼►│ VCC  │ │
   │ │Data │◄┼────────┘ │        │ │ AOUT │◄┼─┘
   │ │ GND │◄┼──────────┼────────┼►│ GND  │ │
   │ └─────┘ │          │        │ └──────┘ │
   └─────────┘          │        └──────────┘
                        │
                        ▼
                 ┌─────────────┐
                 │   SDS011    │
                 │ ┌─────────┐ │
                 │ │ 5V  (1) │◄┼─┐
                 │ │ GND (2) │◄┼─┼──┐
                 │ │ RX  (6) │◄┼─┘  │
                 │ │ TX  (7) │◄┼─┐  │
                 │ └─────────┘ │ │  │
                 └─────────────┘ │  │
                                 │  │
        ┌────────────────────────┘  │
        │ ┌─────────────────────────┘
        │ │
        ▼ ▼
┌─────────────────┐
│ Power Supply    │
│ Module          │
│ ┌─────────────┐ │
│ │ 5V IN   5V  │ │
│ │ GND IN  3.3V│ │
│ │         GND │ │
│ └─────────────┘ │
└─────────────────┘
        ▲ ▲
        │ └─── GND (Pin 6)
        └───── 5V (Pin 2)
```

### 🔧 Connection Summary

**ESP32 GPIO Pinout:**
```
ESP32 Pin    →    Connected To
─────────────────────────────────
GPIO4        →    DHT22 Data Pin
GPIO16       →    SDS011 RX (Pin 6)
GPIO17       →    SDS011 TX (Pin 7)
GPIO36       →    MQ-135 AOUT
VIN          →    5V Power Rail
GND          →    Ground Rail
USB          →    Jetson Nano USB Port
```

**Power Distribution:**
```
Source           →    Destination
─────────────────────────────────────
Jetson Pin 2     →    Power Module 5V IN
Jetson Pin 6     →    Power Module GND IN
Power 5V OUT     →    SDS011 Pin 1, ESP32 VIN
Power 3.3V OUT   →    DHT22 VCC, MQ-135 VCC
Power GND OUT    →    All GND connections
```

---

## 🛠️ ขั้นตอนการประกอบ

### ขั้นตอนที่ 1: เตรียมพื้นฐาน

**1.1 ตรวจสอบอุปกรณ์**
- [ ] ตรวจสอบอุปกรณ์ครบตามรายการ
- [ ] ตรวจสอบสายไฟไม่ขาดหรือเสียหาย
- [ ] เตรียมพื้นที่ทำงานที่สะอาดและปลอดไฟฟ้าสถิต

**1.2 เตรียม Jetson Nano**
- [ ] ติดตั้ง JetPack OS บน microSD card
- [ ] เสียบ microSD card เข้า Jetson Nano
- [ ] เชื่อมต่อ keyboard, mouse, monitor
- [ ] เชื่อมต่อ Ethernet หรือ WiFi

### ขั้นตอนที่ 2: การติดตั้ง Power Supply

**2.1 Power Supply Module Diagram**
```
    Breadboard Power Supply Module
   ┌─────────────────────────────┐
   │  INPUT     │    OUTPUT      │
   │ ┌────────┐ │ ┌────────────┐ │
   │ │ 5V IN  │◄┼─┤ 5V    3.3V │ │
   │ │ GND IN │◄┼─┤ GND   GND  │ │
   │ └────────┘ │ └────────────┘ │
   │     ▲      │       ▲        │
   │     │      │       │        │
   │   Power    │     Power      │
   │   Input    │     Rails      │
   └─────┼──────┴───────┼────────┘
         │              │
         │              └── To Sensors
         │
    From Jetson Nano
    Pin 2 (5V) & Pin 6 (GND)

Jetson Nano GPIO Pinout (40-pin):
┌─────────────────────────────────┐
│  1○ ○2   ← Pin 2 (5V)           │
│  3○ ○4                          │
│  5○ ○6   ← Pin 6 (GND)          │
│  7○ ○8                          │
│  9○ ○10                         │
│ 11○ ○12                         │
│ 13○ ○14                         │
│ 15○ ○16                         │
│ 17○ ○18                         │
│ 19○ ○20                         │
│ 21○ ○22                         │
│ 23○ ○24                         │
│ 25○ ○26                         │
│ 27○ ○28                         │
│ 29○ ○30                         │
│ 31○ ○32                         │
│ 33○ ○34                         │
│ 35○ ○36                         │
│ 37○ ○38                         │
│ 39○ ○40                         │
└─────────────────────────────────┘
```

**2.2 เชื่อมต่อ Breadboard Power Supply**
```
Jetson Nano → Power Supply Module
├── Pin 2 (5V) → Input VIN
├── Pin 6 (GND) → Input GND
└── ตรวจสอบ LED สีเขียวติด
```

**2.2 ทดสอบแรงดันไฟฟ้า**
- [ ] ใช้มัลติมิเตอร์วัด 5V rail = 5.0V ±0.2V
- [ ] ใช้มัลติมิเตอร์วัด 3.3V rail = 3.3V ±0.1V
- [ ] ตรวจสอบ GND ต่อเนื่องกัน

### ขั้นตอนที่ 3: การเชื่อมต่อ ESP32

**3.1 ESP32 Pinout Diagram**
```
                    ESP32 Development Board
                  ┌─────────────────────────────┐
                  │                             │
           3V3 ○──┤                             ├──○ VIN (5V)
           GND ○──┤                             ├──○ GND
            D15 ○──┤                             ├──○ D13
            D2  ○──┤                             ├──○ D12
            D4  ○──┤◄── DHT22 Data               ├──○ D14
           D16  ○──┤◄── SDS011 TX                ├──○ D27
           D17  ○──┤◄── SDS011 RX                ├──○ D26
            D5  ○──┤                             ├──○ D25
           D18  ○──┤                             ├──○ D33
           D19  ○──┤                             ├──○ D32
           D21  ○──┤                             ├──○ D35
            D3  ○──┤                             ├──○ D34
            D1  ○──┤                             ├──○ VN
            D0  ○──┤                             ├──○ VP
                  │                             │
           GND ○──┤                             ├──○ D36 ◄── MQ-135 AOUT
                  │         [USB Port]         │
                  └─────────────┬───────────────┘
                               │
                               ▼
                        To Jetson Nano USB
```

**3.2 Power Connection**
```
ESP32 ← Power Rails
├── VIN ← 5V Rail (สายแดง)
├── GND ← GND Rail (สายดำ)
└── ตรวจสอบ LED บน ESP32 ติด
```

**3.2 USB Connection**
```
ESP32 ← USB Cable → Jetson Nano
└── Micro USB ← USB Type-A Port
```

**3.3 ทดสอบการเชื่อมต่อ**
```bash
# ตรวจสอบ ESP32 ถูกตรวจพบ
ls /dev/ttyUSB* /dev/ttyACM*
# ควรเห็น /dev/ttyUSB0 หรือ /dev/ttyACM0
```

### ขั้นตอนที่ 4: การเชื่อมต่อ DHT22

**4.1 DHT22 Pin Diagram**
```
     DHT22 (Front View)
    ┌─────────────────┐
    │  ┌─┐ ┌─┐ ┌─┐ ┌─┐│
    │  │1│ │2│ │3│ │4││
    │  └─┘ └─┘ └─┘ └─┘│
    └─────────────────┘
       │   │   │   │
       │   │   │   └── GND (สายดำ)
       │   │   └────── NC (ไม่ต่อ)
       │   └────────── Data (สายเหลือง → GPIO4)
       └────────────── VCC (สายแดง → 3.3V)
```

**4.1 Pin Identification**
```
DHT22 Pinout (มองจากด้านหน้า):
├── Pin 1: VCC (3.3V-5V)
├── Pin 2: Data
├── Pin 3: NC (ไม่ใช้)
└── Pin 4: GND
```

**4.2 Wiring**
```
DHT22 → ESP32/Power
├── Pin 1 (VCC) → 3.3V Rail (สายแดง)
├── Pin 2 (Data) → ESP32 GPIO4 (สายเหลือง)
├── Pin 3 (NC) → ไม่ต่อ
└── Pin 4 (GND) → GND Rail (สายดำ)
```

**4.3 Pull-up Resistor (แนะนำ)**
- ต่อตัวต้านทาน 10kΩ ระหว่าง VCC และ Data pin
- ช่วยให้สัญญาณเสถียรขึ้น

### ขั้นตอนที่ 5: การเชื่อมต่อ MQ-135

**5.1 MQ-135 Module Diagram**
```
    MQ-135 Gas Sensor Module
   ┌─────────────────────────┐
   │    ┌─────────────┐      │
   │    │   Sensor    │      │
   │    │   (Round)   │      │
   │    └─────────────┘      │
   │  VCC GND AOUT DOUT     │
   │   │   │   │    │       │
   └───┼───┼───┼────┼───────┘
       │   │   │    │
       │   │   │    └── DOUT (ไม่ต่อ)
       │   │   └─────── AOUT (สายเขียว → GPIO36)
       │   └─────────── GND (สายดำ)
       └─────────────── VCC (สายแดง → 3.3V)
```

**5.1 Module Identification**
```
MQ-135 Module Pins:
├── VCC: Power Input (3.3V-5V)
├── GND: Ground
├── AOUT: Analog Output
└── DOUT: Digital Output (ไม่ใช้)
```

**5.2 Wiring**
```
MQ-135 → ESP32/Power
├── VCC → 3.3V Rail (สายแดง)
├── GND → GND Rail (สายดำ)
├── AOUT → ESP32 GPIO36 (สายเขียว)
└── DOUT → ไม่ต่อ
```

**5.3 หมายเหตุ**
- MQ-135 ต้องอุ่นเครื่อง 24-48 ชั่วโมงเพื่อความแม่นยำ
- ในช่วงแรกค่าอาจไม่เสถียร

### ขั้นตอนที่ 6: การเชื่อมต่อ SDS011

**6.1 SDS011 Connector Diagram**
```
        SDS011 PM2.5/PM10 Sensor
       ┌─────────────────────────┐
       │        ┌─────┐          │
       │        │ Fan │          │
       │        └─────┘          │
       │                        │
       │  7-Pin Connector       │
       │  ┌─┬─┬─┬─┬─┬─┬─┐       │
       └──┤1│2│3│4│5│6│7├───────┘
          └─┴─┴─┴─┴─┴─┴─┘
           │ │ │ │ │ │ │
           │ │ │ │ │ │ └── Pin 7: TX (สายขาว → GPIO17)
           │ │ │ │ │ └──── Pin 6: RX (สายเขียว → GPIO16)
           │ │ │ │ └────── Pin 5: GND (สายดำ)
           │ │ │ └──────── Pin 4: 10μm (ไม่ต่อ)
           │ │ └────────── Pin 3: 25μm (ไม่ต่อ)
           │ └──────────── Pin 2: GND (สายดำ)
           └────────────── Pin 1: 5V (สายแดง → 5V)
```

**6.1 Pin Identification**
```
SDS011 7-Pin Connector:
├── Pin 1: 5V (แดง)
├── Pin 2: GND (ดำ)
├── Pin 3: 25μm (ไม่ใช้)
├── Pin 4: 10μm (ไม่ใช้)
├── Pin 5: GND (ดำ)
├── Pin 6: RX (เขียว)
└── Pin 7: TX (ขาว)
```

**6.2 Wiring**
```
SDS011 → ESP32/Power
├── Pin 1 (5V) → 5V Rail (สายแดง)
├── Pin 2 (GND) → GND Rail (สายดำ)
├── Pin 5 (GND) → GND Rail (สายดำ)
├── Pin 6 (RX) → ESP32 GPIO16 (สายเขียว)
└── Pin 7 (TX) → ESP32 GPIO17 (สายขาว)
```

**6.3 ทดสอบ**
- [ ] ตรวจสอบพัดลมใน SDS011 หมุน
- [ ] ไม่มีเสียงผิดปกติ
- [ ] LED สถานะ (ถ้ามี) ติดปกติ

---

## 🔍 การตรวจสอบและทดสอบ

### Checklist การต่อสาย
```
✅ Power Connections:
   - 5V Rail: 5.0V ±0.2V
   - 3.3V Rail: 3.3V ±0.1V
   - GND: ต่อเนื่องทุกจุด

✅ ESP32:
   - Power LED ติด
   - USB ตรวจพบใน /dev/
   - GPIO pins ไม่สั้น

✅ DHT22:
   - VCC = 3.3V
   - Data → GPIO4
   - Pull-up resistor ติดตั้ง

✅ MQ-135:
   - VCC = 3.3V  
   - AOUT → GPIO36
   - ไม่มีกลิ่นไหม้

✅ SDS011:
   - VCC = 5V
   - พัดลมหมุน
   - Serial pins ถูกต้อง
```

### การทดสอบเบื้องต้น

**1. ทดสอบ Power Supply**
```bash
# ใช้มัลติมิเตอร์วัดแรงดัน
# 5V rail ควรได้ 4.8-5.2V
# 3.3V rail ควรได้ 3.2-3.4V
```

**2. ทดสอบ ESP32**
```bash
# ตรวจสอบ Serial Port
ls /dev/ttyUSB* /dev/ttyACM*

# ทดสอบการสื่อสาร
screen /dev/ttyUSB0 115200
# หรือ
minicom -D /dev/ttyUSB0 -b 115200
```

**3. ทดสอบเซ็นเซอร์**
```bash
# รันสคริปต์ทดสอบ
python sensor_interface.py

# ควรเห็นข้อมูลแบบนี้:
# DHT22: Temperature=25.4°C, Humidity=65.2%
# MQ-135: Gas Level=150
# SDS011: PM2.5=12.5μg/m³, PM10=18.3μg/m³
```

---

## 🚨 การแก้ปัญหา

### ปัญหาที่พบบ่อย

**1. ESP32 ไม่ตรวจพบ**
```
สาเหตุ:
- สาย USB เสียหาย
- Driver ไม่ถูกต้อง
- พอร์ต USB ไม่มีไฟ

วิธีแก้:
- เปลี่ยนสาย USB
- ติดตั้ง CH340/CP2102 driver
- ลองพอร์ต USB อื่น
```

**2. เซ็นเซอร์ไม่มีข้อมูล**
```
DHT22:
- ตรวจสาย Data และ Pull-up resistor
- ตรวจแรงดันไฟฟ้า 3.3V

MQ-135:
- รอให้อุ่นเครื่อง 5-10 นาที
- ตรวจ AOUT connection

SDS011:
- ตรวจพัดลมหมุนหรือไม่
- ตรวจ Serial connection (RX/TX)
- ตรวจแรงดันไฟฟ้า 5V
```

**3. ค่าผิดปกติ**
```
อุณหภูมิ/ความชื้น:
- DHT22 อาจเสียหาย
- การต่อสายผิด
- สัญญาณรบกวน

PM2.5/PM10:
- SDS011 ต้องอุ่นเครื่อง 30 วินาที
- ทำความสะอาดเซ็นเซอร์
- ตรวจสอบสภาพแวดล้อม

Gas Level:
- MQ-135 ต้องอุ่นเครื่อง 24-48 ชั่วโมง
- Calibration ในอากาศสะอาด
- ตรวจสอบ ADC connection
```

### Emergency Shutdown
```
หากเกิดปัญหา:
1. ถอดสาย USB ESP32 ทันที
2. ปิดไฟ Jetson Nano
3. ตรวจสอบการต่อสายทั้งหมด
4. ใช้มัลติมิเตอร์ตรวจสอบ short circuit
5. เริ่มต้นใหม่ทีละขั้นตอน
```

---

## 📦 การติดตั้งซอฟต์แวร์

### 1. เตรียม Jetson Nano
```bash
# อัปเดตระบบ
sudo apt update && sudo apt upgrade -y

# ติดตั้ง Python dependencies
sudo apt install python3-pip python3-venv git -y

# โคลนโปรเจค
git clone <repository-url>
cd air_quality_ai

# สร้าง virtual environment
python3 -m venv venv
source venv/bin/activate

# ติดตั้ง Python packages
pip install -r requirements.txt
```

### 2. เตรียม ESP32
```bash
# ติดตั้ง Arduino IDE
# ดาวน์โหลดจาก: https://www.arduino.cc/en/software

# เพิ่ม ESP32 Board Manager:
# File → Preferences → Additional Board Manager URLs
# เพิ่ม: https://dl.espressif.com/dl/package_esp32_index.json

# ติดตั้งไลบรารี:
# - ArduinoJson
# - DHT sensor library
# - EspSoftwareSerial
```

### 3. อัปโหลดโค้ด ESP32
```
1. เปิดไฟล์ esp32_sensor_code.ino
2. เลือกบอร์ด: "ESP32 Dev Module"
3. เลือกพอร์ต: /dev/ttyUSB0
4. กด Upload
5. รอจนเสร็จ (ประมาณ 1-2 นาที)
```

### 4. ทดสอบระบบ
```bash
# ทดสอบเซ็นเซอร์
python sensor_interface.py

# รันระบบเต็มรูปแบบ
python main.py

# รันเฉพาะเว็บไซต์
python start_website.py
```

---

## 🎯 การใช้งาน

### เริ่มต้นระบบ
```bash
# วิธีที่ 1: เมนูแบบอินเทอร์แอคทีฟ
python run_system.py

# วิธีที่ 2: รันโดยตรง
python main.py                    # ระบบเต็มรูปแบบ
python main.py --mock            # โหมดทดสอบ
python main.py --dashboard-only  # เฉพาะเว็บไซต์

# วิธีที่ 3: เว็บไซต์อย่างเดียว
python start_website.py
```

### เข้าถึงเว็บไซต์
- **Local**: http://localhost:8050
- **Network**: http://[jetson-ip]:8050
- **อัปเดตอัตโนมัติ**: ทุก 30 วินาที

### ข้อมูลที่แสดง
- 📊 **ค่าปัจจุบัน**: PM2.5, PM10, อุณหภูมิ, ความชื้น
- 📈 **กราฟแนวโน้ม**: 24 ชั่วโมงย้อนหลัง
- 🔮 **การพยากรณ์**: 1-6 ชั่วโมงข้างหน้า
- 🎯 **ความแม่นยำ**: ประสิทธิภาพโมเดล AI

---

## 📚 เอกสารเพิ่มเติม

- [README.md](README.md) - ข้อมูลโปรเจคโดยรวม
- [esp32_sensor_code.ino](esp32_sensor_code.ino) - โค้ด Arduino
- [config.py](config.py) - การตั้งค่าระบบ
- [requirements.txt](requirements.txt) - Python dependencies

---

## 🆘 การขอความช่วยเหลือ

หากพบปัญหา:
1. ตรวจสอบ [การแก้ปัญหา](#-การแก้ปัญหา) ในเอกสารนี้
2. ดูไฟล์ log ใน `logs/` directory
3. ตรวจสอบการต่อสายตาม checklist
4. รันคำสั่งทดสอบทีละขั้นตอน

**ข้อมูลที่ควรรวมเมื่อรายงานปัญหา:**
- รุ่น Jetson Nano และ JetPack version
- ข้อความ error แบบเต็ม
- ขั้นตอนที่ทำก่อนเกิดปัญหา
- ผลการทดสอบแต่ละเซ็นเซอร์

---

*สร้างด้วย ❤️ เพื่ออากาศที่สะอาดและสุขภาพที่ดีขึ้น*
