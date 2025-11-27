#!/bin/bash
# Automated Installation Script for Air Quality AI on Jetson Nano
# Run with: bash install_jetson_nano.sh

set -e  # Exit on any error

echo "🚀 Air Quality AI - Jetson Nano Installation Script"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}$1${NC}"
}

# Check if running on Jetson Nano
check_jetson() {
    print_header "🔍 Checking if running on Jetson Nano..."
    
    if [ -f "/etc/nv_tegra_release" ] || grep -q "jetson\|tegra" /proc/cpuinfo 2>/dev/null; then
        print_status "Jetson Nano detected!"
        return 0
    else
        print_warning "Not running on Jetson Nano, but continuing anyway..."
        return 1
    fi
}

# Check system resources
check_resources() {
    print_header "💾 Checking system resources..."
    
    # Check available memory
    TOTAL_MEM=$(free -g | awk 'NR==2{print $2}')
    FREE_MEM=$(free -g | awk 'NR==2{print $7}')
    
    print_status "Total memory: ${TOTAL_MEM}GB"
    print_status "Available memory: ${FREE_MEM}GB"
    
    # Check disk space
    FREE_DISK=$(df -h / | awk 'NR==2{print $4}')
    print_status "Free disk space: $FREE_DISK"
    
    # Check if we need swap
    if [ "$TOTAL_MEM" -lt 6 ]; then
        print_warning "Low memory system detected. Will create swap file."
        return 1
    fi
    
    return 0
}

# Setup swap file
setup_swap() {
    print_header "🔄 Setting up swap file..."
    
    SWAP_FILE="/swapfile_air_quality"
    SWAP_SIZE="4G"
    
    # Check if swap already exists
    if swapon --show | grep -q "$SWAP_FILE"; then
        print_status "Swap file already exists"
        return 0
    fi
    
    print_status "Creating ${SWAP_SIZE} swap file..."
    
    # Create swap file
    sudo fallocate -l $SWAP_SIZE $SWAP_FILE
    sudo chmod 600 $SWAP_FILE
    sudo mkswap $SWAP_FILE
    sudo swapon $SWAP_FILE
    
    # Make it permanent
    if ! grep -q "$SWAP_FILE" /etc/fstab; then
        echo "$SWAP_FILE none swap sw 0 0" | sudo tee -a /etc/fstab
    fi
    
    print_status "Swap file created successfully"
}

# Update system
update_system() {
    print_header "🔄 Updating system packages..."
    
    sudo apt update
    sudo apt upgrade -y
    sudo apt autoremove -y
    
    print_status "System updated successfully"
}

# Install system dependencies
install_system_deps() {
    print_header "📦 Installing system dependencies..."
    
    # Essential build tools
    sudo apt install -y \
        python3-pip python3-dev python3-venv \
        build-essential cmake \
        git curl wget
    
    # Scientific computing libraries
    sudo apt install -y \
        libhdf5-serial-dev hdf5-tools libhdf5-dev \
        libatlas-base-dev gfortran \
        libjpeg-dev libpng-dev libtiff-dev \
        libavcodec-dev libavformat-dev libswscale-dev \
        libgtk-3-dev libcanberra-gtk3-dev
    
    # Python scientific packages (system versions for stability)
    sudo apt install -y \
        python3-numpy python3-pandas python3-matplotlib \
        python3-scipy python3-sklearn python3-serial
    
    print_status "System dependencies installed"
}

# Install Python packages
install_python_packages() {
    print_header "🐍 Installing Python packages..."
    
    # Upgrade pip
    python3 -m pip install --user --upgrade pip setuptools wheel
    
    # Install web framework packages
    python3 -m pip install --user --timeout=1000 \
        dash==2.14.1 \
        dash-bootstrap-components==1.5.0 \
        plotly==5.17.0 \
        flask==2.3.3
    
    # Install utility packages
    python3 -m pip install --user \
        pyserial==3.5 \
        schedule==1.2.0 \
        psutil==5.9.5 \
        tqdm==4.66.1 \
        python-dotenv==1.0.0 \
        joblib==1.3.2
    
    print_status "Python packages installed"
}

# Setup TensorFlow for Jetson Nano (optional)
setup_tensorflow() {
    print_header "🧠 Setting up TensorFlow (optional)..."
    
    read -p "Do you want to install TensorFlow for LSTM models? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Installing TensorFlow for Jetson Nano..."
        
        # Install TensorFlow for Jetson Nano
        python3 -m pip install --user --pre --extra-index-url \
            https://developer.download.nvidia.com/compute/redist/jp/v461 \
            tensorflow || {
            print_warning "TensorFlow installation failed. Installing TensorFlow Lite instead..."
            python3 -m pip install --user tflite-runtime
        }
    else
        print_status "Skipping TensorFlow installation"
    fi
}

# Apply Jetson Nano optimizations
optimize_jetson() {
    print_header "⚡ Applying Jetson Nano optimizations..."
    
    # Enable maximum performance mode
    if command -v jetson_clocks >/dev/null 2>&1; then
        sudo jetson_clocks || print_warning "Could not enable jetson_clocks"
        print_status "Jetson clocks enabled"
    fi
    
    # Set power mode to maximum
    if command -v nvpmodel >/dev/null 2>&1; then
        sudo nvpmodel -m 0 || print_warning "Could not set power mode"
        print_status "Power mode set to maximum"
    fi
    
    # Increase swap tendency (use swap less aggressively)
    echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
    
    print_status "Jetson optimizations applied"
}

# Create startup scripts
create_scripts() {
    print_header "📝 Creating startup scripts..."
    
    # Create quick start script
    cat > start_air_quality.sh << 'EOF'
#!/bin/bash
# Quick start script for Air Quality AI

cd "$(dirname "$0")"

echo "🌬️ Starting Air Quality AI System..."

# Check if ESP32 is connected
if ls /dev/ttyUSB* /dev/ttyACM* 1> /dev/null 2>&1; then
    echo "✅ Serial ports detected"
    python3 main.py
else
    echo "⚠️  No ESP32 detected, starting with mock sensors"
    python3 main.py --mock
fi
EOF
    
    chmod +x start_air_quality.sh
    
    # Create dashboard-only script
    cat > start_dashboard.sh << 'EOF'
#!/bin/bash
# Start only the dashboard

cd "$(dirname "$0")"

echo "📊 Starting Air Quality Dashboard..."
echo "Open http://localhost:8050 in your browser"

python3 start_website.py
EOF
    
    chmod +x start_dashboard.sh
    
    print_status "Startup scripts created"
}

# Test installation
test_installation() {
    print_header "🧪 Testing installation..."
    
    # Test Python imports
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
" || {
        print_error "Package import test failed!"
        return 1
    }
    
    # Test system components
    if python3 -c "import config; print('✅ Config module OK')" 2>/dev/null; then
        print_status "System modules OK"
    else
        print_warning "Some system modules may have issues"
    fi
    
    print_status "Installation test completed"
}

# Main installation function
main() {
    print_header "Starting installation process..."
    
    # Check if we're in the right directory
    if [ ! -f "main.py" ]; then
        print_error "Please run this script from the air_quality_ai directory"
        exit 1
    fi
    
    # Run installation steps
    check_jetson
    check_resources
    
    # Setup swap if needed
    if [ $? -eq 1 ]; then
        setup_swap
    fi
    
    update_system
    install_system_deps
    install_python_packages
    setup_tensorflow
    optimize_jetson
    create_scripts
    test_installation
    
    print_header "🎉 Installation completed successfully!"
    echo
    print_status "You can now start the system with:"
    echo "  ./start_air_quality.sh     - Full system with sensors"
    echo "  ./start_dashboard.sh       - Dashboard only"
    echo "  python3 main.py --mock     - Test with mock sensors"
    echo
    print_status "Dashboard will be available at: http://localhost:8050"
    echo
    print_warning "Reboot recommended to ensure all optimizations take effect"
}

# Run main function
main "$@"
