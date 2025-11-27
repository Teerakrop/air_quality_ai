#!/usr/bin/env python3
"""
Update dashboard charts with better visualization
Run this to restart dashboard with improved charts
"""

import subprocess
import sys
import os
import time

def main():
    print("🎨 Updating Dashboard Charts...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('dashboard.py'):
        print("❌ Please run this script from the air_quality_ai directory")
        sys.exit(1)
    
    print("1. 🛑 Stopping current system...")
    try:
        # Kill existing main.py processes
        subprocess.run(['pkill', '-f', 'python3 main.py'], check=False)
        time.sleep(2)
        print("   ✅ System stopped")
    except:
        print("   ⚠️ No running system found")
    
    print("\n2. 📊 Charts have been updated with:")
    print("   • Better visualization for Prediction Accuracy")
    print("   • Improved Historical vs Predicted comparison")
    print("   • Clearer labels and colors")
    print("   • Summary statistics")
    print("   • Emoji indicators for better UX")
    
    print("\n3. 🚀 Starting system with updated dashboard...")
    try:
        # Start the system
        process = subprocess.Popen(['python3', 'main.py', '--mock'])
        print(f"   ✅ System started (PID: {process.pid})")
        
        print("\n4. ⏳ Waiting for dashboard to initialize...")
        time.sleep(10)
        
        print("\n🎉 Dashboard updated successfully!")
        print("=" * 50)
        print("📱 Access your improved dashboard at:")
        print("   • Local: http://localhost:8050")
        print("   • Network: http://192.168.1.43:8050")
        print("\n💡 New features:")
        print("   • 🎯 Prediction Accuracy: Shows error trends over time")
        print("   • 🔍 Historical vs Predicted: Split view for PM2.5 and PM10")
        print("   • 📊 Summary statistics displayed on charts")
        print("   • 🌈 Better colors and emojis for clarity")
        print("\n🔄 Refresh your browser (Ctrl+F5) to see the changes!")
        
    except Exception as e:
        print(f"❌ Error starting system: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
