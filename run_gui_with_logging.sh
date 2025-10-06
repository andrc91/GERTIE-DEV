#!/bin/bash
# GUI Testing Logger - Captures all GUI output, errors, and system activity
# Run this BEFORE launching the GUI to capture all testing activity

LOG_FILE="/home/andrc1/Desktop/updatelog.txt"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
GUI_LOG_TEMP="/tmp/gui_output_$$.log"

# Start logging session
echo "" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"
echo "[$TIMESTAMP] GUI TESTING SESSION STARTED" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# Capture system state before GUI launch
echo "[$TIMESTAMP] [INFO] System state before GUI launch:" >> "$LOG_FILE"
echo "[$TIMESTAMP] [INFO] Active services:" >> "$LOG_FILE"
systemctl --type=service --state=running | grep -E "(video_stream|still_capture|local_camera)" >> "$LOG_FILE" 2>&1

echo "[$TIMESTAMP] [INFO] Network connections:" >> "$LOG_FILE"
netstat -an | grep -E "(5001|5002|5003|5004|6000)" >> "$LOG_FILE" 2>&1

echo "[$TIMESTAMP] [INFO] Recent errors from slaves (last 10 lines each):" >> "$LOG_FILE"
for ip in 201 202 203 204 205 206 207; do
    echo "[$TIMESTAMP] [INFO] rep$((ip - 200)) (192.168.0.$ip):" >> "$LOG_FILE"
    ssh andrc1@192.168.0.$ip "journalctl -u video_stream.service -u still_capture.service --since '5 minutes ago' | grep -i error | tail -10" >> "$LOG_FILE" 2>&1 || echo "[$TIMESTAMP] [WARN] Could not fetch logs from 192.168.0.$ip" >> "$LOG_FILE"
done

echo "[$TIMESTAMP] [INFO] rep8 (local) recent errors:" >> "$LOG_FILE"
journalctl -u local_camera_slave.service --since '5 minutes ago' | grep -i error | tail -10 >> "$LOG_FILE" 2>&1

# Launch GUI with logging
echo "[$TIMESTAMP] [INFO] Launching GUI with output capture..." >> "$LOG_FILE"
echo "[$TIMESTAMP] [INFO] GUI output will be logged to: $GUI_LOG_TEMP" >> "$LOG_FILE"

# Run the GUI and capture all output
cd /home/andrc1/camera_system_integrated_final/master
python3 -m camera_gui.main 2>&1 | tee "$GUI_LOG_TEMP" &
GUI_PID=$!

echo "[$TIMESTAMP] [INFO] GUI launched with PID: $GUI_PID" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
echo "GUI is running. Press Ctrl+C to stop logging and append GUI output to updatelog.txt" >> "$LOG_FILE"

# Monitor GUI process and append output when it exits
trap "kill $GUI_PID 2>/dev/null" EXIT

# Wait for GUI to exit
wait $GUI_PID
EXIT_CODE=$?

# Append GUI output to main log
echo "" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] GUI SESSION ENDED (Exit code: $EXIT_CODE)" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] GUI output:" >> "$LOG_FILE"
cat "$GUI_LOG_TEMP" >> "$LOG_FILE"
rm "$GUI_LOG_TEMP"

# Capture system state after GUI exit
echo "" >> "$LOG_FILE"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] System state after GUI exit:" >> "$LOG_FILE"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] Recent errors from all services:" >> "$LOG_FILE"
for ip in 201 202 203 204 205 206 207; do
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] rep$((ip - 200)) (192.168.0.$ip) recent errors:" >> "$LOG_FILE"
    ssh andrc1@192.168.0.$ip "journalctl -u video_stream.service -u still_capture.service --since '10 minutes ago' | grep -i error | tail -10" >> "$LOG_FILE" 2>&1
done

echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] rep8 (local) recent errors:" >> "$LOG_FILE"
journalctl -u local_camera_slave.service --since '10 minutes ago' | grep -i error | tail -10 >> "$LOG_FILE" 2>&1

echo "" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] TESTING SESSION COMPLETE" >> "$LOG_FILE"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Full log saved to: $LOG_FILE" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

echo ""
echo "Testing session complete. Full log saved to: $LOG_FILE"
echo "To view errors only: grep ERROR $LOG_FILE"
echo ""
