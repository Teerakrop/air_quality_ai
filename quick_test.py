#!/usr/bin/env python3
"""
Quick test script to verify the fixes work
"""

import sys
import os
import time
import threading
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    tests = [
        ('config', 'Configuration'),
        ('sensor_interface', 'Sensor Interface'),
        ('data_logger', 'Data Logger'),
        ('prediction_system', 'Prediction System'),
        ('ml_models', 'ML Models'),
    ]
    
    success = 0
    for module, name in tests:
        try:
            __import__(module)
            print(f"OK: {name}")
            success += 1
        except ImportError as e:
            print(f"FAIL: {name} - {e}")
    
    print(f"Import test: {success}/{len(tests)} passed")
    return success == len(tests)

def test_dashboard_import():
    """Test dashboard imports"""
    print("\nTesting dashboard imports...")
    
    try:
        from dashboard import app
        print("OK: Main dashboard")
        return True
    except ImportError as e:
        print(f"FAIL: Main dashboard - {e}")
        
        try:
            from simple_dashboard import create_dash_app
            print("OK: Simple dashboard fallback")
            return True
        except ImportError as e2:
            print(f"FAIL: Simple dashboard also failed - {e2}")
            return False

def test_web_server():
    """Test if web server can start"""
    print("\nTesting web server startup...")
    
    try:
        import dash
        from dash import html
        
        app = dash.Dash(__name__)
        app.layout = html.H1("Test")
        
        # Try to start server in a thread
        def start_server():
            try:
                app.run_server(host='127.0.0.1', port=8051, debug=False)
            except:
                pass
        
        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()
        
        # Wait a moment for server to start
        time.sleep(2)
        
        # Try to connect
        import urllib.request
        try:
            response = urllib.request.urlopen('http://127.0.0.1:8051', timeout=5)
            print("OK: Web server test")
            return True
        except:
            print("FAIL: Web server test - Failed to connect")
            return False
            
    except Exception as e:
        print(f"FAIL: Web server test - {e}")
        return False

def test_config():
    """Test configuration"""
    print("\nTesting configuration...")
    
    try:
        import config
        
        required_attrs = [
            'DASHBOARD_HOST', 'DASHBOARD_PORT', 'DATA_DIR', 
            'MODELS_DIR', 'RAW_DATA_FILE'
        ]
        
        missing = []
        for attr in required_attrs:
            if not hasattr(config, attr):
                missing.append(attr)
        
        if missing:
            print(f"FAIL: Missing config attributes: {missing}")
            return False
        
        print(f"OK: Configuration")
        print(f"   Data dir: {config.DATA_DIR}")
        print(f"   Dashboard: {config.DASHBOARD_HOST}:{config.DASHBOARD_PORT}")
        return True
        
    except Exception as e:
        print(f"FAIL: Configuration test - {e}")
        return False

def main():
    """Run all tests"""
    print("Quick Test for Air Quality AI Fixes")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_config),
        ("Module Imports", test_imports),
        ("Dashboard Import", test_dashboard_import),
        ("Web Server", test_web_server),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"CRASH: {name} test crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("SUCCESS: All tests passed! System should work correctly.")
        print("You can now run: python3 main.py --mock")
    elif passed >= total * 0.8:
        print("PARTIAL: Most tests passed. System should work with minor issues.")
        print("Try running: python3 main.py --mock")
    else:
        print("WARNING: Several tests failed. You may need to fix dependencies.")
        print("Try running: python3 fix_jetson_dependencies.py")
    
    return passed >= total * 0.8

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
