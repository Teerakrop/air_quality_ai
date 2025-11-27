#!/usr/bin/env python3
"""
Debug System for Air Quality AI
Checks system status and dependencies
"""

import sys
import subprocess
import importlib
import psutil
from pathlib import Path

def check_python_packages():
    """Check if required Python packages are installed"""
    required_packages = [
        'numpy', 'pandas', 'scikit-learn', 'matplotlib', 
        'dash', 'flask', 'pyserial', 'psutil'
    ]
    
    print("🔍 Checking Python packages...")
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Install missing packages with:")
        print(f"pip3 install {' '.join(missing_packages)}")
    
    return len(missing_packages) == 0

def check_system_resources():
    """Check system resources"""
    print("\n💻 System Resources:")
    
    # Memory
    memory = psutil.virtual_memory()
    print(f"RAM: {memory.used/1024**3:.1f}GB / {memory.total/1024**3:.1f}GB ({memory.percent:.1f}%)")
    
    # Disk
    disk = psutil.disk_usage('/')
    print(f"Disk: {disk.used/1024**3:.1f}GB / {disk.total/1024**3:.1f}GB ({disk.percent:.1f}%)")
    
    # CPU
    cpu_percent = psutil.cpu_percent(interval=1)
    print(f"CPU: {cpu_percent:.1f}%")
    
    return True

def check_serial_ports():
    """Check available serial ports"""
    print("\n📡 Serial Ports:")
    
    import glob
    ports = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
    
    if ports:
        for port in ports:
            print(f"✅ {port}")
    else:
        print("❌ No serial ports found")
    
    return len(ports) > 0

def main():
    print("🔧 Air Quality AI System Debug")
    print("=" * 40)
    
    all_good = True
    
    # Check packages
    if not check_python_packages():
        all_good = False
    
    # Check resources
    check_system_resources()
    
    # Check serial ports
    check_serial_ports()
    
    print("\n" + "=" * 40)
    if all_good:
        print("✅ System looks good! Ready to run Air Quality AI")
    else:
        print("⚠️  Some issues detected. Please fix them before running.")

if __name__ == "__main__":
    main()
