# GERTIE-DEV - 8-Camera Scientific Imaging Platform

## Development Repository for GERTIE Camera System

This is the active development repository for GERTIE (Giant Eight-camera Rig for Taxon Image Extraction).

### Current Status
- **Branch**: master (baseline)  
- **Active Fix**: WYSIWYG aspect ratio correction (16:9 preview/capture matching)
- **Deployment Method**: USB transfer → control1 → sync_to_slaves.sh → 8 cameras

### Repository Links
- **Development Repo**: [https://github.com/andrc91/GERTIE-DEV](https://github.com/andrc91/GERTIE-DEV) (this repo)
- **Reference System**: [https://github.com/andrc1/GERTIE](https://github.com/andrc1/GERTIE) (GOLDEN_REFERENCE)

## Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/andrc91/GERTIE-DEV.git
cd GERTIE-DEV
```

### 2. Deploy to Hardware
```bash
# Copy to USB, then on control1:
cd /home/andrc1/camera_system_integrated_final
./sync_to_slaves.sh
./run_gui_with_logging.sh
```

### 3. Collect Logs
```bash
# After testing, copy log from control1:
cp /home/andrc1/Desktop/updatelog.txt /media/usb/
```

## Priority P0 Fixes (Critical Blockers)

1. **WYSIWYG Aspect Ratio** ✅ Fix applied, needs testing
   - Preview: 640x360 (16:9)
   - Capture: 4608x2592 (16:9)
   
2. **Time Synchronization** 🔄 Next priority
   - Auto-sync from control1 on GUI launch
   
3. **Telemetry Logging** 🔄 Planned
   - Comprehensive event logging
   
4. **System Lag Reduction** 🔄 Planned
   - Target: <2 second response
   
5. **Camera Capture Reliability** 🔄 Planned
   - Auto-recovery on failure

## Project Structure
```
GERTIE-DEV/
├── master/             # GUI controller (runs on control1)
├── slave/              # Camera services (runs on rep1-rep8)
├── sync_to_slaves.sh   # Deployment script
├── run_gui_with_logging.sh  # Testing script
└── DEPLOYMENT_WORKFLOW.md   # Full deployment guide
```

## System Architecture
- **control1**: Master node (Raspberry Pi) - GUI and orchestration
- **rep1-rep8**: Camera nodes (Raspberry Pi) - Image capture services
- **Network**: 192.168.0.x subnet
- **Ports**: 6000 (capture), 5000-5007 (preview)

## Testing Workflow

1. **Make changes** on MacBook
2. **Copy to USB**: `cp -r GERTIE-DEV /Volumes/USB/`
3. **Deploy on control1**: Run sync_to_slaves.sh
4. **Test**: Run GUI with logging
5. **Analyze**: Review updatelog.txt

## Development Guidelines

- Always maintain 16:9 aspect ratio (preview and capture)
- Port 6000 for still capture (DO NOT CHANGE)
- All camera settings must sync between video_stream.py and still_capture.py
- Commit after each fix with descriptive message
- Test on hardware before merging

## Contact
- Repository: andrc91 (acranephoto@gmail.com)
- System: GERTIE scientific imaging platform

---
*Last Updated: October 6, 2025*
