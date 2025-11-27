# 💻 VS Code Setup Guide สำหรับ Jetson Nano

## 🎯 คู่มือการใช้งาน VS Code 1.68.1 บน Jetson Nano

ไฟล์นี้เป็นคู่มือเฉพาะสำหรับการใช้งาน VS Code กับโปรเจค Air Quality AI บน Jetson Nano

## 🚀 การติดตั้งและตั้งค่า

### ขั้นตอนที่ 1: ติดตั้ง VS Code บน Jetson Nano

```bash
# ดาวน์โหลด VS Code สำหรับ ARM64
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/
sudo sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'

sudo apt update
sudo apt install code
```

### ขั้นตอนที่ 2: Setup โปรเจค

```bash
# Clone และ setup โปรเจค
git clone https://github.com/yourusername/air_quality_ai.git
cd air_quality_ai

# รันสคริปต์ setup สำหรับ VS Code
python3 jetson_nano_vscode_setup.py

# เปิดโปรเจคใน VS Code
code air_quality_ai.code-workspace
```

## 🔧 การใช้งาน VS Code Features

### 1. **Launch Configurations**

กด `F5` หรือไปที่ Run and Debug panel เพื่อใช้งาน:

- 🚀 **Run Air Quality AI (Normal)** - รันระบบปกติ
- 🧪 **Run Air Quality AI (Mock Sensor)** - รันด้วยเซ็นเซอร์จำลอง
- 🌐 **Run Dashboard Only** - รันเฉพาะเว็บไซต์
- 🔧 **Run Maintenance** - รันการบำรุงรักษา
- 📊 **Test Data Logger** - ทดสอบระบบบันทึกข้อมูล
- 🤖 **Test ML Models** - ทดสอบโมเดล AI
- 📡 **Test Sensor Interface** - ทดสอบการเชื่อมต่อเซ็นเซอร์

### 2. **Tasks (Ctrl+Shift+P → Tasks: Run Task)**

- 🔧 **Install Dependencies (Jetson Nano)** - ติดตั้ง dependencies
- 📦 **Install Python Requirements** - ติดตั้งแพ็คเกจ Python
- 🚀 **Start Air Quality System** - เริ่มระบบ
- 🧪 **Start with Mock Sensor** - เริ่มด้วยเซ็นเซอร์จำลอง
- 🌐 **Start Dashboard Only** - เริ่มเฉพาะแดชบอร์ด
- 🔍 **Check System Status** - ตรวจสอบสถานะระบบ
- 🧹 **Clean Data Files** - ล้างไฟล์ข้อมูล
- ⚡ **Enable Jetson Performance Mode** - เปิดโหมดประสิทธิภาพสูง

### 3. **Extensions ที่แนะนำ**

VS Code จะแนะนำ extensions ที่เหมาะสมอัตโนมัติ:

- **ms-python.python** - Python support
- **ms-toolsai.jupyter** - Jupyter notebooks
- **ms-python.flake8** - Code linting
- **eamodio.gitlens** - Git integration
- **vsciot-vscode.vscode-arduino** - Arduino/ESP32 support

## 📊 การ Debug และ Monitor

### 1. **Debugging**

```python
# ตั้ง breakpoints ในโค้ด
# กด F5 เพื่อเริ่ม debugging
# ใช้ Debug Console เพื่อตรวจสอบตัวแปร
```

### 2. **Terminal Integration**

```bash
# เปิด terminal ใน VS Code (Ctrl+`)
# รันคำสั่งต่างๆ ได้โดยตรง

# ตรวจสอบสถานะระบบ
python3 debug_system.py

# เริ่มระบบแบบ quick
bash quick_start.sh

# ตรวจสอบ performance
sudo tegrastats
```

### 3. **File Watching**

VS Code ได้รับการปรับแต่งให้ไม่ watch ไฟล์ที่ไม่จำเป็น:
- ไฟล์ข้อมูล (`data/`)
- โมเดล AI (`models/`)
- Log files (`logs/`)
- Cache files (`__pycache__/`)

## ⚡ การปรับแต่งประสิทธิภาพ

### 1. **Jetson Performance Mode**

```bash
# เปิดใช้งานประสิทธิภาพสูงสุด
bash jetson_performance.sh

# หรือใช้ task ใน VS Code
# Ctrl+Shift+P → Tasks: Run Task → Enable Jetson Performance Mode
```

### 2. **Memory Management**

```python
# ระบบได้รับการปรับแต่งให้ใช้หน่วยความจำอย่างมีประสิทธิภาพ
# - ลด batch size สำหรับ LSTM
# - จำกัดจำนวน CPU cores
# - เปิดใช้ GPU memory growth
```

### 3. **Development Settings**

```json
// .vscode/settings.json ได้รับการปรับแต่งแล้ว
{
    "python.defaultInterpreterPath": "/usr/bin/python3",
    "files.watcherExclude": {
        "**/data/**": true,
        "**/models/**": true,
        "**/logs/**": true
    }
}
```

## 🧪 การทดสอบ

### 1. **Quick Testing**

```bash
# ทดสอบระบบด้วยเซ็นเซอร์จำลอง
# กด F5 → เลือก "Run Air Quality AI (Mock Sensor)"

# หรือใช้ terminal
python3 main.py --mock
```

### 2. **Component Testing**

```bash
# ทดสอบแต่ละส่วน
python3 sensor_interface.py  # ทดสอบเซ็นเซอร์
python3 ml_models.py         # ทดสอบโมเดล AI
python3 data_logger.py       # ทดสอบการบันทึกข้อมูล
```

### 3. **System Debugging**

```bash
# ตรวจสอบสถานะระบบ
python3 debug_system.py

# ตรวจสอบ dependencies
python3 -c "import numpy, pandas, sklearn, dash; print('All good!')"
```

## 🔧 Troubleshooting

### ปัญหาที่พบบ่อย

1. **VS Code ช้า**
   ```bash
   # ลด file watching
   # ปิด extensions ที่ไม่จำเป็น
   # เปิด performance mode
   bash jetson_performance.sh
   ```

2. **Python Interpreter ไม่ถูกต้อง**
   ```bash
   # Ctrl+Shift+P → Python: Select Interpreter
   # เลือก /usr/bin/python3
   ```

3. **Serial Port ไม่พบ**
   ```bash
   # ตรวจสอบ USB connection
   ls /dev/ttyUSB* /dev/ttyACM*
   
   # เพิ่มสิทธิ์ user
   sudo usermod -a -G dialout $USER
   ```

4. **Memory Issues**
   ```bash
   # เพิ่ม swap space
   sudo fallocate -l 4G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

## 📚 เอกสารเพิ่มเติม

- [README.md](README.md) - คู่มือหลัก
- [JETSON_NANO_COMPATIBILITY.md](JETSON_NANO_COMPATIBILITY.md) - รายงานความเข้ากันได้
- [HARDWARE_DIAGRAM.md](HARDWARE_DIAGRAM.md) - แผนภาพฮาร์ดแวร์
- [Air_Quality_AI_Presentation.md](Air_Quality_AI_Presentation.md) - การนำเสนอโปรเจค

## 🎯 สรุป

VS Code 1.68.1 บน Jetson Nano สามารถรันโปรเจค Air Quality AI ได้อย่างสมบูรณ์ ระบบได้รับการปรับแต่งเฉพาะเพื่อให้ทำงานได้อย่างมีประสิทธิภาพบนแพลตฟอร์ม ARM และหน่วยความจำจำกัด

**Happy Coding! 🚀**
