#!/bin/bash

set -e

echo "=========================================="
echo "Development Environment Setup"
echo "=========================================="

# Ensure we're in the workspace
cd /workspace

# Test ROS2 installation
echo "✓ Testing ROS2 installation..."
source /opt/ros/humble/setup.bash
ros2 --version

# Test Python packages installation (no hardware required)
echo "✓ Verifying Python packages..."

echo "  - Testing PyTorch (CPU-only)..."
python3 -c "import torch; print(f'    PyTorch version: {torch.__version__}')"

echo "  - Testing ultralytics..."
python3 -c "from ultralytics import YOLO; print('    Ultralytics imported successfully')"

echo "  - Testing pyrealsense2..."
python3 -c "import pyrealsense2 as rs; print(f'    pyrealsense2 version: {rs.__version__}')"

echo "  - Testing OpenCV..."
python3 -c "import cv2; print(f'    OpenCV version: {cv2.__version__}')"

echo "  - Testing ROS2 Python bindings..."
python3 -c "import rclpy; print('    rclpy imported successfully')"

# Make Python scripts executable
echo "✓ Setting executable permissions on Python scripts..."
chmod +x /workspace/*.py 2>/dev/null || true

# Display environment info
echo "=========================================="
echo "Environment Ready for Development"
echo "=========================================="
echo "ROS Distribution: humble"
echo "Python: $(python3 --version)"
echo "Workspace: $(pwd)"
echo ""
echo "Note: This is a development environment"
echo "- No GPU/CUDA (CPU-only PyTorch)"
echo "- No camera hardware access"
echo "- LSP and code completion fully functional"
echo "=========================================="
echo "Ready to code!"
echo "=========================================="
