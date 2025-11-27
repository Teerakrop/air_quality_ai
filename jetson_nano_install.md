# 🚀 คำแนะนำการติดตั้ง Python Packages บน Jetson Nano

## 🔧 เตรียมระบบ Jetson Nano

### ขั้นตอนที่ 1: อัปเดตระบบ
```bash
sudo apt update && sudo apt upgrade -y
sudo apt autoremove -y
```

### ขั้นตอนที่ 2: ติดตั้ง Dependencies พื้นฐาน
```bash
# Python development tools
sudo apt install python3-pip python3-dev python3-venv -y
sudo apt install build-essential cmake -y

# Scientific computing libraries
sudo apt install libhdf5-serial-dev hdf5-tools libhdf5-dev -y
sudo apt install libatlas-base-dev gfortran -y
sudo apt install libjpeg-dev libpng-dev libtiff-dev -y
sudo apt install libavcodec-dev libavformat-dev libswscale-dev -y
sudo apt install libgtk-3-dev libcanberra-gtk3-dev -y

# Serial communication
sudo apt install python3-serial -y
```

### ขั้นตอนที่ 3: เพิ่ม Swap Memory (สำคัญ!)
```bash
# เพิ่ม swap เพื่อป้องกัน out of memory
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# ทำให้ swap ถาวร
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# ตรวจสอบ
free -h
```

## 📦 การติดตั้ง Python Packages

### วิธีที่ 1: ใช้ System Packages (แนะนำสำหรับ Jetson Nano)
```bash
# ติดตั้งจาก apt repository (เร็วและเสถียร)
sudo apt install python3-numpy python3-pandas -y
sudo apt install python3-matplotlib python3-scipy -y
sudo apt install python3-sklearn python3-serial -y

# ติดตั้งที่เหลือด้วย pip
pip3 install --user dash dash-bootstrap-components
pip3 install --user plotly schedule psutil tqdm
pip3 install --user python-dotenv joblib
```

### วิธีที่ 2: ใช้ pip แบบระมัดระวัง
```bash
# อัปเกรด pip ก่อน
pip3 install --upgrade pip

# ติดตั้งทีละตัว พร้อม timeout ยาว
pip3 install --user --timeout=1000 numpy
pip3 install --user --timeout=1000 pandas
pip3 install --user --timeout=1000 matplotlib
pip3 install --user --timeout=1000 scikit-learn

# Web framework
pip3 install --user dash==2.14.1
pip3 install --user dash-bootstrap-components==1.5.0
pip3 install --user plotly==5.17.0
pip3 install --user flask==2.3.3

# Utilities
pip3 install --user pyserial==3.5
pip3 install --user schedule==1.2.0
pip3 install --user psutil==5.9.5
pip3 install --user tqdm==4.66.1
pip3 install --user python-dotenv==1.0.0
pip3 install --user joblib==1.3.2
```

### วิธีที่ 3: ใช้ Virtual Environment (แนะนำสำหรับการพัฒนา)
```bash
# สร้าง virtual environment
python3 -m venv ~/air_quality_venv
source ~/air_quality_venv/bin/activate

# อัปเกรด pip ใน venv
pip install --upgrade pip setuptools wheel

# ติดตั้ง packages
pip install numpy pandas matplotlib
pip install scikit-learn plotly joblib
pip install dash dash-bootstrap-components flask
pip install pyserial schedule psutil tqdm python-dotenv
```

## ⚠️ ข้อควรระวังสำหรับ Jetson Nano

### 1. หน่วยความจำ
```bash
# ตรวจสอบ RAM และ Swap
free -h

# หากไม่พอ ให้เพิ่ม swap
sudo swapon --show
```

### 2. TensorFlow บน Jetson Nano
```bash
# TensorFlow สำหรับ Jetson Nano (ถ้าต้องการ)
pip3 install --pre --extra-index-url https://developer.download.nvidia.com/compute/redist/jp/v461 tensorflow

# หรือใช้ TensorFlow Lite แทน
pip3 install --user tflite-runtime
```

### 3. การจัดการ Dependencies
```bash
# หากมีปัญหา dependency conflicts
pip3 install --user --force-reinstall --no-deps <package_name>

# ตรวจสอบ packages ที่ติดตั้งแล้ว
pip3 list --user
```

## 🧪 ทดสอบการติดตั้ง

### ทดสอบ Import Packages
```bash
python3 -c "
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sklearn
print('✅ Scientific packages OK')

import dash
import plotly
import flask
print('✅ Web packages OK')

import serial
import schedule
import psutil
print('✅ System packages OK')

print('🎉 All packages installed successfully!')
"
```

### ทดสอบระบบ Air Quality
```bash
cd ~/air_quality_ai
python3 -c "import dashboard; print('✅ Dashboard module OK')"
python3 start_website.py
```

## 🚨 การแก้ปัญหาที่พบบ่อย

### 1. Out of Memory Error
```bash
# เพิ่ม swap memory
sudo fallocate -l 6G /swapfile2
sudo chmod 600 /swapfile2
sudo mkswap /swapfile2
sudo swapon /swapfile2

# หรือติดตั้งทีละตัว
pip3 install --user --no-cache-dir numpy
```

### 2. Compilation Error
```bash
# ติดตั้ง pre-compiled wheels
pip3 install --user --only-binary=all numpy pandas matplotlib

# หรือใช้ system packages
sudo apt install python3-numpy python3-pandas python3-matplotlib
```

### 3. Permission Error
```bash
# ใช้ --user flag
pip3 install --user <package_name>

# หรือเปลี่ยน ownership
sudo chown -R $USER:$USER ~/.local/
```

### 4. SSL Certificate Error
```bash
# อัปเดต certificates
sudo apt update && sudo apt install ca-certificates -y

# หรือใช้ trusted host
pip3 install --trusted-host pypi.org --trusted-host pypi.python.org --user <package_name>
```

## 📋 Checklist การติดตั้ง

```bash
# 1. ตรวจสอบ Python version
python3 --version  # ควรเป็น 3.6+

# 2. ตรวจสอบ pip
pip3 --version

# 3. ตรวจสอบ memory
free -h

# 4. ตรวจสอบ disk space
df -h

# 5. ทดสอบ import
python3 -c "import numpy, pandas, dash, serial"

# 6. รันระบบ
cd ~/air_quality_ai
python3 start_website.py
```

## 🎯 คำสั่งติดตั้งแบบครบเซ็ต

### สำหรับ Jetson Nano (แนะนำ)
```bash
# ขั้นตอนที่ 1: เตรียมระบบ
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-dev python3-venv build-essential -y
sudo apt install libhdf5-serial-dev hdf5-tools libatlas-base-dev gfortran -y

# ขั้นตอนที่ 2: เพิ่ม swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# ขั้นตอนที่ 3: ติดตั้ง system packages
sudo apt install python3-numpy python3-pandas python3-matplotlib python3-scipy python3-sklearn -y

# ขั้นตอนที่ 4: ติดตั้ง web packages
pip3 install --user dash dash-bootstrap-components plotly flask
pip3 install --user pyserial schedule psutil tqdm python-dotenv joblib

# ขั้นตอนที่ 5: ทดสอบ
python3 -c "import numpy, pandas, dash, serial; print('✅ Installation successful!')"
```

## 💡 Tips สำหรับ Jetson Nano

1. **ใช้ --user flag**: ป้องกัน permission issues
2. **ติดตั้งทีละตัว**: ลดความเสี่ยง memory overflow
3. **ใช้ system packages**: เร็วกว่าและเสถียรกว่า
4. **เพิ่ม swap memory**: จำเป็นสำหรับ compilation
5. **ใช้ timeout ยาว**: compilation ใช้เวลานาน
6. **ตรวจสอบ temperature**: ป้องกัน thermal throttling

```bash
# ตรวจสอบอุณหภูมิ
sudo tegrastats

# เปิดใช้งาน performance mode
sudo jetson_clocks
```

---

*คำแนะนำนี้ทดสอบบน Jetson Nano 4GB Developer Kit พร้อม JetPack 4.6*
