# 8-Camera System Troubleshooting Guide

**System**: camera_system_integrated_final  
**Hardware**: 8 Raspberry Pi cameras (rep1-rep7 networked, rep8 local)  
**Control**: MacBook → USB → control1 Pi → sync_to_slaves.sh → all cameras  
**Last Updated**: 2025-10-15

---

## Quick Diagnostics

### Fastest Problem Identification

Run these commands on **control1** to quickly identify issues:

```bash
# Check all camera services status
for i in {1..8}; do 
    ssh rep$i "systemctl status video_stream.service still_capture.service | grep Active"
done

# Check network connectivity
for i in {1..8}; do 
    ping -c 1 rep$i && echo "rep$i: OK" || echo "rep$i: FAILED"
done

# Check running processes
for i in {1..8}; do
    ssh rep$i "ps aux | grep -E 'video_stream|still_capture' | grep -v grep" 
done
```

### Quick Health Check Script
Location: `/home/andrc1/camera_system_integrated_final/troubleshooting/quick_camera_diag.sh`

```bash
cd ~/camera_system_integrated_final/troubleshooting
./quick_camera_diag.sh
```

---

## Common Issues & Solutions

### Issue 1: Camera Not Streaming Video

**Symptoms**: Black preview window, no video feed

**Quick Fix**:
```bash
# On control1, restart the camera's video service
ssh rep[N] "sudo systemctl restart video_stream.service"

# Check service status
ssh rep[N] "systemctl status video_stream.service"

# Check logs for errors
ssh rep[N] "journalctl -u video_stream.service -n 50"
```

**Root Causes**:
- Service crashed or stopped
- Network connection lost
- Camera hardware not initialized
- Port conflict (5000-5007)

**Verification**: GUI should show green status dot and live preview within 5 seconds

---

### Issue 2: Still Capture Not Working

**Symptoms**: Capture button pressed but no image appears, timeout errors

**Quick Fix**:
```bash
# Restart still_capture service on affected camera
ssh rep[N] "sudo systemctl restart still_capture.service"

# Verify service is listening
ssh rep[N] "netstat -tlnp | grep 600[N]"

# Test manual capture
ssh rep[N] "curl -X POST http://localhost:600[N]/capture"
```

**Root Causes**:
- Service not running
- Port 600[N] not accessible
- Camera busy with another operation
- Picamera2 lock held by another process

---

### Issue 3: All Cameras Not Responding

**Symptoms**: Multiple cameras offline, network unreachable

**Quick Fix**:
```bash
# Check network switch/router
ping 192.168.1.1

# Check control1 connectivity
ping control1
for i in {1..8}; do ping -c 1 rep$i; done

# Restart all services (on control1)
cd ~/camera_system_integrated_final
./sync_to_slaves.sh  # Redeploy code
for i in {1..8}; do 
    ssh rep$i "sudo systemctl restart video_stream.service still_capture.service"
done
```

**Root Causes**:
- Network infrastructure failure
- Power loss to switch/hub
- control1 Pi offline
- DHCP lease issues

---

### Issue 4: Rep8 Local Camera Issues

**Symptoms**: Rep8 (MacBook local camera) not working, others OK

**Quick Fix**:
```bash
# Check if local process is running
ps aux | grep local_camera_slave

# Restart local camera service
cd ~/Desktop/camera_system_integrated_final
python3 local_camera_slave.py &

# Check port 6008
netstat -an | grep 6008
```

**Root Causes**:
- Local service not started (rep8 runs differently than Pi cameras)
- Port 6008 conflict with another application
- MacBook camera access permission denied
- Process crashed without restart (no systemd on MacBook)

---

## Service Management

### SystemD Service Control (on Pi cameras rep1-rep7)

**Video Streaming Service**: `video_stream.service`  
**Still Capture Service**: `still_capture.service`

```bash
# Check status
ssh rep[N] "systemctl status video_stream.service"
ssh rep[N] "systemctl status still_capture.service"

# Start services
ssh rep[N] "sudo systemctl start video_stream.service"
ssh rep[N] "sudo systemctl start still_capture.service"

# Stop services
ssh rep[N] "sudo systemctl stop video_stream.service"
ssh rep[N] "sudo systemctl stop still_capture.service"

# Restart services (most common fix)
ssh rep[N] "sudo systemctl restart video_stream.service still_capture.service"

# Enable services (auto-start on boot)
ssh rep[N] "sudo systemctl enable video_stream.service still_capture.service"

# View service logs
ssh rep[N] "journalctl -u video_stream.service -n 100"
ssh rep[N] "journalctl -u still_capture.service -n 100"

# Follow logs in real-time
ssh rep[N] "journalctl -u video_stream.service -f"
```

### Restart All Cameras Script

```bash
#!/bin/bash
# restart_all_cameras.sh - Run on control1

for i in {1..7}; do
    echo "Restarting rep$i services..."
    ssh rep$i "sudo systemctl restart video_stream.service still_capture.service"
done
echo "All camera services restarted"
```

---
## Log File Locations

### Primary System Log (Most Important)
**Location**: `/home/andrc1/Desktop/updatelog.txt` (on control1 Pi)

This file contains:
- GUI operation logs
- Deployment success/failure messages
- Network communication logs
- Camera response times
- Error messages and stack traces

```bash
# View recent logs (on control1)
tail -100 ~/Desktop/updatelog.txt

# Search for errors
grep -i error ~/Desktop/updatelog.txt

# Watch logs in real-time
tail -f ~/Desktop/updatelog.txt

# Copy to USB for analysis on MacBook
cp ~/Desktop/updatelog.txt /media/USB/
```

### Service Logs (Per Camera)

**Video Stream Service**: 
```bash
ssh rep[N] "journalctl -u video_stream.service -n 100"
ssh rep[N] "journalctl -u video_stream.service --since '10 minutes ago'"
```

**Still Capture Service**:
```bash
ssh rep[N] "journalctl -u still_capture.service -n 100"
ssh rep[N] "journalctl -u still_capture.service --since today"
```

### System Logs (General Pi Issues)
```bash
# System messages
ssh rep[N] "tail -50 /var/log/syslog"

# Kernel messages (hardware issues)
ssh rep[N] "dmesg | tail -50"
```

---
## Network Diagnostics

### Test Camera Connectivity

```bash
# Basic ping test (on control1)
ping -c 3 rep1
ping -c 3 rep2
# ... etc for rep3-rep8

# Test all cameras at once
for i in {1..8}; do
    ping -c 1 rep$i && echo "✓ rep$i OK" || echo "✗ rep$i FAILED"
done
```

### Test Service Ports

**Video Stream Ports**: 5000-5007  
**Still Capture Ports**: 6000-6007

```bash
# Test if ports are listening
ssh rep[N] "netstat -tlnp | grep 500[N]"  # Video
ssh rep[N] "netstat -tlnp | grep 600[N]"  # Stills

# Test port connectivity from control1
nc -zv rep[N] 500[N]  # Video port
nc -zv rep[N] 600[N]  # Still port

# Test HTTP endpoint
curl -v http://rep[N]:500[N]/  # Should respond
curl -X POST http://rep[N]:600[N]/capture  # Trigger capture
```

### Network Performance Testing

```bash
# Check latency
ping -c 10 rep[N]

# Bandwidth test (if iperf3 installed)
# On camera: iperf3 -s
# On control1: iperf3 -c rep[N]
```

---
## Camera-Specific Issues

### Rep8 (MacBook Local Camera)

**Unique Characteristics**:
- Runs directly on MacBook (not a Pi)
- No systemd service management
- Uses local_camera_slave.py script
- Port 6008 for still capture
- Must be started manually

**Starting Rep8**:
```bash
cd ~/Desktop/camera_system_integrated_final
python3 local_camera_slave.py &

# Verify it's running
ps aux | grep local_camera_slave
netstat -an | grep 6008
```

**Common Rep8 Issues**:
- Process dies without systemd restart
- MacBook camera permissions denied
- Port 6008 conflict
- Solution: Kill and restart process

### Rep1-Rep7 (Raspberry Pi Cameras)

**Standard Pi Issues**:
```bash
# Check Pi is accessible
ping rep[N]

# Check services
ssh rep[N] "systemctl status video_stream.service still_capture.service"

# Restart services
ssh rep[N] "sudo systemctl restart video_stream.service still_capture.service"

# Check camera hardware
ssh rep[N] "vcgencmd get_camera"  # Should show "detected=1"
```

---
## Settings Troubleshooting

### Settings Files Location
**Master Settings**: `camera_system_integrated_final/master/config/settings.json`  
**Per-Camera Settings**: `rep[N]_settings.json` (in project root)

### Common Settings Issues

**Issue**: Settings changes not taking effect

**Solution**:
```bash
# On MacBook - verify settings files exist
cd ~/Desktop/camera_system_integrated_final
ls -la rep*.json

# After changing settings, redeploy
./sync_to_slaves.sh  # Copies settings to all cameras

# Restart services to apply new settings
for i in {1..7}; do
    ssh rep$i "sudo systemctl restart video_stream.service still_capture.service"
done
```

**Issue**: Settings reset after reboot

**Root Cause**: Settings file not persisted or service reading wrong file

**Solution**:
```bash
# Check which settings file the service is reading
ssh rep[N] "ps aux | grep video_stream"

# Ensure settings are in correct location
ssh rep[N] "ls -la ~/camera_system_integrated_final/rep[N]_settings.json"
```

### Settings Validation

```bash
# Check settings file syntax (must be valid JSON)
python3 -c "import json; json.load(open('rep1_settings.json'))"

# Common setting keys to check:
# - resolution
# - framerate  
# - exposure_mode
# - awb_mode
```

---
## Emergency Procedures

### System Not Responding - Full Reset

**When to Use**: Multiple cameras offline, GUI frozen, network issues

**Procedure**:
```bash
# 1. On control1 Pi via SSH or direct keyboard
cd ~/camera_system_integrated_final

# 2. Stop all services
for i in {1..7}; do
    ssh rep$i "sudo systemctl stop video_stream.service still_capture.service"
done

# 3. Wait 5 seconds
sleep 5

# 4. Start all services
for i in {1..7}; do
    ssh rep$i "sudo systemctl start video_stream.service still_capture.service"
done

# 5. Restart GUI
cd ~/camera_system_integrated_final
./run_gui_with_logging.sh
```

### Rollback to Previous Version

**When to Use**: New deployment broke system, need stable version

**Procedure**:
```bash
# On MacBook
cd ~/Desktop/camera_system_integrated_final

# Check available git tags
git tag -l

# Rollback to last tested version
git checkout tested-status-indicators-20251015

# Redeploy to cameras
# Copy to USB, then on control1:
cd ~/camera_system_integrated_final
./sync_to_slaves.sh

# Restart all services
for i in {1..7}; do
    ssh rep$i "sudo systemctl restart video_stream.service still_capture.service"
done
```

---
### Emergency: Single Camera Hardware Failure

**Symptoms**: One camera completely unresponsive, others OK

**Procedure**:
```bash
# 1. Check physical connections
# - Power cable
# - Network cable
# - Camera ribbon cable

# 2. Reboot the Pi
ssh rep[N] "sudo reboot"

# 3. If still not responding, check from another Pi
ssh rep[M] "ping rep[N]"
ssh rep[M] "ssh rep[N]"

# 4. Physical access may be required:
# - Remove SD card
# - Reflash with backup image
# - Restore camera_system_integrated_final code
```

### Emergency: Network Infrastructure Failure

**Symptoms**: No cameras reachable, network down

**Procedure**:
1. Check physical network switch/hub power
2. Restart network switch
3. Check control1 Pi can ping router: `ping 192.168.1.1`
4. Check DHCP leases are being assigned
5. Restart all Pis if necessary

---

## Deployment Workflow Reference

### Standard Deployment Process

**Always use sync_to_slaves.sh - NO EXCEPTIONS**

```bash
# On MacBook
cd ~/Desktop/camera_system_integrated_final
git status  # Ensure changes committed
git log -1  # Note commit hash

# Copy to USB drive
cp -r camera_system_integrated_final /Volumes/USB/
```

```bash
# On control1 Pi
cd /home/andrc1
cp -r /media/USB/camera_system_integrated_final ./

# Deploy to all cameras
cd camera_system_integrated_final
./sync_to_slaves.sh

# Restart services on all cameras
for i in {1..7}; do
    ssh rep$i "sudo systemctl restart video_stream.service still_capture.service"
done

# Start GUI with logging
./run_gui_with_logging.sh

# Monitor logs
tail -f ~/Desktop/updatelog.txt

# After testing, copy logs back to USB
cp ~/Desktop/updatelog.txt /media/USB/
```

---

## Quick Reference Commands

### Most Common Fixes

```bash
# Restart single camera (on control1)
ssh rep[N] "sudo systemctl restart video_stream.service still_capture.service"

# Restart all cameras
for i in {1..7}; do ssh rep$i "sudo systemctl restart video_stream.service still_capture.service"; done

# Check all camera status
for i in {1..8}; do ping -c 1 rep$i && echo "✓ rep$i" || echo "✗ rep$i"; done

# View recent errors
tail -100 ~/Desktop/updatelog.txt | grep -i error

# Redeploy code
cd ~/camera_system_integrated_final && ./sync_to_slaves.sh
```

---
## Step-by-Step Diagnostic Checklist

When troubleshooting any issue, follow this systematic approach:

### 1. Identify the Problem
- [ ] Which camera(s) affected? (rep1-8 or all)
- [ ] What operation failing? (streaming, capture, settings)
- [ ] Error messages? (check updatelog.txt)
- [ ] When did it start? (after deployment, reboot, etc.)

### 2. Check Connectivity
- [ ] Can you ping the camera? `ping rep[N]`
- [ ] Can you SSH to the camera? `ssh rep[N]`
- [ ] Are services running? `systemctl status video_stream.service`

### 3. Check Services
- [ ] Video stream service active?
- [ ] Still capture service active?
- [ ] Ports listening? `netstat -tlnp | grep 500[N]`
- [ ] Service logs show errors? `journalctl -u video_stream.service -n 50`

### 4. Try Basic Fixes
- [ ] Restart services: `sudo systemctl restart video_stream.service still_capture.service`
- [ ] Check logs: `tail -100 ~/Desktop/updatelog.txt`
- [ ] Verify settings: `cat rep[N]_settings.json`

### 5. Advanced Diagnostics
- [ ] Compare with working camera configuration
- [ ] Check hardware: `vcgencmd get_camera`
- [ ] Network performance: `ping -c 10 rep[N]`
- [ ] Review recent deployments: `git log -10`

### 6. Document & Escalate
- [ ] Copy updatelog.txt to USB
- [ ] Note exact error messages
- [ ] Document steps already tried
- [ ] Check GERTIE_SESSION_LOG.md for similar issues

---
## Important File Paths Reference

### On MacBook
- Project: `/Users/andrew1/Desktop/camera_system_integrated_final`
- Session Log: `/Users/andrew1/Desktop/GERTIE_SESSION_LOG.md`
- Golden Reference: `/Users/andrew1/Desktop/GOLDEN_REFERENCE_DO_NOT_TOUCH`
- Salvaged Knowledge: `/Users/andrew1/Desktop/GERTIE_SALVAGED_KNOWLEDGE`

### On control1 Pi
- Project: `/home/andrc1/camera_system_integrated_final`
- Logs: `/home/andrc1/Desktop/updatelog.txt`
- Deployment: `/home/andrc1/camera_system_integrated_final/sync_to_slaves.sh`
- GUI Launcher: `/home/andrc1/camera_system_integrated_final/run_gui_with_logging.sh`

### On Each Camera Pi (rep1-rep7)
- Project: `/home/andrc1/camera_system_integrated_final`
- Video Service: `/etc/systemd/system/video_stream.service`
- Still Service: `/etc/systemd/system/still_capture.service`
- Settings: `/home/andrc1/camera_system_integrated_final/rep[N]_settings.json`

---

## Summary

This troubleshooting guide covers:
✓ Quick diagnostic procedures  
✓ Common issues with tested solutions  
✓ Service management commands  
✓ Log file locations and interpretation  
✓ Network diagnostic procedures  
✓ Camera-specific troubleshooting  
✓ Settings troubleshooting  
✓ Emergency recovery procedures  
✓ Deployment workflow reference  
✓ Systematic diagnostic checklist  

**Remember**: Always use `sync_to_slaves.sh` for deployment, check `updatelog.txt` first, restart services as first fix attempt.

---

**Document Version**: 1.0  
**Last Updated**: 2025-10-15  
**System Version**: commit 32af4e4
