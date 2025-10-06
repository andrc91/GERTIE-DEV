#!/bin/bash
# Complete setup script for Raspberry Pi deployment

echo "🚀 Setting up Modular Camera GUI on Raspberry Pi..."

# Navigate to camera system directory
cd /home/andrc1/camera_system_integrated_final/master/camera_gui

# Install required dependencies
echo "📦 Installing dependencies..."
pip3 install pillow opencv-python

# Make scripts executable
chmod +x main.py launch.py test_structure.py

# Test the structure
echo "🧪 Testing modular structure..."
python3 test_structure.py

echo "✅ Setup complete! Ready to run:"
echo "   python3 main.py       # Launch full GUI"
echo "   python3 launch.py     # Launch with fallbacks"
echo "   python3 test_structure.py  # Test structure"
