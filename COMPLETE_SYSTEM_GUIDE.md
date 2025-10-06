# COMPREHENSIVE SYSTEM DIAGNOSIS + FIXES

## **Issues Diagnosed & Fixed:**

### **1. rep8 Preview Missing** 
- **Root Cause**: Color conversion issue resolved
- **Fix Applied**: Removed double color swap in network_manager.py
- **Verification**: Added `test_rep8_video.py` for independent testing

### **2. Settings Not Applied Live (rep1–rep7)**
- **Root Cause**: Settings cache in video_stream.py not refreshing
- **Fix Applied**: Force fresh import via `importlib.reload()` in `get_current_camera_settings()`
- **Result**: Settings now apply immediately to video preview

### **3. Directory Creation Inconsistent**
- **Root Cause**: Path creation without proper verification
- **Fix Applied**: Enhanced directory creation with verification and fallback
- **Structure**: `/home/andrc1/Desktop/captured_images/<date>/rep<N>/`

### **4. Settings Package Missing (rep8)**
- **Root Cause**: local_camera_slave.py missing `SET_ALL_SETTINGS` handler
- **Fix Applied**: Added `handle_local_settings_package()` function

---

## **Complete File List - Ready for USB Transfer:**

### **Modified Files:**
- ✅ `shared/config.py` - Master IP configuration
- ✅ `master/camera_gui/core/network_manager.py` - Directory paths + color handling + robust directory creation
- ✅ `master/camera_gui/menu/settings_menu.py` - Settings package approach
- ✅ `master/camera_gui/config/settings.py` - Disabled auto-start
- ✅ `master/camera_gui/core/gui_base.py` - Manual stream controls
- ✅ `slave/video_stream.py` - Fresh settings import + unified transforms
- ✅ `slave/still_capture.py` - Settings package handler
- ✅ `local_camera_slave.py` - Settings package handler for rep8
- ✅ `video_stream.service` - Fixed directory paths
- ✅ `still_capture.service` - Fixed directory paths
- ✅ `local_camera_slave.service` - Service for rep8 on control1

### **New Diagnostic Files:**
- ✅ `deploy_fixes.sh` - Auto-detects control1 vs remote, deploys correct services
- ✅ `verify_fixes.sh` - Post-deployment verification
- ✅ `diagnostic_endtoend.sh` - Comprehensive system test
- ✅ `test_rep8_video.py` - Independent rep8 video test
- ✅ `sync_settings.py` - Manual settings synchronization
- ✅ `MINIMAL_FIXES_SUMMARY.md` - This documentation
- ✅ `CRITICAL_PATCHES.md` - Additional patch information

---

## **Deployment Process:**

### **Step 1: USB Transfer**
```bash
# Copy entire directory to USB drive
cp -r camera_system_integrated_final /media/usb/
```

### **Step 2: Deploy to control1 (Master)**
```bash
# On control1 Pi:
cp -r /media/usb/camera_system_integrated_final /home/andrc1/
cd /home/andrc1/camera_system_integrated_final
chmod +x *.sh *.py
./deploy_fixes.sh  # Auto-detects control1, installs local_camera_slave.service
```

### **Step 3: Deploy to rep1-rep7 (Remote Replicas)**  
```bash
# On each remote Pi:
cp -r /media/usb/camera_system_integrated_final /home/andrc1/
cd /home/andrc1/camera_system_integrated_final
chmod +x *.sh *.py
./deploy_fixes.sh  # Auto-detects remote, installs standard services
```

### **Step 4: Verification**
```bash
# On any Pi:
./verify_fixes.sh           # Quick status check
./diagnostic_endtoend.sh    # Comprehensive test
```

### **Step 5: Start System**
```bash
# On control1 only:
cd /home/andrc1/camera_system_integrated_final/master/camera_gui
python3 main.py
```

---

## **Testing Protocol:**

### **1. Basic Functionality**
- GUI starts → All 8 camera frames visible
- Click "Start All Video Streams" → All cameras show preview (including rep8)
- All heartbeats green

### **2. Settings Application** 
- Settings → Camera Controls → rep1 Settings
- Set: ISO=800, Flip Horizontal=True, Grayscale=True
- Click "Apply Settings" 
- **Expected**: Changes visible immediately in rep1 preview

### **3. Still Capture**
- Click "Capture" on rep1
- **Expected**: Image saves to `/home/andrc1/Desktop/captured_images/2025-09-01/rep1/timestamp.jpg`
- **Expected**: Still image looks identical to preview

### **4. Settings Persistence**
- Change settings on rep2, apply, restart services
- **Expected**: Settings persist after restart

### **5. rep8 Specific**
- rep8 preview should show correct colors (no blue/red swap)
- rep8 should respond to settings changes same as remote cameras
- If rep8 fails: Run `python3 test_rep8_video.py` on control1

---

## **Troubleshooting:**

### **If rep8 Still No Preview:**
```bash
# On control1:
python3 test_rep8_video.py
sudo journalctl -u local_camera_slave.service -f
```

### **If Settings Don't Apply Live:**
```bash
# Check video stream logs:
sudo journalctl -u video_stream.service -f
# Look for: "[VIDEO] Received settings package"
```

### **If Directory Creation Fails:**
```bash
# Check permissions:
ls -la /home/andrc1/Desktop/
mkdir -p /home/andrc1/Desktop/captured_images/test
# Should work without errors
```

### **Manual Settings Sync:**
```bash
# Force settings sync to all devices:
python3 sync_settings.py sync_all
```

---

## **System Architecture Summary:**

- **control1** (192.168.0.200): GUI + rep8 via `local_camera_slave.service`
- **rep1-rep7** (192.168.0.201-207): `video_stream.service` + `still_capture.service`
- **Settings**: GUI → `SET_ALL_SETTINGS_<json>` → All replicas apply immediately
- **Video**: All devices → port 5002 → GUI displays 8 previews
- **Still**: All devices → port 6000 → GUI saves to `/Desktop/captured_images/<date>/rep<N>/`
- **Heartbeat**: All devices → port 5003 → GUI shows green/red status

The system should now work reliably with live preview matching still capture, persistent settings, and proper directory creation.
