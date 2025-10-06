# GERTIE SYSTEM UPGRADES - PRIORITIZED LIST

**Date**: 2025-10-06  
**Last Updated**: 2025-10-06 (Streamlined camera controls)
**Source**: ABSOLUTE_COMPREHENSIVE_FEATURES_UPDATES_LIST.md

**Recent Changes**:
- ✓ Removed digital gain, white balance presets, fine R/B gain adjustment, noise reduction, frame duration limits, video stabilization, manual lens position
- ✓ Streamlined camera controls to essential parameters only
- ✓ Updated effort estimate: Camera controls now 2-3 days (was 4-5 days)

---

## P0 - PRODUCTION BLOCKERS (Must fix before any use)

**Timeline**: 3-5 weeks | **Effort**: 14-20 days + hardware

1. **WYSIWYG Synchronization** (3-5 days)
   - Match preview aspect ratio to 16:9 (change from 4:3)
   - Implement coordinate scaling between preview (640px) and sensor (4608px)
   - Test all transforms at both resolutions
   - Verify crop coordinates scale proportionally

2. **Telemetry Logging System** (2-3 days)
   - Log every capture attempt with timestamp
   - Record all settings applied per capture
   - Track network events and errors
   - Store metadata with each image file
   - Implement synchronized clock system

3. **System Lag Reduction** (3-4 days)
   - Profile network usage across 8 streams
   - Test lower preview resolutions
   - Implement async frame processing
   - Add request batching/caching
   - Reduce FPS to 5-8 for focus checking only

4. **Camera Capture Reliability** (3-4 days)
   - Implement watchdog monitoring per camera
   - Add auto-restart on failure detection
   - Enhanced error handling and recovery
   - Fix memory leak issues
   - Achieve zero crashes in 4+ hour sessions

5. **Dome Height Hardware** (URGENT)
   - Increase clearance to minimum 15cm for forceps
   - Physical modification required
   - Test with actual workflow tools

6. **Platform Ergonomics Hardware** (URGENT)
   - Adjustable height platform design
   - Address back pain reported by 50% of users
   - Physical modification required

---

## P1 - HIGH PRIORITY (Essential for workflow)

**Timeline**: Additional 4-5 weeks | **Effort**: 17-24 days

### Camera Calibration & Controls (5-6 days)

7. **Camera Calibration System** (3-4 days)
   - Lens distortion correction per camera
   - OpenCV cv2.calibrateCamera integration
   - Checkerboard pattern detection (20-30 images)
   - Calculate camera matrix and distortion coefficients
   - Save per-camera calibration profiles (rep1-8_calibration.json)
   - Apply undistortion to all captures

8. **Shutter Speed / Exposure Time** (1 day)
   - Range: 100µs - 10 seconds
   - GUI slider (log scale) + numeric input
   - Auto mode toggle
   - Sync between preview and still capture

9. **ISO / Analogue Gain** (<1 day)
   - Verify existing implementation
   - Ensure preview/still synchronization
   - Range: 100-6400

10. **Exposure Compensation** (<1 day)
    - Range: ±8.0 EV
    - GUI slider in 0.5 EV steps
    - Works in auto-exposure mode only

11. **White Balance Control** (1 day)
    - Auto mode (current default)
    - Manual color temperature (2000K-10000K)
    - Real-time preview of changes

12. **Sharpness Control** (<1 day)
    - Range: 0.0 - 4.0 (1.0 = normal)
    - GUI slider
    - Warning about over-sharpening artifacts

### GUI Improvements (3-5 days)

13. **Interactive Crop Box** (1 day)
    - Click & drag on preview to set crop
    - Visual crop rectangle overlay
    - Aspect ratio locking
    - Reset button

14. **Visual Status Indicators** (2-3 days)
    - Green/yellow/red dots per camera
    - Heartbeat visualization
    - Real-time connection status
    - Network quality indicators
    - Error state tooltips

15. **Audio Feedback** (<1 day)
    - File already exists (shutter.wav)
    - Add trigger to capture event
    - Enable/disable checkbox
    - Volume control

16. **Progress Indicators** (1 day)
    - Capture progress bar (8 cameras)
    - Individual camera status during capture
    - File save progress
    - Estimated time remaining

17. **Keyboard Shortcuts** (1 day)
    - Space: Capture all
    - 1-8: Toggle individual camera
    - S: Settings panel
    - G: Gallery panel
    - R: Restart streams
    - Esc: Close dialogs
    - Ctrl+Q: Quit

18. **Enhanced Preview Size** (1-2 days)
    - Adjustable grid layout (2x4, 4x2, 1x8)
    - Individual camera zoom/expand
    - Full-screen preview mode
    - Responsive window sizing

### System Integration (4 days)

19. **Feature Toggle Integration** (1 day)
    - Connect FeatureToggleManager to GUI
    - Load production_feature_config.json
    - Test dynamic enable/disable

20. **Hardware Controls Connection** (2 days)
    - Add network protocol for hardware commands
    - Implement in network_manager.py
    - Test real-time camera response

21. **Module Import Fix (rep8)** (1 day)
    - Fix PYTHONPATH for local camera
    - Correct import paths in local_camera_slave.py
    - Test rep8 functionality

22. **Troubleshooting Guide** (1 day)
    - Common issues documentation
    - Error message meanings
    - Recovery procedures
    - Service management commands
    - Log file locations

---

## P2 - MEDIUM PRIORITY (Polish & features)

**Timeline**: Additional 5-6 weeks | **Effort**: 23-32 days

### Image & Resolution Controls (2-4 days)

23. **Resolution Switching** (1-2 days)
    - Video: 640x360, 854x480, 1280x720 (all 16:9)
    - Still: Full, half, quarter sensor
    - Per-camera override

24. **JPEG Quality Sync** (<1 day)
    - Ensure same quality preview and still
    - GUI slider 50-100
    - Per-camera override

### GUI Organization (5-7 days)

25. **Per-Camera UI Tabs** (1-2 days)
    - Tab-based camera selector
    - Apply to selected camera(s)
    - "Apply to All" button

26. **Settings Profile System** (2 days)
    - Save/load named profiles
    - Default profiles (macro, low-light, high-contrast)
    - Profile import/export
    - Quick-switch dropdown

27. **Metadata Tagging GUI** (3-4 days)
    - Text fields: specimen ID, location, date, notes
    - Auto-populate common fields
    - Per-camera metadata override
    - CSV export
    - Metadata templates/presets

28. **Gallery Enhancements** (2-3 days)
    - Thumbnail grid of recent captures
    - Image viewer with zoom/pan
    - Side-by-side compare mode
    - Delete/archive functions
    - Metadata display
    - Batch operations

### System Features (3-4 days)

29. **File Organization** (1 day)
    - Standardized directory structure
    - ISO 8601 timestamp format
    - Camera ID in filenames
    - Metadata sidecar files (.json)
    - Optional automatic cleanup

30. **Device Naming** (<1 day)
    - Replace "rep1-rep8" with custom names
    - Store in settings JSON
    - Display throughout GUI
    - Name validation

31. **System Shutdown/Reboot** (1-2 days)
    - Remote Pi shutdown from GUI
    - Graceful service stop
    - Reboot individual or all cameras
    - Safety confirmation dialogs

### Code Quality (3-4 days)

32. **Requirements.txt Fix** (<1 hour)
    - Add picamera2, requests, matplotlib
    - Add paramiko, psutil
    - Use requirements_complete.txt

33. **Calibration Wizard Completion** (2-3 days)
    - Integrate cv2.calibrateCamera
    - Image processing for calibration
    - Camera matrix calculation
    - Result validation and export

34. **Duplicate Function Check** (1 day)
    - Scan all Python files
    - Verify no conflicting calls
    - Check import paths

### Documentation (6-8 days)

35. **User Manual** (3-4 days)
    - Quick start guide (15 min to first capture)
    - Hardware setup and calibration
    - GUI walkthrough with screenshots
    - Common workflows
    - Settings explained
    - Best practices
    - Technical specifications

36. **Technical Documentation** (2-3 days)
    - System architecture diagram
    - Network topology and ports
    - Code structure and dependencies
    - UDP command API
    - Settings file format
    - Deployment procedures

### Testing Infrastructure (5-6 days)

37. **Integration Tests** (3-4 days)
    - End-to-end capture workflow
    - Settings persistence tests
    - Network communication tests
    - Multi-camera synchronization
    - Error recovery scenarios

38. **Load Testing Framework** (2 days)
    - 4+ hour continuous operation
    - 1000+ captures without restart
    - Network congestion scenarios
    - Memory leak detection
    - CPU/GPU usage monitoring

---

## P3 - FUTURE ENHANCEMENTS (Post-v1.0)

**Estimated**: 30+ days for all future features

### Advanced Camera Features (8-12 days)

39. FPS selection for preview (5/10/15/30/60)
40. Focus peaking visualization
41. Histogram display per camera
42. Zebra stripes for overexposure warning
43. Waveform monitor

### Capture Enhancements (10-15 days)

44. Burst mode (rapid multiple captures)
45. Bracketing (exposure/focus stacking)
46. Time-lapse mode
47. Video recording (not just preview)
48. HDR merge for high contrast

### Image Processing (15-20 days)

49. Color correction profiles per camera
50. Distortion correction (lens calibration)
51. Focus stacking post-processing
52. Background removal automation
53. Measurement tools (calibrated scale)

### Workflow Automation (10-15 days)

54. Batch processing
55. Auto-naming from metadata
56. QR code scanning for specimen ID
57. RFID integration
58. Database integration (TaxonWorks, Specify)

### System Features (15-20 days)

59. Time synchronization via NTP
60. Cloud backup automation
61. Remote access via VPN
62. Multi-user support with permissions
63. AI-assisted specimen detection
64. Mobile app for monitoring
65. Web interface alternative
66. Foot pedal integration

---

## SUMMARY STATISTICS

**Total Items**: 66 distinct upgrades (was 70)

**By Priority**:
- P0 (Blocking): 6 items → 3-5 weeks
- P1 (High): 16 items → +4-5 weeks (7-10 weeks total) 
- P2 (Medium): 16 items → +5-6 weeks (12-16 weeks total)
- P3 (Future): 28 items → Variable timeline

**Items Removed**: 4 items (digital gain, white balance presets/fine gains, noise reduction, frame/video advanced controls)

**Effort by Category**:
- Camera Controls & Calibration: 5-6 days (was 5-7 days)
- GUI Improvements: 8-12 days
- System Integration: 4-5 days
- Code Quality: 3-4 days
- Documentation: 6-8 days
- Testing: 5-6 days
- Hardware: Physical modifications required

**Quick Wins** (can complete in 1 day or less):
- Audio feedback
- Progress indicators
- Keyboard shortcuts
- File organization
- Device naming
- Troubleshooting guide
- JPEG quality sync
- Requirements.txt fix
- ISO verification
- Exposure compensation
- Sharpness control

**Total Quick Wins**: 11 items in approximately 5-7 days (was 14 items)

---

## ESSENTIAL CAMERA CONTROLS RETAINED

After simplification, the system will have these camera controls:

**Exposure**:
- Shutter speed (100µs - 10s)
- ISO/Analogue gain (100-6400)
- Exposure compensation (±8.0 EV)

**Color**:
- Auto white balance
- Manual color temperature (2000K-10000K)

**Image Quality**:
- Brightness (existing)
- Contrast (existing)
- Saturation (existing)
- Sharpness (0.0-4.0)

**Preview**:
- FPS options (5/10/15/30 FPS)

These controls provide essential manual override for scientific imaging without the complexity of advanced camera features.

---

## RECOMMENDED IMPLEMENTATION ORDER

### Week 1-2: Quick Wins + WYSIWYG
- All 11 quick wins (5-7 days)
- Start WYSIWYG synchronization (3-5 days overlap)

### Week 3-4: Core Stability
- Complete WYSIWYG
- Telemetry logging
- Camera capture reliability
- System lag reduction

### Week 5-6: Camera Controls
- Camera calibration system
- Shutter speed, ISO, white balance
- Sharpness, exposure compensation
- All exposure controls

### Week 7-8: GUI Polish
- Interactive crop
- Status indicators
- Enhanced preview size
- Resolution switching

### Week 9-10: Integration & Testing
- Feature toggles
- Hardware controls connection
- Integration tests
- Load testing

### Week 11-12: Documentation
- User manual
- Technical documentation
- Final testing
- Production deployment prep

**Result**: System ready for production use in 12 weeks (3 months)

---

## VERIFICATION REQUIREMENTS

Before marking any feature complete:

**Code Quality**:
- No syntax errors
- No duplicate function definitions
- Correct port assignments
- No broken imports
- Proper error handling

**Functionality**:
- Works on development machine
- Works on single Raspberry Pi
- Works on all 8 Raspberry Pis
- Settings persist across restarts
- Error recovery functional

**WYSIWYG Compliance**:
- Preview aspect ratio matches sensor
- Crop coordinates scale correctly
- All transforms apply identically
- Color accuracy maintained

**Performance**:
- Response time acceptable
- No memory leaks
- Stable over 4+ hour sessions
- Handles 100+ consecutive captures

**Documentation**:
- Feature documented in manual
- Troubleshooting section updated
- Code commented
- API documented (if applicable)
