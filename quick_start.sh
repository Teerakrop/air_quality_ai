#!/bin/bash
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
