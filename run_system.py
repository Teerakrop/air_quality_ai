#!/usr/bin/env python3
"""
Quick Start Script for Air Quality AI System
Provides easy commands to run different parts of the system
"""

import sys
import subprocess
import os
import time
import signal
from pathlib import Path

def print_banner():
    """Print system banner"""
    banner = """
    🌬️ Air Quality AI System 🤖
    ================================
    Real-time monitoring & AI forecasting
    Built for NVIDIA Jetson Nano
    """
    print(banner)

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import pandas
        import numpy
        import sklearn
        print("✅ Core dependencies found")
        return True
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def check_serial_port():
    """Check if ESP32 is connected"""
    import glob
    ports = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
    if ports:
        print(f"✅ Serial ports found: {ports}")
        return True
    else:
        print("⚠️  No serial ports found. ESP32 may not be connected.")
        return False

def run_command(cmd, description):
    """Run a system command"""
    print(f"\n🚀 {description}")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                 universal_newlines=True, bufsize=1)
        
        # Print output in real-time
        for line in process.stdout:
            print(line.rstrip())
        
        process.wait()
        return process.returncode == 0
        
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        process.terminate()
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main menu"""
    print_banner()
    
    # Check if we're in the right directory
    if not os.path.exists('main.py'):
        print("❌ Please run this script from the air_quality_ai directory")
        sys.exit(1)
    
    while True:
        print("\n" + "="*50)
        print("📋 MENU - Choose an option:")
        print("="*50)
        print("1. 🔍 System Check (Check dependencies & hardware)")
        print("2. 🚀 Start Full System (Data collection + AI + Dashboard)")
        print("3. 🧪 Start with Mock Sensors (Testing mode)")
        print("4. 📊 Dashboard Only (View existing data)")
        print("5. 🔧 Test Individual Components")
        print("6. 🧹 Maintenance Tasks")
        print("7. 📖 View System Status")
        print("8. ❌ Exit")
        print("="*50)
        
        choice = input("Enter your choice (1-8): ").strip()
        
        if choice == '1':
            system_check()
        elif choice == '2':
            start_full_system()
        elif choice == '3':
            start_mock_system()
        elif choice == '4':
            start_dashboard_only()
        elif choice == '5':
            test_components()
        elif choice == '6':
            maintenance_menu()
        elif choice == '7':
            view_status()
        elif choice == '8':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

def system_check():
    """Perform system check"""
    print("\n🔍 SYSTEM CHECK")
    print("="*30)
    
    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 7):
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"❌ Python version too old: {python_version}")
        return
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Check serial ports
    check_serial_port()
    
    # Check disk space
    import shutil
    total, used, free = shutil.disk_usage('.')
    free_gb = free // (1024**3)
    print(f"💾 Free disk space: {free_gb} GB")
    
    if free_gb < 5:
        print("⚠️  Low disk space! Consider cleaning up old data.")
    
    # Check if data directory exists
    if os.path.exists('data'):
        data_files = os.listdir('data')
        print(f"📁 Data directory: {len(data_files)} files")
    else:
        print("📁 Data directory: Will be created")
    
    print("\n✅ System check completed!")

def start_full_system():
    """Start the complete system"""
    print("\n🚀 STARTING FULL SYSTEM")
    print("="*35)
    print("This will start:")
    print("- Data collection from sensors")
    print("- AI model training/prediction")
    print("- Web dashboard")
    print("\nPress Ctrl+C to stop the system")
    
    input("\nPress Enter to continue or Ctrl+C to cancel...")
    
    cmd = [sys.executable, 'main.py']
    run_command(cmd, "Starting Air Quality AI System")

def start_mock_system():
    """Start system with mock sensors"""
    print("\n🧪 STARTING MOCK SYSTEM")
    print("="*35)
    print("This will start the system with simulated sensor data")
    print("Perfect for testing without hardware!")
    
    input("\nPress Enter to continue or Ctrl+C to cancel...")
    
    cmd = [sys.executable, 'main.py', '--mock']
    run_command(cmd, "Starting system with mock sensors")

def start_dashboard_only():
    """Start only the dashboard"""
    print("\n📊 STARTING DASHBOARD ONLY")
    print("="*40)
    print("This will start only the web dashboard")
    print("Useful for viewing existing data")
    
    input("\nPress Enter to continue or Ctrl+C to cancel...")
    
    cmd = [sys.executable, 'main.py', '--dashboard-only']
    run_command(cmd, "Starting dashboard")

def test_components():
    """Test individual components"""
    print("\n🔧 COMPONENT TESTING")
    print("="*30)
    print("1. Test Sensor Interface")
    print("2. Test Data Logger")
    print("3. Test ML Models")
    print("4. Test Prediction System")
    print("5. Back to main menu")
    
    choice = input("Choose component to test (1-5): ").strip()
    
    if choice == '1':
        cmd = [sys.executable, 'sensor_interface.py']
        run_command(cmd, "Testing sensor interface")
    elif choice == '2':
        cmd = [sys.executable, 'data_logger.py']
        run_command(cmd, "Testing data logger")
    elif choice == '3':
        cmd = [sys.executable, 'ml_models.py']
        run_command(cmd, "Testing ML models")
    elif choice == '4':
        cmd = [sys.executable, 'prediction_system.py']
        run_command(cmd, "Testing prediction system")
    elif choice == '5':
        return
    else:
        print("❌ Invalid choice")

def maintenance_menu():
    """Maintenance tasks menu"""
    print("\n🧹 MAINTENANCE TASKS")
    print("="*30)
    print("1. Run system maintenance")
    print("2. Clean old data (>30 days)")
    print("3. Backup data")
    print("4. View data statistics")
    print("5. Check model files")
    print("6. Back to main menu")
    
    choice = input("Choose maintenance task (1-6): ").strip()
    
    if choice == '1':
        cmd = [sys.executable, 'main.py', '--maintenance']
        run_command(cmd, "Running system maintenance")
    elif choice == '2':
        clean_old_data()
    elif choice == '3':
        backup_data()
    elif choice == '4':
        view_data_stats()
    elif choice == '5':
        check_model_files()
    elif choice == '6':
        return
    else:
        print("❌ Invalid choice")

def clean_old_data():
    """Clean old data files"""
    print("\n🧹 Cleaning old data...")
    
    if os.path.exists('data/air_quality_data.csv'):
        try:
            import pandas as pd
            from datetime import datetime, timedelta
            
            df = pd.read_csv('data/air_quality_data.csv')
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            cutoff_date = datetime.now() - timedelta(days=30)
            old_count = len(df[df['timestamp'] < cutoff_date])
            
            if old_count > 0:
                df_clean = df[df['timestamp'] >= cutoff_date]
                df_clean.to_csv('data/air_quality_data.csv', index=False)
                print(f"✅ Removed {old_count} old records")
            else:
                print("✅ No old data to clean")
                
        except Exception as e:
            print(f"❌ Error cleaning data: {e}")
    else:
        print("📁 No data file found")

def backup_data():
    """Backup data directory"""
    print("\n💾 Backing up data...")
    
    if os.path.exists('data'):
        from datetime import datetime
        import shutil
        
        backup_name = f"data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            shutil.copytree('data', backup_name)
            print(f"✅ Data backed up to: {backup_name}")
        except Exception as e:
            print(f"❌ Backup failed: {e}")
    else:
        print("📁 No data directory to backup")

def view_data_stats():
    """View data statistics"""
    print("\n📊 DATA STATISTICS")
    print("="*25)
    
    if os.path.exists('data/air_quality_data.csv'):
        try:
            import pandas as pd
            
            df = pd.read_csv('data/air_quality_data.csv')
            print(f"📊 Total records: {len(df):,}")
            
            if len(df) > 0:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                print(f"📅 Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
                print(f"📈 PM2.5 avg: {df['pm25'].mean():.1f} μg/m³")
                print(f"📈 PM10 avg: {df['pm10'].mean():.1f} μg/m³")
                print(f"🌡️  Temperature avg: {df['temperature'].mean():.1f}°C")
                print(f"💧 Humidity avg: {df['humidity'].mean():.1f}%")
                
        except Exception as e:
            print(f"❌ Error reading data: {e}")
    else:
        print("📁 No data file found")

def check_model_files():
    """Check model files"""
    print("\n🤖 MODEL FILES")
    print("="*20)
    
    model_files = [
        'models/lstm_model.h5',
        'models/random_forest_model.joblib',
        'models/scaler.joblib'
    ]
    
    for file_path in model_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            size_mb = size / (1024 * 1024)
            print(f"✅ {file_path}: {size_mb:.1f} MB")
        else:
            print(f"❌ {file_path}: Not found")

def view_status():
    """View system status"""
    print("\n📖 SYSTEM STATUS")
    print("="*25)
    
    # Check if system is running
    try:
        import psutil
        
        # Look for running Python processes
        python_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'python' in proc.info['name'].lower():
                    cmdline = ' '.join(proc.info['cmdline'])
                    if 'main.py' in cmdline or 'dashboard.py' in cmdline:
                        python_processes.append(f"PID {proc.info['pid']}: {cmdline}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if python_processes:
            print("🟢 Running processes:")
            for proc in python_processes:
                print(f"   {proc}")
        else:
            print("🔴 No system processes found")
            
    except ImportError:
        print("⚠️  psutil not available for process checking")
    
    # Check data freshness
    if os.path.exists('data/air_quality_data.csv'):
        try:
            import pandas as pd
            from datetime import datetime, timedelta
            
            df = pd.read_csv('data/air_quality_data.csv')
            if len(df) > 0:
                last_record = pd.to_datetime(df.iloc[-1]['timestamp'])
                time_diff = datetime.now() - last_record
                
                if time_diff < timedelta(minutes=5):
                    print("🟢 Data is fresh (< 5 minutes old)")
                elif time_diff < timedelta(hours=1):
                    print("🟡 Data is recent (< 1 hour old)")
                else:
                    print("🔴 Data is stale (> 1 hour old)")
                    
                print(f"📅 Last record: {last_record}")
            else:
                print("📊 No data records found")
                
        except Exception as e:
            print(f"❌ Error checking data: {e}")
    else:
        print("📁 No data file found")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please check your installation and try again.")

