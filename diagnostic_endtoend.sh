#!/bin/bash
# Comprehensive End-to-End Diagnostic Script
# Run this to verify the complete command path from GUI to replicas

echo "🔬 END-TO-END SYSTEM DIAGNOSTIC"
echo "==============================="

HOSTNAME=$(hostname)
IP=$(hostname -I | awk '{print $1}')
echo "Testing on: $HOSTNAME ($IP)"
echo ""

echo "1. NETWORK CONNECTIVITY TEST"
echo "============================"

# Test if we can reach each replica
echo "📡 Testing UDP connectivity to all replicas:"
for i in {1..7}; do
    target_ip="192.168.0.20$i"
    echo -n "  rep$i ($target_ip): "
    
    # Send test command with timeout
    if timeout 3 bash -c "echo 'STATUS' | nc -u -w 2 $target_ip 5001" 2>/dev/null; then
        echo "✅ Reachable"
    else
        echo "❌ Not reachable"
    fi
done

# Test local camera (rep8) if on control1
if [ "$IP" = "192.168.0.200" ] || [ "$HOSTNAME" = "control1" ]; then
    echo -n "  rep8 (127.0.0.1): "
    if timeout 3 bash -c "echo 'STATUS' | nc -u -w 2 127.0.0.1 5011" 2>/dev/null; then
        echo "✅ Reachable"
    else
        echo "❌ Not reachable"
    fi
fi
echo ""

echo "2. SERVICE STATUS CHECK"
echo "======================"
if [ "$IP" = "192.168.0.200" ] || [ "$HOSTNAME" = "control1" ]; then
    echo "📊 control1 services:"
    systemctl is-active local_camera_slave.service && echo "  ✅ local_camera_slave: Active" || echo "  ❌ local_camera_slave: Inactive"
else
    echo "📊 Remote replica services:"
    systemctl is-active video_stream.service && echo "  ✅ video_stream: Active" || echo "  ❌ video_stream: Inactive"
    systemctl is-active still_capture.service && echo "  ✅ still_capture: Active" || echo "  ❌ still_capture: Inactive"
fi
echo ""

echo "3. PORT LISTENING CHECK"
echo "======================"
echo "🌐 Required ports should be listening:"

if [ "$IP" = "192.168.0.200" ] || [ "$HOSTNAME" = "control1" ]; then
    # control1 (master) port checks
    netstat -tuln | grep ':5011' && echo "  ✅ rep8 Control port 5011" || echo "  ❌ rep8 Control port 5011 not listening"
    netstat -tuln | grep ':5002' && echo "  ✅ Master Video port 5002 (GUI receives)" || echo "  ❌ Master Video port 5002 not listening"
    netstat -tuln | grep ':6000' && echo "  ✅ Master Still port 6000 (GUI receives)" || echo "  ❌ Master Still port 6000 not listening"
    netstat -tuln | grep ':5003' && echo "  ✅ Master Heartbeat port 5003 (GUI receives)" || echo "  ❌ Master Heartbeat port 5003 not listening"
else
    # Remote replica port checks
    netstat -tuln | grep ':5001' && echo "  ✅ Control port 5001" || echo "  ❌ Control port 5001 not listening"
    netstat -tuln | grep ':5004' && echo "  ✅ Video control port 5004" || echo "  ❌ Video control port 5004 not listening"
    netstat -tuln | grep ':5003' && echo "  ✅ Heartbeat port 5003" || echo "  ❌ Heartbeat port 5003 not listening"
fi
echo ""

echo "4. SETTINGS PACKAGE TEST"
echo "========================"
# Test if the replica can handle the new settings package format
echo "📤 Testing settings package command:"

TEST_SETTINGS='{"iso":400,"brightness":60,"flip_horizontal":true,"grayscale":false}'
if [ "$IP" = "192.168.0.200" ] || [ "$HOSTNAME" = "control1" ]; then
    # Test rep8 (local camera)
    echo "  Sending to rep8: SET_ALL_SETTINGS_$TEST_SETTINGS"
    echo "SET_ALL_SETTINGS_$TEST_SETTINGS" | nc -u -w 2 127.0.0.1 5011 || echo "  ❌ Failed to send to rep8"
else
    # Test remote replica
    echo "  Sending to $IP: SET_ALL_SETTINGS_$TEST_SETTINGS"
    echo "SET_ALL_SETTINGS_$TEST_SETTINGS" | nc -u -w 2 $IP 5001 || echo "  ❌ Failed to send to self"
fi
echo ""

echo "5. DIRECTORY STRUCTURE TEST"
echo "=========================="
TODAY=$(date +%Y-%m-%d)
echo "📁 Testing directory creation:"

# Test if we can create the expected directory structure
for rep in rep1 rep2 rep3 rep4 rep5 rep6 rep7 rep8; do
    target_dir="/home/andrc1/Desktop/captured_images/$TODAY/$rep"
    
    if mkdir -p "$target_dir" 2>/dev/null; then
        echo "  ✅ $rep directory created/exists"
        
        # Test write permissions
        test_file="$target_dir/test_write.txt"
        if echo "test" > "$test_file" 2>/dev/null; then
            echo "    ✅ Write permissions OK"
            rm -f "$test_file"
        else
            echo "    ❌ Write permissions failed"
        fi
    else
        echo "  ❌ $rep directory creation failed"
    fi
done
echo ""

echo "6. VIDEO STREAM TEST"
echo "==================="
if [ "$IP" = "192.168.0.200" ] || [ "$HOSTNAME" = "control1" ]; then
    echo "📺 Testing rep8 video stream capability:"
    
    # Check if camera device exists
    if [ -e "/dev/video0" ]; then
        echo "  ✅ Camera device /dev/video0 exists"
        
        # Test camera access
        if [ -r "/dev/video0" ] && [ -w "/dev/video0" ]; then
            echo "  ✅ Camera permissions OK"
        else
            echo "  ❌ Camera permission issue"
            ls -la /dev/video0
        fi
    else
        echo "  ❌ No camera device found"
    fi
    
    # Send START_STREAM command to rep8
    echo "  📤 Sending START_STREAM to rep8..."
    echo "START_STREAM" | nc -u -w 2 127.0.0.1 5011
    
    echo "  ⏳ Waiting 3 seconds for stream to start..."
    sleep 3
    
    # Check if video stream is sending data to port 5002
    echo "  🔍 Checking if video data is being sent to master port 5002..."
    timeout 5 tcpdump -i lo port 5002 -c 5 2>/dev/null && echo "  ✅ Video traffic detected" || echo "  ❌ No video traffic"
    
else
    echo "📺 Remote replica video test (send START_STREAM to self):"
    echo "START_STREAM" | nc -u -w 2 $IP 5001
    sleep 2
    echo "  Check video_stream.service logs: sudo journalctl -u video_stream.service -n 10"
fi
echo ""

echo "7. PROCESS AND LOG CHECK"
echo "======================="
echo "🔍 Python processes:"
ps aux | grep python | grep -E '(video_stream|still_capture|local_camera)' | grep -v grep

echo ""
echo "📋 Recent service logs (last 5 lines):"
if [ "$IP" = "192.168.0.200" ] || [ "$HOSTNAME" = "control1" ]; then
    echo "  local_camera_slave.service:"
    sudo journalctl -u local_camera_slave.service -n 5 --no-pager
else
    echo "  video_stream.service:"
    sudo journalctl -u video_stream.service -n 3 --no-pager
    echo "  still_capture.service:"  
    sudo journalctl -u still_capture.service -n 3 --no-pager
fi

echo ""
echo "DIAGNOSTIC COMPLETE"
echo "=================="
echo "🎯 Action items based on results:"
echo "- ❌ items need attention"
echo "- ✅ items are working correctly"
echo ""
echo "To test GUI integration:"
echo "1. Start GUI on control1: cd master/camera_gui && python3 main.py"
echo "2. Click 'Start All Video Streams'"
echo "3. Go to Settings -> Camera Controls -> rep1 Settings"
echo "4. Change flip horizontal = True, click Apply Settings"
echo "5. Should see flip applied immediately in preview"
