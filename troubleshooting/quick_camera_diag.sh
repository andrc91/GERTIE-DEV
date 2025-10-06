#!/bin/bash
# Quick diagnostic for cameras with heartbeat but no video

echo "🔍 QUICK VIDEO STREAM DIAGNOSTIC"
echo "================================"
echo "Camera: $(hostname) ($(hostname -I | awk '{print $1}'))"
echo ""

echo "1. SERVICE STATUS:"
sudo systemctl status video_stream.service --no-pager | head -10
echo ""

echo "2. RECENT ERRORS (last 10 lines):"
sudo journalctl -u video_stream.service -n 10 --no-pager
echo ""

echo "3. CAMERA HARDWARE:"
ls -la /dev/video* 2>/dev/null || echo "No video devices"
vcgencmd get_camera 2>/dev/null || echo "vcgencmd unavailable"
echo ""

echo "4. USER PERMISSIONS:"
groups andrc1 | grep video && echo "✅ In video group" || echo "❌ NOT in video group"
echo ""

echo "5. NETWORK PORTS:"
echo "Port 5002 (video): $(netstat -tuln | grep :5002 && echo 'LISTENING' || echo 'NOT LISTENING')"
echo "Port 5003 (heartbeat): $(netstat -tuln | grep :5003 && echo 'LISTENING' || echo 'NOT LISTENING')" 
echo "Port 5004 (control): $(netstat -tuln | grep :5004 && echo 'LISTENING' || echo 'NOT LISTENING')"
echo ""

echo "6. PYTHON PROCESSES:"
ps aux | grep python | grep -E "(video|camera)" | grep -v grep || echo "No video-related python processes"
echo ""

echo "7. QUICK CAMERA TEST:"
cd /home/andrc1/camera_system_integrated_final/slave
python3 -c "
try:
    from picamera2 import Picamera2
    picam2 = Picamera2()
    picam2.close()
    print('✅ Camera hardware OK')
except Exception as e:
    print(f'❌ Camera test failed: {e}')
" 2>/dev/null
echo ""

echo "SUMMARY:"
echo "========"
if systemctl is-active --quiet video_stream.service; then
    echo "✅ Service is running"
    if netstat -tuln | grep -q :5003; then
        echo "✅ Heartbeat port active (explains GUI heartbeat)"
    else
        echo "❌ Heartbeat port not active"
    fi
    
    if netstat -tuln | grep -q :5002; then
        echo "✅ Video port active - check for START_STREAM command reception"
    else
        echo "❌ Video port NOT active - this is the problem!"
        echo "   The video streaming thread likely crashed"
    fi
else
    echo "❌ Service not running"
fi
