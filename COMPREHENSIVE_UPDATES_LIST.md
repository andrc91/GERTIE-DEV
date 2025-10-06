# GERTIE Camera System - Comprehensive Fixes & Updates List

**Complete inventory of all desired improvements and fixes**  
**Source:** GitHub Issues, User Feedback, System Documentation  
**Date:** October 6, 2025

---

## 🔴 CRITICAL PRIORITY - Production Blockers

### 1. Lighting Control System
**Status:** Not Started  
**Effort:** 4-5 days  
**Impact:** 75% of users (3/4)

**Problem:**
- Under-label camera images too dark to read specimen labels
- Glare and shadow issues on other cameras
- Direct user quote: "The camera capturing data underneath the specimen needs lighting, as currently images are very dark and not readable"

**Solution Required:**
- Hardware interface for LED control (PWM or relay-based)
- Network protocol for lighting commands
- GUI panel with per-camera intensity sliders (0-100%)
- Master brightness control for all lights
- Settings persistence
- Preset save/load system

**Acceptance Criteria:**
- Each camera has individual brightness control
- Under-label images clearly readable
- Settings persist across restarts
- No glare in dorsal images
- Response time <500ms

---

### 2. System Performance Optimization
**Status:** Partially Implemented  
**Effort:** 3-4 days  
**Impact:** 100% of users

**Problem:**
- 5-10 second lag between command and response
- Mouse cursor lag during operations
- Inconsistent frame rates (<10 FPS)
- Prevents real-time focus verification
- Makes system nearly unusable for production

**Current Metrics:**
- Response time: 5-10 seconds
- Frame rate: Variable, often <10 FPS
- Capture completion: 3-5 seconds

**Target Metrics:**
- Response time: <1 second (stretch: <500ms)
- Frame rate: 15-30 FPS consistent
- Capture completion: <2 seconds
- No cursor lag

**Solutions Required:**
- Implement aggressive frame skipping
- Reduce preview resolution option (640x480 → 320x240)
- Optimize network packet handling
- Add operation queuing with visual feedback
- Hardware acceleration for video (if possible)
- Memory pool for image buffers
- Async/await for all operations
- Threading optimization

**Test Requirements:**
- 2-hour continuous operation test
- Rapid capture sequences
- All 8 cameras active simultaneously
- 1000+ images in gallery without slowdown

---

### 3. Camera Stability & Reliability
**Status:** Testing  
**Effort:** 3-4 days  
**Impact:** High - System crashes

**Problems:**
- Lateral camera freezes during grouped capture
- Rep 8 camera shuts off after single image
- Requires multiple reboots
- Complete system freezes (13:45 incident documented)
- Issues often occur at session start

**Solutions Required:**
- Implement camera watchdog with auto-restart
- Add initialization retry logic
- Stagger camera startup to reduce load
- Implement health check before every capture
- Add manual camera reset button in GUI
- Better error reporting and logging

**Investigation Needed:**
- Hardware diagnostic on Rep 8
- Network traffic analysis during freeze
- Power supply verification
- USB bandwidth analysis
- Temperature monitoring

**Acceptance Criteria:**
- Zero crashes in 8-hour session
- Successful grouped capture 100 times consecutively
- Automatic recovery from disconnection
- Clear error messages when issues occur
- All cameras initialize reliably on first attempt

**Test Protocol:**
- Cold start test (10 iterations)
- Continuous capture test (4 hours)
- Rapid fire capture test (100 captures in 10 minutes)
- Network disruption recovery test
- Power cycle recovery test

---

## 🟡 HIGH PRIORITY - Significant User Experience Impact

### 4. Visual Status Indicators
**Status:** Not Started  
**Effort:** 2-3 days  
**Impact:** 100% of users - reduces confusion

**Problem:**
- Users confused during lag periods
- No way to know if cameras are responsive
- Backend infrastructure exists but no GUI display

**Solution Required:**
- Color-coded status dots per camera:
  - 🟢 GREEN: Online and responsive
  - 🟡 YELLOW: Idle, no recent activity
  - 🔴 RED: Offline or not responding
  - 🔵 BLUE: Actively capturing
- Small colored dot in corner of each camera frame
- Tooltip with: Last heartbeat, IP address, Capture count
- Pulsing animation during capture
- Master status bar showing overall system health

**Acceptance Criteria:**
- Status updates within 1 second of state change
- All 8 cameras show individual status
- Master status bar shows system overview
- Status persists through capture operations
- Color-blind friendly indicators

---

### 5. Audio Capture Feedback ⚡ QUICK WIN
**Status:** Not Started  
**Effort:** <1 day  
**Impact:** 75% of users (3/4 requested)

**Problem:**
- Audio file exists (master/shutter.wav) but not triggered
- Users compare to ALICE system's "six clicks" confirmation
- No auditory feedback for capture confirmation

**Solution Required:**
- Trigger existing shutter.wav on capture
- Volume control in settings (0-100%)
- Enable/disable toggle
- Optional: Different sounds for different events

**Implementation:**
```python
import pygame
pygame.mixer.init()
shutter_sound = pygame.mixer.Sound("master/shutter.wav")
```

**Acceptance Criteria:**
- Sound plays within 100ms of capture
- Volume adjustable
- Setting persists across sessions
- No audio delays or glitches
- Works with all capture modes

---

### 6. Metadata Tagging GUI Panel
**Status:** Not Started  
**Effort:** 3-4 days  
**Impact:** Medium - Data organization/tracking

**Problem:**
- Backend infrastructure exists (biometric_logger.py)
- No GUI for entering metadata
- Users need to track specimen information

**Solution Required:**
- Collapsible panel below camera grid
- Quick-entry form with tab navigation
- Fields:
  - Specimen ID (auto-increment option)
  - Barcode
  - Angle/view
  - Custom notes
- Barcode scanner integration ready
- Template system for common entries

**Acceptance Criteria:**
- All metadata saved with images
- Quick entry without mouse (keyboard shortcuts)
- Validation for required fields
- Export to CSV functionality
- Search/filter by metadata

---

## 🟢 MEDIUM PRIORITY - Convenience & Polish Features

### 7. Keyboard Shortcuts
**Status:** Not Started  
**Effort:** 1 day  
**Impact:** High productivity improvement

**Required Shortcuts:**
- `Space`: Capture all cameras
- `1-8`: Select camera 1-8
- `S`: Start/stop streaming
- `C`: Capture selected camera
- `F`: Toggle fullscreen
- `+/-`: Zoom in/out preview
- `Ctrl+S`: Save settings
- `Esc`: Close dialogs

---

### 8. Progress Indicators
**Status:** Not Started  
**Effort:** 1 day  
**Impact:** Reduces confusion

**Solution Required:**
- Progress bars for multi-capture operations
- Visual feedback for all long-running operations
- Time remaining estimates
- Cancel button for long operations

---

### 9. Enhanced Preview Features
**Status:** Not Started  
**Effort:** 1-2 days  
**Impact:** Better image verification

**Features:**
- Increase preview size option (current too small)
- Zoom functionality (2x, 4x)
- Focus peaking overlay
- Histogram display
- Grid overlay option

---

### 10. Gallery Panel
**Status:** Not Started  
**Effort:** 2-3 days  
**Impact:** Workflow improvement

**Features:**
- Recent captures viewer (thumbnail grid)
- Image metadata display
- Quick delete/export
- Side-by-side comparison
- Filter by camera/date

---

### 11. Enhanced File Organization
**Status:** Needs Improvement  
**Effort:** 1 day  
**Impact:** Medium

**Problems:**
- Current naming scheme not intuitive
- Need better folder structure

**Solution:**
- Configurable naming patterns
- Auto-organize by date/specimen/camera
- Batch rename functionality

---

### 12. Settings Profiles/Presets
**Status:** Partially Implemented  
**Effort:** 2 days  
**Impact:** Workflow efficiency

**Features:**
- Save complete system configuration as preset
- Quick-switch between presets
- Export/import presets
- Preset templates for common scenarios

---

## 🔧 HARDWARE MODIFICATIONS REQUIRED

### H1. Dome Height Adjustment
**Priority:** URGENT  
**Impact:** 4/4 users affected  
**Modification:** Raise dome by 2-3 inches  
**Reason:** Forceps clearance - cannot manipulate specimens

---

### H2. Platform Height Ergonomics
**Priority:** URGENT  
**Impact:** 2/4 users report back pain  
**Modification:** Reduce platform to 50% current height  
**Reason:** Too high, causes strain during extended use

---

### H3. Lateral Camera Background
**Priority:** HIGH  
**Impact:** Privacy + professionalism  
**Modification:** Retractable backdrop or curtain  
**Reason:** Background shows workspace/people

---

## 📚 DOCUMENTATION IMPROVEMENTS

### D1. User Manual
**Effort:** 3-4 days  
**Required:**
- Step-by-step setup guide
- Operation procedures
- Troubleshooting section
- FAQ
- Keyboard shortcut reference card

---

### D2. Technical Documentation
**Effort:** 2-3 days  
**Required:**
- API documentation
- Network protocol specification
- Architecture diagrams
- Development setup guide

---

### D3. Troubleshooting Guide
**Effort:** 1 day  
**Required:**
- Common issues and solutions
- Diagnostic procedures
- Log file locations
- Support contact information

---

## 🧪 TESTING INFRASTRUCTURE IMPROVEMENTS

### T1. Automated Integration Tests
**Effort:** 3-4 days  
**Required:**
- End-to-end capture workflow tests
- Multi-camera simultaneous operation tests
- Network disruption recovery tests
- Performance regression tests

---

### T2. Load Testing
**Effort:** 2 days  
**Required:**
- Long-duration stability tests
- High-frequency capture tests
- Memory leak detection
- Network bandwidth testing

---

### T3. Hardware Test Rig
**Effort:** Variable  
**Required:**
- Automated camera testing setup
- Benchmark suite
- Performance monitoring

---

## 🎯 FUTURE ENHANCEMENTS (Lower Priority)

### F1. FPS Selection
**Effort:** 1-2 days  
**Feature:** Allow user to select preview FPS (15/30/60)

---

### F2. Shutter Speed Control
**Effort:** 1 day  
**Feature:** Fine-tune exposure for different specimens

---

### F3. JPEG Quality Control
**Effort:** 1 day  
**Feature:** Adjust compression level (storage vs quality)

---

### F4. Grid Overlay
**Effort:** 1 day  
**Feature:** Alignment grid on preview

---

### F5. Biometric Logging
**Effort:** 3-4 days  
**Feature:** Track session metrics (captures/hour, etc.)

---

### F6. Time Sync to Replicas
**Effort:** 1-2 days  
**Feature:** Ensure all timestamps synchronized

---

### F7. Capture All Enhancement
**Effort:** 2 days  
**Feature:** Sequential vs simultaneous capture options

---

### F8. Advanced Color Correction
**Effort:** 3-4 days  
**Feature:** White balance calibration, color profiles

---

### F9. Remote Access
**Effort:** 4-5 days  
**Feature:** Web interface for remote monitoring/control

---

### F10. Multi-User Support
**Effort:** 5-7 days  
**Feature:** User accounts, permissions, session tracking

---

## 📊 SUMMARY STATISTICS

### By Priority
- **CRITICAL:** 3 items (10-13 days total)
- **HIGH:** 3 items (6-8 days total)
- **MEDIUM:** 6 items (9-13 days total)
- **HARDWARE:** 3 items
- **DOCUMENTATION:** 3 items (6-8 days total)
- **TESTING:** 3 items (7-10 days total)
- **FUTURE:** 10 items (22-36 days total)

### By Impact
- **100% of users affected:** 2 items
- **75% of users affected:** 2 items
- **50% of users affected:** 1 item
- **High workflow impact:** 8 items

### Total Estimated Effort
- **Minimum to Production:** 10-13 days (Critical only)
- **Full High Priority:** 16-21 days
- **All Medium Priority:** 25-34 days
- **Complete System:** 60-88 days

### Quick Wins (<2 days each)
1. Audio Feedback (<1 day)
2. Keyboard Shortcuts (1 day)
3. File Organization (1 day)
4. Progress Bars (1 day)
5. Troubleshooting Guide (1 day)

---

## 🎯 RECOMMENDED IMPLEMENTATION ORDER

### Phase 1: Production Blockers (Weeks 1-2)
1. Lighting Control System
2. Performance Optimization
3. Camera Stability

### Phase 2: User Experience (Weeks 3-4)
4. Audio Feedback ⚡
5. Visual Status Indicators
6. Keyboard Shortcuts
7. Progress Indicators

### Phase 3: Polish (Weeks 5-6)
8. Metadata Tagging
9. Enhanced Preview
10. Gallery Panel
11. Settings Profiles

### Phase 4: Documentation & Testing (Weeks 7-8)
12. User Manual
13. Technical Docs
14. Automated Tests
15. Load Testing

### Phase 5: Future Enhancements (Ongoing)
16. Advanced features as needed

---

**Total Items:** 40+ fixes/updates/enhancements identified  
**Critical Path:** 10-13 days to production-ready  
**Full Implementation:** 8+ weeks for complete system

---

*Document compiled from:*
- *GITHUB_ISSUES_TO_CREATE.md*
- *User feedback surveys*
- *System documentation*
- *Testing reports*
- *Developer notes*

*Last Updated: October 6, 2025*
