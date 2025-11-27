#!/usr/bin/env python3
"""
Quick Start Script for Air Quality AI Website
รันเว็บไซต์แดชบอร์ดอย่างง่าย
"""

import sys
import os
import time
import webbrowser
from threading import Timer

def open_browser():
    """เปิดเบราว์เซอร์หลังจากเซิร์ฟเวอร์เริ่มทำงาน"""
    webbrowser.open('http://localhost:8050')

def main():
    print("Air Quality AI Dashboard - Starting Website")
    print("=" * 50)
    
    # Check if we're in the correct directory
    if not os.path.exists('dashboard.py'):
        print("Error: dashboard.py not found")
        print("Please run this script in the air_quality_ai folder")
        sys.exit(1)
    
    print("Starting dashboard...")
    print("Website will open at: http://localhost:8050")
    print("Please wait...")
    
    # เปิดเบราว์เซอร์หลังจาก 3 วินาที
    Timer(3.0, open_browser).start()
    
    try:
        # Import และรันแดชบอร์ด
        from dashboard import app
        import config
        
        print("Server started successfully!")
        print("Data updates every 30 seconds")
        print("Press Ctrl+C to stop the server")
        print("-" * 50)
        
        app.run_server(
            host=config.DASHBOARD_HOST,
            port=config.DASHBOARD_PORT,
            debug=False
        )
        
    except KeyboardInterrupt:
        print("\nServer stopped!")
    except Exception as e:
        print(f"Error occurred: {e}")
        print("Try checking if dependencies are installed:")
        print("   pip install dash dash-bootstrap-components plotly pandas")

if __name__ == "__main__":
    main()
