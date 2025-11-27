#!/usr/bin/env python3
"""
Fix dependencies issues on Jetson Nano
This script will install compatible versions of packages
"""

import subprocess
import sys
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_command(cmd, description=""):
    """Run a command and return success status"""
    try:
        logger.info(f"Running: {description}")
        result = subprocess.run(cmd, shell=True, check=True, 
                              capture_output=True, text=True)
        logger.info(f"✅ Success: {description}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed: {description}")
        logger.error(f"Error: {e.stderr}")
        return False

def install_package_flexible(package_name, fallback_versions=None):
    """Try to install a package with fallback versions"""
    if fallback_versions is None:
        fallback_versions = []
    
    # Try latest version first
    if run_command(f"pip3 install --user {package_name}", f"Installing {package_name}"):
        return True
    
    # Try fallback versions
    for version in fallback_versions:
        if run_command(f"pip3 install --user {package_name}=={version}", 
                      f"Installing {package_name}=={version}"):
            return True
    
    logger.warning(f"⚠️ Could not install {package_name}")
    return False

def main():
    """Main function to fix dependencies"""
    print("🔧 Fixing Jetson Nano Dependencies...")
    print("=" * 50)
    
    # Essential packages with fallback versions
    packages = {
        'pyserial': ['3.5', '3.4'],
        'dash': ['2.14.1', '2.10.0', '2.0.0'],
        'dash-bootstrap-components': ['1.4.0', '1.2.0', '1.0.0'],
        'plotly': ['5.17.0', '5.10.0', '5.0.0'],
        'flask': ['2.3.3', '2.0.0', '1.1.4'],
        'schedule': ['1.2.0', '1.1.0'],
        'psutil': ['5.9.5', '5.8.0'],
        'tqdm': ['4.66.1', '4.60.0'],
        'python-dotenv': ['1.0.0', '0.19.0'],
        'joblib': ['1.3.2', '1.0.0']
    }
    
    success_count = 0
    total_count = len(packages)
    
    for package, versions in packages.items():
        print(f"\n📦 Installing {package}...")
        if install_package_flexible(package, versions):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Installation Summary: {success_count}/{total_count} packages installed")
    
    if success_count == total_count:
        print("🎉 All packages installed successfully!")
    elif success_count >= total_count * 0.8:  # 80% success rate
        print("✅ Most packages installed. System should work.")
    else:
        print("⚠️ Some packages failed. You may need to install manually.")
    
    # Test imports
    print("\n🧪 Testing imports...")
    test_imports = [
        ('serial', 'pyserial'),
        ('dash', 'dash'),
        ('plotly', 'plotly'),
        ('flask', 'flask'),
        ('schedule', 'schedule'),
        ('psutil', 'psutil')
    ]
    
    import_success = 0
    for module, package in test_imports:
        try:
            __import__(module)
            print(f"✅ {module} - OK")
            import_success += 1
        except ImportError:
            print(f"❌ {module} - Failed (from {package})")
    
    print(f"\n📊 Import Test: {import_success}/{len(test_imports)} modules working")
    
    if import_success >= len(test_imports) * 0.8:
        print("🚀 System ready! You can now run: python3 main.py --mock")
    else:
        print("⚠️ Some modules missing. Try running this script again or install manually.")

if __name__ == "__main__":
    main()
