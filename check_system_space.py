#!/usr/bin/env python3
"""
System Space Checker for Air Quality AI on Jetson Nano
Checks available space and provides recommendations for 119GB SD card
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def get_size_mb(path):
    """Get size of directory in MB"""
    if os.path.isfile(path):
        return os.path.getsize(path) / (1024 * 1024)
    elif os.path.isdir(path):
        total = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total += os.path.getsize(filepath)
                except (OSError, FileNotFoundError):
                    pass
        return total / (1024 * 1024)
    return 0

def check_disk_space():
    """Check available disk space"""
    total, used, free = shutil.disk_usage('/')
    
    total_gb = total / (1024**3)
    used_gb = used / (1024**3)
    free_gb = free / (1024**3)
    used_percent = (used / total) * 100
    
    return {
        'total_gb': total_gb,
        'used_gb': used_gb,
        'free_gb': free_gb,
        'used_percent': used_percent
    }

def check_memory():
    """Check memory usage"""
    try:
        with open('/proc/meminfo', 'r') as f:
            meminfo = f.read()
        
        lines = meminfo.split('\n')
        mem_total = int([line for line in lines if 'MemTotal' in line][0].split()[1]) / 1024
        mem_available = int([line for line in lines if 'MemAvailable' in line][0].split()[1]) / 1024
        
        return {
            'total_mb': mem_total,
            'available_mb': mem_available,
            'used_percent': ((mem_total - mem_available) / mem_total) * 100
        }
    except:
        return None

def check_swap():
    """Check swap usage"""
    try:
        result = subprocess.run(['swapon', '--show'], capture_output=True, text=True)
        if result.stdout.strip():
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            total_swap = 0
            for line in lines:
                parts = line.split()
                if len(parts) >= 3:
                    size_str = parts[2]
                    if 'G' in size_str:
                        total_swap += float(size_str.replace('G', '')) * 1024
                    elif 'M' in size_str:
                        total_swap += float(size_str.replace('M', ''))
            return total_swap
        return 0
    except:
        return 0

def check_project_size():
    """Check size of project components"""
    components = {
        'data': 'data/',
        'models': 'models/',
        'logs': 'logs/',
        'cache': os.path.expanduser('~/.cache/pip'),
        'local_packages': os.path.expanduser('~/.local/lib/python3.6/site-packages')
    }
    
    sizes = {}
    for name, path in components.items():
        if os.path.exists(path):
            sizes[name] = get_size_mb(path)
        else:
            sizes[name] = 0
    
    return sizes

def get_recommendations(disk_info, memory_info, project_sizes):
    """Generate recommendations based on system status"""
    recommendations = []
    
    # Disk space recommendations
    if disk_info['free_gb'] < 10:
        recommendations.append("🚨 CRITICAL: Less than 10GB free space! Clean up immediately.")
        recommendations.append("   Run: sudo apt autoremove -y && sudo apt autoclean")
    elif disk_info['free_gb'] < 20:
        recommendations.append("⚠️  WARNING: Less than 20GB free space. Consider cleanup.")
        recommendations.append("   Run: ./maintenance.sh")
    else:
        recommendations.append("✅ Disk space looks good!")
    
    # Memory recommendations
    if memory_info and memory_info['used_percent'] > 80:
        recommendations.append("⚠️  High memory usage detected.")
        recommendations.append("   Consider restarting or reducing running processes.")
    
    # Project size recommendations
    if project_sizes['data'] > 1000:  # > 1GB
        recommendations.append("📊 Data folder is large (>1GB). Consider archiving old data.")
        recommendations.append("   Run: python3 main.py --maintenance")
    
    if project_sizes['cache'] > 500:  # > 500MB
        recommendations.append("🧹 Pip cache is large. Clean it up to save space.")
        recommendations.append("   Run: python3 -m pip cache purge")
    
    return recommendations

def main():
    print("🔍 Air Quality AI - System Space Checker")
    print("=" * 50)
    
    # Check if we're in the project directory
    if not os.path.exists('main.py'):
        print("❌ Please run this script from the air_quality_ai directory")
        sys.exit(1)
    
    # Check disk space
    print("\n💿 Disk Space Analysis:")
    disk_info = check_disk_space()
    print(f"   Total: {disk_info['total_gb']:.1f} GB")
    print(f"   Used:  {disk_info['used_gb']:.1f} GB ({disk_info['used_percent']:.1f}%)")
    print(f"   Free:  {disk_info['free_gb']:.1f} GB")
    
    # Check memory
    print("\n💾 Memory Analysis:")
    memory_info = check_memory()
    if memory_info:
        print(f"   Total: {memory_info['total_mb']:.0f} MB")
        print(f"   Available: {memory_info['available_mb']:.0f} MB")
        print(f"   Used: {memory_info['used_percent']:.1f}%")
    else:
        print("   Could not read memory information")
    
    # Check swap
    print("\n🔄 Swap Analysis:")
    swap_mb = check_swap()
    if swap_mb > 0:
        print(f"   Swap enabled: {swap_mb:.0f} MB")
    else:
        print("   No swap detected")
    
    # Check project components
    print("\n📁 Project Size Analysis:")
    project_sizes = check_project_size()
    total_project_size = sum(project_sizes.values())
    
    for component, size_mb in project_sizes.items():
        if size_mb > 0:
            print(f"   {component}: {size_mb:.1f} MB")
        else:
            print(f"   {component}: Not found or empty")
    
    print(f"   Total project size: {total_project_size:.1f} MB")
    
    # System recommendations
    print("\n💡 Recommendations:")
    recommendations = get_recommendations(disk_info, memory_info, project_sizes)
    
    for rec in recommendations:
        print(f"   {rec}")
    
    # Space optimization tips
    print("\n🎯 Space Optimization Tips for 119GB SD Card:")
    print("   • Keep at least 20GB free for optimal performance")
    print("   • Use system packages (apt) instead of pip when possible")
    print("   • Clean pip cache regularly: python3 -m pip cache purge")
    print("   • Archive old data files periodically")
    print("   • Skip TensorFlow if you don't need LSTM models")
    print("   • Run maintenance script weekly: ./maintenance.sh")
    
    # Quick cleanup commands
    if disk_info['free_gb'] < 20:
        print("\n🧹 Quick Cleanup Commands:")
        print("   sudo apt autoremove -y")
        print("   sudo apt autoclean")
        print("   python3 -m pip cache purge")
        print("   sudo journalctl --vacuum-time=7d")
        print("   ./maintenance.sh")
    
    print(f"\n📊 Summary: {disk_info['free_gb']:.1f}GB free of {disk_info['total_gb']:.1f}GB total")
    
    if disk_info['free_gb'] >= 20:
        print("🎉 Your system has plenty of space for Air Quality AI!")
    elif disk_info['free_gb'] >= 10:
        print("⚠️  Your system has adequate space but consider cleanup soon.")
    else:
        print("🚨 Your system is running low on space. Cleanup required!")

if __name__ == "__main__":
    main()
