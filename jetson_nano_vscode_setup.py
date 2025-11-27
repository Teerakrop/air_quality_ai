#!/usr/bin/env python3
"""
Jetson Nano VS Code Setup Script
Optimizes the Air Quality AI project for VS Code 1.68.1 on Jetson Nano
"""

import os
import sys
import subprocess
import json
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JetsonVSCodeSetup:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.vscode_dir = self.project_root / '.vscode'
        
    def check_system_requirements(self):
        """Check if system meets requirements"""
        logger.info("🔍 Checking system requirements...")
        
        # Check Python version
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 6):
            logger.error("❌ Python 3.6+ required")
            return False
        logger.info(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Check if running on Jetson Nano
        try:
            with open('/etc/nv_tegra_release', 'r') as f:
                tegra_info = f.read()
                if 'tegra' in tegra_info.lower():
                    logger.info("✅ Running on NVIDIA Jetson platform")
                else:
                    logger.warning("⚠️  Not running on Jetson platform")
        except FileNotFoundError:
            logger.warning("⚠️  Could not detect Jetson platform")
        
        # Check available memory
        try:
            import psutil
            memory = psutil.virtual_memory()
            memory_gb = memory.total / (1024**3)
            logger.info(f"✅ Available RAM: {memory_gb:.1f} GB")
            
            if memory_gb < 3:
                logger.warning("⚠️  Low memory detected. Some features may be limited.")
        except ImportError:
            logger.warning("⚠️  Could not check memory (psutil not installed)")
        
        return True
    
    def setup_vscode_workspace(self):
        """Setup VS Code workspace settings"""
        logger.info("⚙️  Setting up VS Code workspace...")
        
        # Create workspace file
        workspace_config = {
            "folders": [
                {
                    "name": "Air Quality AI",
                    "path": "."
                }
            ],
            "settings": {
                "python.defaultInterpreterPath": "/usr/bin/python3",
                "python.terminal.activateEnvironment": False,
                "files.watcherExclude": {
                    "**/data/**": True,
                    "**/models/**": True,
                    "**/logs/**": True,
                    "**/__pycache__/**": True
                }
            },
            "extensions": {
                "recommendations": [
                    "ms-python.python",
                    "ms-toolsai.jupyter",
                    "ms-python.flake8"
                ]
            }
        }
        
        workspace_file = self.project_root / 'air_quality_ai.code-workspace'
        with open(workspace_file, 'w') as f:
            json.dump(workspace_config, f, indent=4)
        
        logger.info(f"✅ Workspace file created: {workspace_file}")
    
    def optimize_for_jetson(self):
        """Apply Jetson Nano specific optimizations"""
        logger.info("🚀 Applying Jetson Nano optimizations...")
        
        # Create performance script
        performance_script = self.project_root / 'jetson_performance.sh'
        script_content = """#!/bin/bash
# Jetson Nano Performance Optimization Script

echo "🚀 Optimizing Jetson Nano for Air Quality AI..."

# Enable maximum performance mode
if command -v jetson_clocks &> /dev/null; then
    echo "⚡ Enabling jetson_clocks..."
    sudo jetson_clocks
else
    echo "⚠️  jetson_clocks not found"
fi

# Set power mode to maximum (MAXN)
if command -v nvpmodel &> /dev/null; then
    echo "🔋 Setting power mode to MAXN..."
    sudo nvpmodel -m 0
else
    echo "⚠️  nvpmodel not found"
fi

# Increase swap if needed
SWAP_SIZE=$(free | grep Swap | awk '{print $2}')
if [ "$SWAP_SIZE" -lt 4194304 ]; then
    echo "💾 Creating 4GB swap file..."
    sudo fallocate -l 4G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
fi

# Optimize GPU memory
echo "🎮 Optimizing GPU memory..."
echo 'export TF_FORCE_GPU_ALLOW_GROWTH=true' >> ~/.bashrc

echo "✅ Jetson Nano optimization completed!"
"""
        
        with open(performance_script, 'w') as f:
            f.write(script_content)
        
        # Make script executable
        os.chmod(performance_script, 0o755)
        logger.info(f"✅ Performance script created: {performance_script}")
    
    def create_development_scripts(self):
        """Create helpful development scripts"""
        logger.info("📝 Creating development scripts...")
        
        # Quick start script
        start_script = self.project_root / 'quick_start.sh'
        start_content = """#!/bin/bash
# Quick Start Script for Air Quality AI on Jetson Nano

echo "🚀 Starting Air Quality AI System..."

# Check if VS Code is available
if command -v code &> /dev/null; then
    echo "📝 Opening project in VS Code..."
    code air_quality_ai.code-workspace
else
    echo "⚠️  VS Code not found. Opening in default editor..."
fi

# Activate performance mode
if [ -f "jetson_performance.sh" ]; then
    echo "⚡ Applying performance optimizations..."
    bash jetson_performance.sh
fi

# Start the system
echo "🌟 Starting Air Quality AI with mock sensor..."
python3 main.py --mock

echo "✅ System started! Dashboard available at http://localhost:8050"
"""
        
        with open(start_script, 'w') as f:
            f.write(start_content)
        os.chmod(start_script, 0o755)
        
        # Debug script
        debug_script = self.project_root / 'debug_system.py'
        debug_content = '''#!/usr/bin/env python3
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
        print(f"\\n📦 Install missing packages with:")
        print(f"pip3 install {' '.join(missing_packages)}")
    
    return len(missing_packages) == 0

def check_system_resources():
    """Check system resources"""
    print("\\n💻 System Resources:")
    
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
    print("\\n📡 Serial Ports:")
    
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
    
    print("\\n" + "=" * 40)
    if all_good:
        print("✅ System looks good! Ready to run Air Quality AI")
    else:
        print("⚠️  Some issues detected. Please fix them before running.")

if __name__ == "__main__":
    main()
'''
        
        with open(debug_script, 'w') as f:
            f.write(debug_content)
        os.chmod(debug_script, 0o755)
        
        logger.info("✅ Development scripts created")
    
    def run_setup(self):
        """Run the complete setup process"""
        logger.info("🚀 Starting Jetson Nano VS Code setup...")
        
        if not self.check_system_requirements():
            logger.error("❌ System requirements not met")
            return False
        
        self.setup_vscode_workspace()
        self.optimize_for_jetson()
        self.create_development_scripts()
        
        logger.info("✅ Setup completed successfully!")
        logger.info("📝 Next steps:")
        logger.info("1. Run: bash jetson_performance.sh")
        logger.info("2. Install dependencies: pip3 install -r requirements_jetson_nano.txt")
        logger.info("3. Open VS Code: code air_quality_ai.code-workspace")
        logger.info("4. Start system: bash quick_start.sh")
        
        return True

def main():
    setup = JetsonVSCodeSetup()
    success = setup.run_setup()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
