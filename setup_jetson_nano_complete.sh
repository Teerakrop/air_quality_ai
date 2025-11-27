#!/bin/bash
# 🚀 Complete Setup Script for Air Quality AI on Jetson Nano
# One-click installation and setup for 119GB SD card
# Usage: bash setup_jetson_nano_complete.sh

set -e  # Exit on any error

# Colors for beautiful output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo -e "\n${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC} ${CYAN}$1${NC} ${BLUE}║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}\n"
}

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${PURPLE}ℹ️  $1${NC}"
}

# Welcome banner
echo -e "${CYAN}"
cat << "EOF"
    🌬️  Air Quality AI - Jetson Nano Complete Setup  🤖
    ═══════════════════════════════════════════════════════
    
    This script will automatically:
    ✅ Check system compatibility
    ✅ Install all dependencies
    ✅ Optimize for 119GB SD card
    ✅ Configure Jetson Nano performance
    ✅ Set up the complete Air Quality system
    
    Ready to transform your Jetson Nano! 🚀
EOF
echo -e "${NC}\n"

# Confirm installation
read -p "🤔 Do you want to proceed with the complete setup? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "👋 Setup cancelled. Come back when you're ready!"
    exit 0
fi

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please don't run this script as root!"
    print_info "The script will use sudo when needed."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    print_error "Please run this script from the air_quality_ai directory"
    print_info "Usage: cd air_quality_ai && bash setup_jetson_nano_complete.sh"
    exit 1
fi

# ============================================================================
# STEP 1: System Detection and Resource Check
# ============================================================================
print_header "🔍 SYSTEM DETECTION & RESOURCE CHECK"

# Detect Jetson Nano
JETSON_DETECTED=false
if [ -f "/etc/nv_tegra_release" ] || grep -q "jetson\|tegra" /proc/cpuinfo 2>/dev/null; then
    print_status "Jetson Nano detected!"
    JETSON_DETECTED=true
else
    print_warning "Not running on Jetson Nano, but continuing anyway..."
fi

# Check system resources
TOTAL_MEM=$(free -g | awk 'NR==2{print $2}')
FREE_MEM=$(free -g | awk 'NR==2{print $7}')
FREE_DISK=$(df -BG / | awk 'NR==2{gsub(/G/,"",$4); print $4}')

print_info "System Resources:"
echo "   💾 Total RAM: ${TOTAL_MEM}GB"
echo "   🆓 Available RAM: ${FREE_MEM}GB"  
echo "   💿 Free Disk: ${FREE_DISK}GB"

# Check if we have enough space (need at least 10GB free)
if [ "$FREE_DISK" -lt 10 ]; then
    print_error "Not enough disk space! Need at least 10GB free."
    print_info "Current free space: ${FREE_DISK}GB"
    
    read -p "🧹 Do you want to clean up the system first? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Cleaning up system..."
        sudo apt autoremove -y
        sudo apt autoclean
        sudo journalctl --vacuum-time=7d
        print_status "System cleanup completed"
    else
        print_error "Please free up some disk space and try again"
        exit 1
    fi
fi

# ============================================================================
# STEP 2: System Update and Basic Dependencies
# ============================================================================
print_header "🔄 SYSTEM UPDATE & BASIC DEPENDENCIES"

print_info "Updating package lists..."
sudo apt update

print_info "Installing essential build tools..."
sudo apt install -y \
    python3-pip python3-dev python3-venv \
    build-essential cmake git curl wget \
    software-properties-common

print_status "Basic dependencies installed"

# ============================================================================
# STEP 3: Memory Optimization (Swap Setup)
# ============================================================================
print_header "💾 MEMORY OPTIMIZATION"

# Setup swap for better performance (2GB for 119GB SD card)
SWAP_FILE="/swapfile_air_quality"
SWAP_SIZE="2G"  # Reduced for SD card longevity

if swapon --show | grep -q "$SWAP_FILE"; then
    print_status "Swap file already exists"
else
    print_info "Creating ${SWAP_SIZE} swap file for better performance..."
    
    sudo fallocate -l $SWAP_SIZE $SWAP_FILE
    sudo chmod 600 $SWAP_FILE
    sudo mkswap $SWAP_FILE
    sudo swapon $SWAP_FILE
    
    # Make it permanent
    if ! grep -q "$SWAP_FILE" /etc/fstab; then
        echo "$SWAP_FILE none swap sw 0 0" | sudo tee -a /etc/fstab
    fi
    
    # Optimize swap usage for SD card
    echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
    echo 'vm.vfs_cache_pressure=50' | sudo tee -a /etc/sysctl.conf
    
    print_status "Swap file created and optimized for SD card"
fi

# ============================================================================
# STEP 4: Scientific Computing Libraries (System Packages)
# ============================================================================
print_header "🧮 SCIENTIFIC COMPUTING LIBRARIES"

print_info "Installing system scientific packages (faster and more stable)..."

# Install scientific libraries from system packages
sudo apt install -y \
    python3-numpy python3-pandas python3-matplotlib \
    python3-scipy python3-sklearn python3-serial \
    libhdf5-serial-dev hdf5-tools libhdf5-dev \
    libatlas-base-dev gfortran \
    libjpeg-dev libpng-dev libtiff-dev

print_status "Scientific libraries installed"

# ============================================================================
# STEP 5: Web Framework and Additional Python Packages
# ============================================================================
print_header "🌐 WEB FRAMEWORK & PYTHON PACKAGES"

print_info "Upgrading pip..."
python3 -m pip install --user --upgrade pip setuptools wheel

print_info "Installing web framework packages..."

# Install packages one by one with progress indication
packages=(
    "dash==2.14.1"
    "dash-bootstrap-components==1.5.0" 
    "plotly==5.17.0"
    "flask==2.3.3"
    "pyserial==3.5"
    "schedule==1.2.0"
    "psutil==5.9.5"
    "tqdm==4.66.1"
    "python-dotenv==1.0.0"
    "joblib==1.3.2"
)

total_packages=${#packages[@]}
current=0

for package in "${packages[@]}"; do
    current=$((current + 1))
    print_info "Installing $package ($current/$total_packages)..."
    
    python3 -m pip install --user --timeout=600 "$package" || {
        print_warning "Failed to install $package, trying with --no-cache-dir..."
        python3 -m pip install --user --no-cache-dir --timeout=600 "$package"
    }
done

print_status "All Python packages installed successfully"

# ============================================================================
# STEP 6: TensorFlow Setup (Optional)
# ============================================================================
print_header "🧠 TENSORFLOW SETUP (OPTIONAL)"

echo "TensorFlow enables advanced LSTM models but requires more resources."
echo "For 119GB SD card, we recommend skipping TensorFlow to save space."
echo "The system will work perfectly with Random Forest models only."
echo

read -p "🤖 Do you want to install TensorFlow? (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Installing TensorFlow for Jetson Nano..."
    
    # Try to install TensorFlow for Jetson Nano
    python3 -m pip install --user --pre --extra-index-url \
        https://developer.download.nvidia.com/compute/redist/jp/v461 \
        tensorflow || {
        print_warning "TensorFlow installation failed. Installing TensorFlow Lite instead..."
        python3 -m pip install --user tflite-runtime
    }
    
    print_status "TensorFlow setup completed"
else
    print_info "Skipping TensorFlow installation (recommended for SD card)"
    
    # Create a flag file to disable TensorFlow
    echo "TENSORFLOW_DISABLED=True" > .env
    print_status "TensorFlow disabled, system will use Random Forest only"
fi

# ============================================================================
# STEP 7: Jetson Nano Performance Optimization
# ============================================================================
print_header "⚡ JETSON NANO PERFORMANCE OPTIMIZATION"

if [ "$JETSON_DETECTED" = true ]; then
    print_info "Applying Jetson Nano specific optimizations..."
    
    # Enable maximum performance mode
    if command -v jetson_clocks >/dev/null 2>&1; then
        sudo jetson_clocks || print_warning "Could not enable jetson_clocks"
        print_status "Jetson clocks enabled"
    fi
    
    # Set power mode to maximum (mode 0)
    if command -v nvpmodel >/dev/null 2>&1; then
        sudo nvpmodel -m 0 || print_warning "Could not set power mode"
        print_status "Power mode set to maximum performance"
    fi
    
    # Optimize for SD card usage
    echo 'kernel.printk = 3 4 1 3' | sudo tee -a /etc/sysctl.conf
    
    print_status "Jetson Nano optimizations applied"
else
    print_info "Skipping Jetson-specific optimizations (not detected)"
fi

# ============================================================================
# STEP 8: Create Startup Scripts and Shortcuts
# ============================================================================
print_header "📝 CREATING STARTUP SCRIPTS"

# Create main startup script
cat > start_air_quality_system.sh << 'EOF'
#!/bin/bash
# 🌬️ Air Quality AI System Launcher

cd "$(dirname "$0")"

echo "🌬️ Air Quality AI System Starting..."
echo "=================================="

# Check system status
echo "📊 System Status:"
echo "   💾 Memory: $(free -h | awk 'NR==2{print $3"/"$2}')"
echo "   💿 Disk: $(df -h / | awk 'NR==2{print $3"/"$2" ("$5" used)"}')"

# Check if ESP32 is connected
if ls /dev/ttyUSB* /dev/ttyACM* 1> /dev/null 2>&1; then
    echo "   🔌 ESP32: Connected"
    echo
    echo "🚀 Starting with real sensors..."
    python3 main.py
else
    echo "   🔌 ESP32: Not detected"
    echo
    echo "🧪 Starting with mock sensors (demo mode)..."
    python3 main.py --mock
fi
EOF

# Create dashboard-only script
cat > start_dashboard_only.sh << 'EOF'
#!/bin/bash
# 📊 Air Quality Dashboard Only

cd "$(dirname "$0")"

echo "📊 Air Quality Dashboard Starting..."
echo "===================================="
echo
echo "🌐 Dashboard will be available at:"
echo "   http://localhost:8050"
echo "   http://$(hostname -I | awk '{print $1}'):8050"
echo
echo "📱 Open the URL above in your browser"
echo "🛑 Press Ctrl+C to stop the dashboard"
echo

python3 start_website.py
EOF

# Create system test script
cat > test_system.sh << 'EOF'
#!/bin/bash
# 🧪 System Test Script

cd "$(dirname "$0")"

echo "🧪 Testing Air Quality AI System..."
echo "==================================="

# Test Python imports
echo "📦 Testing Python packages..."
python3 -c "
try:
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import sklearn
    print('✅ Scientific packages: OK')
    
    import dash
    import plotly
    import flask
    print('✅ Web packages: OK')
    
    import serial
    import schedule
    import psutil
    print('✅ System packages: OK')
    
    # Test system modules
    import config
    import sensor_interface
    import data_logger
    print('✅ System modules: OK')
    
    print('\n🎉 All tests passed! System is ready to use.')
    
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
except Exception as e:
    print(f'❌ System error: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo
    echo "🚀 System test completed successfully!"
    echo "   You can now run: ./start_air_quality_system.sh"
else
    echo
    echo "❌ System test failed. Please check the installation."
fi
EOF

# Create maintenance script
cat > maintenance.sh << 'EOF'
#!/bin/bash
# 🧹 System Maintenance Script

cd "$(dirname "$0")"

echo "🧹 Air Quality AI - System Maintenance"
echo "======================================"

# Show system status
echo "📊 Current System Status:"
echo "   💾 Memory: $(free -h | awk 'NR==2{print $3"/"$2" ("$5" used)"}')"
echo "   💿 Disk: $(df -h / | awk 'NR==2{print $3"/"$2" ("$5" used)"}')"
echo "   🔄 Swap: $(free -h | awk 'NR==3{print $2}')"

# Check data directory size
if [ -d "data" ]; then
    DATA_SIZE=$(du -sh data | cut -f1)
    DATA_FILES=$(find data -name "*.csv" | wc -l)
    echo "   📁 Data: $DATA_SIZE ($DATA_FILES files)"
fi

echo
echo "🛠️ Maintenance Options:"
echo "1. Clean old data (>30 days)"
echo "2. Clean system cache"
echo "3. Update system packages"
echo "4. Check model files"
echo "5. View system logs"
echo "6. Exit"

read -p "Choose option (1-6): " choice

case $choice in
    1)
        echo "🧹 Cleaning old data..."
        python3 main.py --maintenance
        ;;
    2)
        echo "🧹 Cleaning system cache..."
        sudo apt autoremove -y
        sudo apt autoclean
        python3 -m pip cache purge
        ;;
    3)
        echo "🔄 Updating system packages..."
        sudo apt update && sudo apt upgrade -y
        ;;
    4)
        echo "🤖 Checking model files..."
        ls -lh models/ 2>/dev/null || echo "No model files found"
        ;;
    5)
        echo "📋 Recent system logs:"
        tail -n 20 logs/*.log 2>/dev/null || echo "No log files found"
        ;;
    6)
        echo "👋 Goodbye!"
        ;;
    *)
        echo "❌ Invalid option"
        ;;
esac
EOF

# Make all scripts executable
chmod +x start_air_quality_system.sh
chmod +x start_dashboard_only.sh
chmod +x test_system.sh
chmod +x maintenance.sh

print_status "Startup scripts created"

# ============================================================================
# STEP 9: Create Desktop Shortcuts (if GUI available)
# ============================================================================
print_header "🖥️ CREATING DESKTOP SHORTCUTS"

if [ -d "$HOME/Desktop" ] && [ -n "$DISPLAY" ]; then
    print_info "Creating desktop shortcuts..."
    
    # Air Quality System shortcut
    cat > "$HOME/Desktop/Air Quality System.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Air Quality AI System
Comment=Start the complete Air Quality monitoring system
Exec=$(pwd)/start_air_quality_system.sh
Icon=applications-science
Terminal=true
Categories=Science;Education;
StartupNotify=true
Path=$(pwd)
EOF

    # Dashboard shortcut
    cat > "$HOME/Desktop/Air Quality Dashboard.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Air Quality Dashboard
Comment=Open the Air Quality web dashboard
Exec=$(pwd)/start_dashboard_only.sh
Icon=applications-internet
Terminal=true
Categories=Network;Science;
StartupNotify=true
Path=$(pwd)
EOF

    chmod +x "$HOME/Desktop/Air Quality System.desktop"
    chmod +x "$HOME/Desktop/Air Quality Dashboard.desktop"
    
    print_status "Desktop shortcuts created"
else
    print_info "No desktop environment detected, skipping shortcuts"
fi

# ============================================================================
# STEP 10: Final System Test
# ============================================================================
print_header "🧪 FINAL SYSTEM TEST"

print_info "Running comprehensive system test..."

# Run the test script
bash test_system.sh

# ============================================================================
# STEP 11: Create Quick Reference Guide
# ============================================================================
print_header "📚 CREATING QUICK REFERENCE"

cat > QUICK_START_GUIDE.md << 'EOF'
# 🚀 Air Quality AI - Quick Start Guide

## 🎯 How to Use Your System

### 🌟 Main Commands
```bash
# Start the complete system
./start_air_quality_system.sh

# Start dashboard only
./start_dashboard_only.sh

# Test the system
./test_system.sh

# Run maintenance
./maintenance.sh
```

### 🌐 Web Access
- **Local**: http://localhost:8050
- **Network**: http://YOUR_JETSON_IP:8050

### 📊 System Status
- **Data Location**: `data/` folder
- **Models**: `models/` folder  
- **Logs**: `logs/` folder

### 🔧 Troubleshooting
1. **No ESP32 detected**: System will run in demo mode
2. **Low memory**: Restart system or run maintenance
3. **Dashboard not loading**: Check if port 8050 is free

### 🛠️ Manual Commands
```bash
# With real sensors
python3 main.py

# With mock sensors (demo)
python3 main.py --mock

# Dashboard only
python3 main.py --dashboard-only

# Run maintenance
python3 main.py --maintenance
```

### 📱 Mobile Access
Open your phone browser and go to:
`http://YOUR_JETSON_IP:8050`

---
*System optimized for Jetson Nano with 119GB SD card*
EOF

print_status "Quick reference guide created"

# ============================================================================
# COMPLETION MESSAGE
# ============================================================================
print_header "🎉 INSTALLATION COMPLETED SUCCESSFULLY!"

echo -e "${GREEN}"
cat << "EOF"
    ╔══════════════════════════════════════════════════════════════╗
    ║                    🎉 SUCCESS! 🎉                           ║
    ║                                                              ║
    ║  Your Air Quality AI system is now ready to use!            ║
    ║                                                              ║
    ║  🚀 Quick Start:                                             ║
    ║     ./start_air_quality_system.sh                           ║
    ║                                                              ║
    ║  📊 Dashboard Only:                                          ║
    ║     ./start_dashboard_only.sh                               ║
    ║                                                              ║
    ║  🧪 Test System:                                             ║
    ║     ./test_system.sh                                        ║
    ║                                                              ║
    ║  🌐 Web Dashboard: http://localhost:8050                    ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

print_info "Installation Summary:"
echo "   📦 All dependencies installed"
echo "   💾 Memory optimized for 119GB SD card"
echo "   ⚡ Jetson Nano performance optimized"
echo "   📝 Startup scripts created"
echo "   🖥️ Desktop shortcuts ready (if GUI available)"
echo "   📚 Quick start guide available"

echo
print_info "Next Steps:"
echo "   1. Connect your ESP32 sensor (optional)"
echo "   2. Run: ./start_air_quality_system.sh"
echo "   3. Open http://localhost:8050 in browser"
echo "   4. Enjoy your AI-powered air quality monitoring!"

echo
print_warning "💡 Tips:"
echo "   • System will work in demo mode without ESP32"
echo "   • Dashboard updates every 30 seconds"
echo "   • Run ./maintenance.sh periodically"
echo "   • Check QUICK_START_GUIDE.md for more info"

echo
echo -e "${CYAN}🌬️ Happy monitoring! Your air quality AI system is ready! 🤖${NC}"
