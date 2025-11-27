#!/usr/bin/env python3
"""
Jetson Nano Setup and Optimization Script
Automatically configures the system for optimal performance
"""

import os
import sys
import subprocess
import platform
import psutil
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JetsonNanoSetup:
    def __init__(self):
        self.is_jetson = self.detect_jetson_nano()
        
    def detect_jetson_nano(self):
        """Detect if running on Jetson Nano"""
        try:
            # Check for Jetson-specific files
            jetson_files = [
                '/etc/nv_tegra_release',
                '/sys/firmware/devicetree/base/model'
            ]
            
            for file_path in jetson_files:
                if os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        content = f.read().lower()
                        if 'jetson' in content or 'tegra' in content:
                            logger.info("Jetson Nano detected!")
                            return True
            
            # Check CPU info
            with open('/proc/cpuinfo', 'r') as f:
                cpu_info = f.read().lower()
                if 'tegra' in cpu_info or 'jetson' in cpu_info:
                    return True
                    
        except Exception as e:
            logger.warning(f"Could not detect Jetson Nano: {e}")
        
        return False
    
    def check_system_resources(self):
        """Check system resources and provide recommendations"""
        logger.info("Checking system resources...")
        
        # Memory check
        memory = psutil.virtual_memory()
        total_gb = memory.total / (1024**3)
        available_gb = memory.available / (1024**3)
        
        logger.info(f"Total RAM: {total_gb:.1f} GB")
        logger.info(f"Available RAM: {available_gb:.1f} GB")
        
        if total_gb < 6:  # Jetson Nano has 4GB
            logger.warning("Low memory system detected. Enabling memory optimizations.")
            return True
        
        # Disk space check
        disk = psutil.disk_usage('/')
        free_gb = disk.free / (1024**3)
        
        logger.info(f"Free disk space: {free_gb:.1f} GB")
        
        if free_gb < 5:
            logger.warning("Low disk space! Consider cleaning up.")
        
        # CPU check
        cpu_count = psutil.cpu_count()
        logger.info(f"CPU cores: {cpu_count}")
        
        return total_gb < 6
    
    def setup_swap(self, size_gb=4):
        """Setup swap file for memory management"""
        swap_file = '/swapfile_air_quality'
        
        try:
            # Check if swap already exists
            result = subprocess.run(['swapon', '--show'], capture_output=True, text=True)
            if swap_file in result.stdout:
                logger.info("Swap file already exists")
                return True
            
            logger.info(f"Creating {size_gb}GB swap file...")
            
            # Create swap file
            subprocess.run(['sudo', 'fallocate', '-l', f'{size_gb}G', swap_file], check=True)
            subprocess.run(['sudo', 'chmod', '600', swap_file], check=True)
            subprocess.run(['sudo', 'mkswap', swap_file], check=True)
            subprocess.run(['sudo', 'swapon', swap_file], check=True)
            
            # Make permanent
            with open('/etc/fstab', 'a') as f:
                f.write(f'{swap_file} none swap sw 0 0\n')
            
            logger.info("Swap file created successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create swap: {e}")
            return False
        except Exception as e:
            logger.error(f"Swap setup error: {e}")
            return False
    
    def optimize_jetson_performance(self):
        """Apply Jetson Nano performance optimizations"""
        if not self.is_jetson:
            logger.info("Not a Jetson Nano, skipping Jetson-specific optimizations")
            return
        
        logger.info("Applying Jetson Nano optimizations...")
        
        try:
            # Enable maximum performance mode
            subprocess.run(['sudo', 'jetson_clocks'], check=False)
            logger.info("Jetson clocks enabled")
            
            # Set power mode to maximum
            subprocess.run(['sudo', 'nvpmodel', '-m', '0'], check=False)
            logger.info("Power mode set to maximum")
            
        except Exception as e:
            logger.warning(f"Could not apply all Jetson optimizations: {e}")
    
    def install_system_packages(self):
        """Install system packages for better performance"""
        logger.info("Installing system packages...")
        
        packages = [
            'python3-numpy', 'python3-pandas', 'python3-matplotlib',
            'python3-scipy', 'python3-sklearn', 'python3-serial',
            'build-essential', 'cmake', 'libhdf5-serial-dev',
            'libatlas-base-dev', 'gfortran'
        ]
        
        try:
            # Update package list
            subprocess.run(['sudo', 'apt', 'update'], check=True)
            
            # Install packages
            cmd = ['sudo', 'apt', 'install', '-y'] + packages
            subprocess.run(cmd, check=True)
            
            logger.info("System packages installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install system packages: {e}")
            return False
    
    def setup_python_environment(self):
        """Setup Python environment with optimized packages"""
        logger.info("Setting up Python environment...")
        
        try:
            # Upgrade pip
            subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], check=True)
            
            # Install requirements
            if os.path.exists('requirements_jetson_nano.txt'):
                subprocess.run([
                    sys.executable, '-m', 'pip', 'install', '--user', 
                    '-r', 'requirements_jetson_nano.txt'
                ], check=True)
            else:
                # Fallback to basic requirements
                basic_packages = [
                    'dash', 'dash-bootstrap-components', 'plotly', 
                    'flask', 'pyserial', 'schedule', 'psutil', 
                    'tqdm', 'python-dotenv', 'joblib'
                ]
                
                for package in basic_packages:
                    subprocess.run([
                        sys.executable, '-m', 'pip', 'install', '--user', package
                    ], check=True)
            
            logger.info("Python packages installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install Python packages: {e}")
            return False
    
    def create_startup_script(self):
        """Create startup script for the Air Quality system"""
        script_content = '''#!/bin/bash
# Air Quality AI System Startup Script for Jetson Nano

cd /home/$USER/air_quality_ai

# Set environment variables
export PYTHONPATH=$PYTHONPATH:/home/$USER/.local/lib/python3.6/site-packages

# Start the system
python3 main.py --mock
'''
        
        try:
            with open('start_air_quality.sh', 'w') as f:
                f.write(script_content)
            
            os.chmod('start_air_quality.sh', 0o755)
            logger.info("Startup script created: start_air_quality.sh")
            
        except Exception as e:
            logger.error(f"Failed to create startup script: {e}")
    
    def run_setup(self):
        """Run complete setup process"""
        logger.info("Starting Jetson Nano setup for Air Quality AI...")
        
        # Check system resources
        low_memory = self.check_system_resources()
        
        # Setup swap if low memory
        if low_memory:
            self.setup_swap()
        
        # Install system packages
        self.install_system_packages()
        
        # Setup Python environment
        self.setup_python_environment()
        
        # Apply Jetson optimizations
        self.optimize_jetson_performance()
        
        # Create startup script
        self.create_startup_script()
        
        logger.info("Setup completed! You can now run the Air Quality AI system.")
        logger.info("Use: python3 main.py --mock (for testing)")
        logger.info("Or: ./start_air_quality.sh")

def main():
    if os.geteuid() == 0:
        print("Please don't run this script as root!")
        print("Some commands will use sudo when needed.")
        sys.exit(1)
    
    setup = JetsonNanoSetup()
    setup.run_setup()

if __name__ == "__main__":
    main()
