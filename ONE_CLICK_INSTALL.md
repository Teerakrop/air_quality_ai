# 🚀 One-Click Installation for Jetson Nano (119GB SD Card)

## 📋 Prerequisites
- NVIDIA Jetson Nano with JetPack 4.6+
- 119GB SD card (or larger)
- Internet connection
- At least 10GB free space

## 🎯 One-Click Installation

### Step 1: Clone the Repository
```bash
git clone https://github.com/Teerakrop/air_quality_ai.git
cd air_quality_ai
```

### Step 2: Run the Complete Setup (ONE COMMAND!)
```bash
bash setup_jetson_nano_complete.sh
```

**That's it!** ✨ The script will automatically:
- ✅ Check system compatibility
- ✅ Install all dependencies
- ✅ Optimize for 119GB SD card
- ✅ Configure Jetson Nano performance
- ✅ Create startup scripts
- ✅ Test the installation

## 🚀 How to Use After Installation

### Quick Start Commands
```bash
# Start the complete system (recommended)
./start_air_quality_system.sh

# Start dashboard only
./start_dashboard_only.sh

# Test the system
./test_system.sh

# Run maintenance
./maintenance.sh
```

### Web Dashboard Access
- **Local**: http://localhost:8050
- **Network**: http://YOUR_JETSON_IP:8050
- **Mobile**: Use your Jetson's IP address

## 📊 What Gets Installed

### System Packages (via apt)
- Python 3 development tools
- Scientific computing libraries (NumPy, Pandas, Matplotlib, SciKit-Learn)
- Build tools and dependencies

### Python Packages (via pip)
- Dash web framework
- Plotly for visualizations
- Serial communication tools
- System utilities

### Optimizations for 119GB SD Card
- **Minimal TensorFlow**: Optional installation to save space
- **System packages**: Use apt packages instead of pip when possible
- **Smart swap**: 2GB swap file optimized for SD card longevity
- **Cache management**: Automatic cleanup of unnecessary files

## 🎛️ System Features

### 🌬️ Air Quality Monitoring
- Real-time PM2.5, PM10 readings
- Temperature and humidity monitoring
- Gas level detection
- Historical data logging

### 🤖 AI Predictions
- 1-hour, 3-hour, 6-hour forecasts
- Machine learning models (Random Forest/LSTM)
- Accuracy tracking and validation

### 📊 Web Dashboard
- Beautiful real-time charts
- Mobile-responsive design
- Auto-refresh every 30 seconds
- Historical data visualization

### 🔧 Hardware Support
- ESP32 with multiple sensors
- Auto-detection of serial ports
- Mock sensor mode for testing
- Jetson Nano GPIO ready

## 💾 Storage Optimization for 119GB

The installation is optimized for your 119GB SD card:

### Space Usage
- **System packages**: ~2GB
- **Python packages**: ~1GB
- **Swap file**: 2GB
- **Data storage**: ~1GB (grows over time)
- **Total**: ~6GB initial usage

### Space Saving Features
- Uses system Python packages when possible
- Optional TensorFlow installation
- Automatic old data cleanup
- Smart cache management
- Minimal package versions

## 🛠️ Troubleshooting

### Common Issues

**1. "Not enough disk space"**
```bash
# Clean up system
sudo apt autoremove -y
sudo apt autoclean
sudo journalctl --vacuum-time=7d
```

**2. "ESP32 not detected"**
- System will run in demo mode automatically
- Check USB connections
- Try different USB ports

**3. "Dashboard not loading"**
```bash
# Check if port is in use
sudo netstat -tulpn | grep :8050

# Restart the system
./start_air_quality_system.sh
```

**4. "Memory issues"**
```bash
# Check memory usage
free -h

# Run maintenance
./maintenance.sh
```

### Getting Help
1. Check `QUICK_START_GUIDE.md`
2. Run `./test_system.sh` for diagnostics
3. Check logs in `logs/` directory
4. Run `./maintenance.sh` for system health

## 🔄 Regular Maintenance

### Weekly
```bash
./maintenance.sh
```

### Monthly
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Clean old data
python3 main.py --maintenance
```

## 📱 Mobile Access

Your dashboard is mobile-friendly! Access it from any device on your network:

1. Find your Jetson's IP: `hostname -I`
2. Open browser on phone/tablet
3. Go to: `http://YOUR_JETSON_IP:8050`

## 🎉 Success Indicators

After installation, you should see:
- ✅ All package tests pass
- ✅ Startup scripts created
- ✅ Desktop shortcuts (if GUI available)
- ✅ Web dashboard accessible
- ✅ System optimizations applied

## 💡 Pro Tips

1. **Save Space**: Skip TensorFlow if you don't need LSTM models
2. **Performance**: Keep at least 20GB free space for optimal performance
3. **Monitoring**: Check system status regularly with `./maintenance.sh`
4. **Backup**: Backup your `data/` folder periodically
5. **Updates**: Pull latest code updates regularly

---

**🌬️ Enjoy your AI-powered air quality monitoring system! 🤖**

*Optimized for NVIDIA Jetson Nano with 119GB SD card*
