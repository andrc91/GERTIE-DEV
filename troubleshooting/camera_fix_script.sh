#!/bin/bash
"""
Auto-Fix Script for Camera Video Streaming Issues
Run this on rep5, rep6, rep7 (cameras showing heartbeats but no video)
"""

echo "🔧 8-CAMERA SYSTEM VIDEO STREAMING REPAIR SCRIPT"
echo "==============================================="
echo "Run this on each problem camera (rep5, rep6, rep7)"
echo ""

# Get system info
HOSTNAME=$(hostname)
IP=$(hostname -I | awk '{print $1}')
echo "Fixing camera: $HOSTNAME ($IP)"
echo ""

# Function to run with error checking
run_with_check() {
    echo "🔄 $1..."
    if eval "$2"; then
        echo "   ✅ Success"
    else
        echo "   ❌ Failed: $1"
    fi
    echo ""
}

# Function to check and report
check_and_report() {
    echo "🔍 Checking: $1"
    eval "$2"
    echo ""
}

echo "STEP 1: STOP ALL VIDEO SERVICES"
echo "================================"
run_with_check "Stopping video_stream service" "sudo systemctl stop video_stream.service"
run_with_check "Killing existing video processes" "sudo pkill -f video_stream.py || true"
run_with_check "Killing python processes in camera dir" "sudo pkill -f 'python.*camera_system' || true"

sleep 2

echo "STEP 2: CHECK CAMERA HARDWARE"
echo "============================="
check_and_report "Camera device files" "ls -la /dev/video* || echo 'No video devices found'"
check_and_report "Camera detection" "vcgencmd get_camera || echo 'vcgencmd not available'"
check_and_report "USB cameras" "lsusb | grep -i camera || echo 'No USB cameras'"
check_and_report "Camera modules in kernel" "lsmod | grep -E '(bcm2835|v4l2)' || echo 'No camera modules loaded'"

echo "STEP 3: FIX PERMISSIONS"
echo "======================="

# Add user to video group
if groups andrc1 | grep -q video; then
    echo "✅ User andrc1 already in video group"
else
    run_with_check "Adding user to video group" "sudo usermod -a -G video andrc1"
    echo "⚠️  REBOOT REQUIRED after adding to video group"
fi

# Fix camera device permissions
if [ -e "/dev/video0" ]; then
    run_with_check "Setting camera permissions" "sudo chmod 666 /dev/video0"
    run_with_check "Setting camera ownership" "sudo chown andrc1:video /dev/video0"
else
    echo "⚠️  No /dev/video0 found - camera hardware issue"
fi

echo "STEP 4: CHECK NETWORK PORTS"
echo "==========================="
check_and_report "Port usage" "netstat -tulnp | grep :500"

# Check if required ports are available
for port in 5001 5002 5003 5004; do
    if netstat -tuln | grep -q ":$port "; then
        echo "⚠️  Port $port is in use"
        netstat -tulnp | grep ":$port "
    else
        echo "✅ Port $port is available"
    fi
done
echo ""

echo "STEP 5: TEST CAMERA ACCESS"
echo "=========================="
cd /home/andrc1/camera_system_integrated_final/slave

echo "🔄 Testing Picamera2 import and basic functionality..."
python3 -c "
import sys
sys.path.insert(0, '/home/andrc1/camera_system_integrated_final')

try:
    from picamera2 import Picamera2
    print('✅ Picamera2 import successful')
    
    # Test camera initialization
    picam2 = Picamera2()
    print('✅ Picamera2 object created')
    
    # Test configuration
    config = picam2.create_video_configuration(main={'size': (640, 480), 'format': 'RGB888'})
    picam2.configure(config)
    print('✅ Camera configuration successful')
    
    # Test start/stop
    picam2.start()
    print('✅ Camera started successfully')
    
    import time
    time.sleep(1)
    
    # Test frame capture
    frame = picam2.capture_array()
    print(f'✅ Frame capture successful: {frame.shape}')
    
    picam2.stop()
    picam2.close()
    print('✅ Camera test completed successfully')
    
except Exception as e:
    print(f'❌ Camera test failed: {e}')
    import traceback
    traceback.print_exc()
"
echo ""

echo "STEP 6: CHECK VIDEO STREAM SERVICE"
echo "=================================="
check_and_report "Service file exists" "ls -la /etc/systemd/system/video_stream.service"
check_and_report "Service file content" "cat /etc/systemd/system/video_stream.service"

echo "STEP 7: TEST VIDEO STREAM SCRIPT MANUALLY"
echo "========================================="
echo "🔄 Testing video stream script directly..."

# Test the video stream script in foreground mode
timeout 10s python3 video_stream.py &
STREAM_PID=$!

sleep 5

if ps -p $STREAM_PID > /dev/null; then
    echo "✅ Video stream script running (PID: $STREAM_PID)"
    
    # Check if it's listening on ports
    netstat -tuln | grep :5002 && echo "✅ Video port 5002 listening" || echo "❌ Video port 5002 not listening"
    netstat -tuln | grep :5003 && echo "✅ Heartbeat port 5003 listening" || echo "❌ Heartbeat port 5003 not listening"
    netstat -tuln | grep :5004 && echo "✅ Video control port 5004 listening" || echo "❌ Video control port 5004 not listening"
    
    kill $STREAM_PID 2>/dev/null || true
else
    echo "❌ Video stream script crashed or failed to start"
fi
echo ""

echo "STEP 8: RESTART VIDEO SERVICE"
echo "============================="
run_with_check "Reloading systemd daemon" "sudo systemctl daemon-reload"
run_with_check "Enabling video_stream service" "sudo systemctl enable video_stream.service"
run_with_check "Starting video_stream service" "sudo systemctl start video_stream.service"

sleep 3

echo "🔄 Checking service status..."
sudo systemctl status video_stream.service --no-pager
echo ""

echo "🔄 Checking recent service logs..."
sudo journalctl -u video_stream.service -n 20 --no-pager
echo ""

echo "STEP 9: VERIFY HEARTBEAT AND VIDEO"
echo "=================================="
sleep 5

# Check if heartbeat is working
echo "🔄 Testing heartbeat (should see output if working)..."
timeout 3s tcpdump -i any port 5003 2>/dev/null || echo "tcpdump not available, skipping heartbeat test"

# Check if video stream is working  
echo "🔄 Testing video stream (should see output if working)..."
timeout 3s tcpdump -i any port 5002 2>/dev/null || echo "tcpdump not available, skipping video test"

echo ""
echo "STEP 10: FINAL STATUS CHECK"
echo "=========================="
check_and_report "Video service status" "systemctl is-active video_stream.service"
check_and_report "Python processes" "ps aux | grep python | grep -v grep"
check_and_report "Network connections" "netstat -tuln | grep ':500'"

echo ""
echo "🎯 REPAIR COMPLETE!"
echo "=================="
echo "If the service is running but still no video:"
echo ""
echo "1. Check the master GUI - send START_STREAM command"
echo "2. Run: sudo journalctl -u video_stream.service -f"
echo "3. Look for error messages when START_STREAM is sent"
echo "4. If camera permissions error - REBOOT this Pi"
echo "5. If port conflicts - check what's using the ports"
echo ""
echo "NEXT: Test from master control Pi GUI"
echo "Expected behavior after fix:"
echo "✅ Heartbeat should be green (already working)"  
echo "✅ Video stream should start showing frames"
echo ""

# Offer to reboot if needed
echo "⚠️  If user was added to video group, REBOOT is required"
read -p "Reboot now? (y/n): " -r
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔄 Rebooting in 10 seconds..."
    sleep 10
    sudo reboot
fi
