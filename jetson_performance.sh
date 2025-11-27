#!/bin/bash
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
