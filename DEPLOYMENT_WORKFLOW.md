# GERTIE Deployment & Testing Workflow

## Overview
This document describes the complete workflow for deploying code changes and logging all system activity for debugging.

---

## 1. PREPARATION (On Your MacBook)

### Make Code Changes
```bash
cd ~/Desktop/camera_system_incremental
# Make your changes to the code
# Test locally if possible
```

### Commit Changes to Git
```bash
git add .
git commit -m "Description of changes"
```

### Copy to USB Drive
```bash
# Insert USB drive
cp -r ~/Desktop/camera_system_incremental /Volumes/YOUR_USB/camera_system_incremental
# Safely eject USB
```

---

## 2. DEPLOYMENT (On control1 Raspberry Pi)

### Transfer from USB to control1
```bash
# Insert USB into control1
# Copy directory
cp -r /media/usb/camera_system_incremental /home/andrc1/camera_system_integrated_final
cd /home/andrc1/camera_system_integrated_final
```

### Make Scripts Executable
```bash
chmod +x sync_to_slaves.sh
chmod +x run_gui_with_logging.sh
```

### Deploy to All Slaves
```bash
./sync_to_slaves.sh
```

**What this does:**
- Syncs code to all 7 remote slaves (rep1-7)
- Restarts services on all remote slaves
- Restarts local slave (rep8)
- Logs everything to `/home/andrc1/Desktop/updatelog.txt`
- Captures service status, errors, network info
- Shows deployment summary

**Expected output:**
```
========================================
[2025-10-06 14:23:45] DEPLOYMENT STARTED
========================================
...
Deployment completed successfully
Log file: /home/andrc1/Desktop/updatelog.txt
```

---

## 3. TESTING (On control1 Raspberry Pi)

### Launch GUI with Full Logging
```bash
cd /home/andrc1/camera_system_integrated_final
./run_gui_with_logging.sh
```

**What this does:**
- Captures system state before GUI launch
- Launches GUI and logs all output
- Monitors all 8 camera services
- Logs errors from all slaves
- Appends everything to `updatelog.txt` when GUI exits

### Perform Tests
While GUI is running:
1. Check all 8 camera previews are visible
2. Test aspect ratio (previews should be 16:9, not 4:3)
3. Capture images
4. Compare preview to captured images (WYSIWYG test)
5. Test camera controls
6. Test crop function
7. Note any errors, lag, or unexpected behavior

### Exit GUI
- Close GUI normally or press Ctrl+C
- All output automatically appends to updatelog.txt

---

## 4. LOG ANALYSIS

### View Full Log
```bash
cat /home/andrc1/Desktop/updatelog.txt
```

### View Recent Errors Only
```bash
grep ERROR /home/andrc1/Desktop/updatelog.txt | tail -50
```

### View Specific Section
```bash
# View most recent deployment
grep -A 50 "DEPLOYMENT STARTED" /home/andrc1/Desktop/updatelog.txt | tail -60

# View most recent GUI session
grep -A 100 "GUI TESTING SESSION" /home/andrc1/Desktop/updatelog.txt | tail -120
```

### Check Log Size
```bash
ls -lh /home/andrc1/Desktop/updatelog.txt
```

---

## 5. TRANSFER LOG FOR ANALYSIS (Back to MacBook)

### Copy Log to USB
```bash
# On control1
cp /home/andrc1/Desktop/updatelog.txt /media/usb/updatelog.txt
# Safely eject USB
```

### On MacBook
```bash
# Insert USB
cp /Volumes/YOUR_USB/updatelog.txt ~/Desktop/
# Feed to Claude for analysis
```

---

## Log File Structure

The `updatelog.txt` file contains:

### Deployment Sections
- Timestamp and git info (branch, commit)
- Sync status for each slave (rep1-8)
- Service restart status
- Service health checks
- Recent error logs from each slave
- Network connectivity status
- System resource usage

### GUI Testing Sections
- System state before GUI launch
- All active services
- Network connections
- Recent errors from all slaves
- Complete GUI output (stdout/stderr)
- System state after GUI exit
- Post-test error summary

---

## Troubleshooting

### If deployment fails:
```bash
# Check individual slave connectivity
ping 192.168.0.201  # rep1
ping 192.168.0.202  # rep2
# etc...

# Check SSH access
ssh andrc1@192.168.0.201

# View deployment log
tail -100 /home/andrc1/Desktop/updatelog.txt
```

### If services don't restart:
```bash
# Check service status on specific slave
ssh andrc1@192.168.0.201 "systemctl status video_stream.service"

# View service logs
ssh andrc1@192.168.0.201 "journalctl -u video_stream.service -n 50"

# Manual restart
ssh andrc1@192.168.0.201 "sudo systemctl restart video_stream.service"
```

### If GUI won't launch:
```bash
# Check Python dependencies
python3 -c "import picamera2, cv2, tkinter"

# Check for port conflicts
netstat -an | grep -E "(5001|5002|6000)"

# View recent GUI errors
grep GUI /home/andrc1/Desktop/updatelog.txt | tail -20
```

---

## Quick Reference Commands

### On control1:
```bash
# Deploy changes
./sync_to_slaves.sh

# Test with logging
./run_gui_with_logging.sh

# View log
cat /home/andrc1/Desktop/updatelog.txt

# View errors only
grep ERROR /home/andrc1/Desktop/updatelog.txt

# Clear old logs (optional, creates backup)
mv /home/andrc1/Desktop/updatelog.txt /home/andrc1/Desktop/updatelog_backup_$(date +%Y%m%d_%H%M%S).txt
touch /home/andrc1/Desktop/updatelog.txt
```

### Check all cameras:
```bash
for ip in 201 202 203 204 205 206 207; do
    echo "Checking rep$((ip-200)) (192.168.0.$ip)..."
    ping -c 1 192.168.0.$ip && echo "✓ Reachable" || echo "✗ Not reachable"
done
```

---

## Notes

- **updatelog.txt** is append-only - it grows with each deployment/test cycle
- Each session is timestamped and clearly separated
- Log file location: Always `/home/andrc1/Desktop/updatelog.txt`
- If log gets too large (>100MB), archive it and start fresh
- All errors are tagged with `[ERROR]` for easy grepping
- Git commit info is logged with each deployment for traceability
