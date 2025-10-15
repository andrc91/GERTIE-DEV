# ARCHITECTURAL FIXES REQUIRED - Both Issues Need Structural Changes

## User Feedback After 7b25c2c Deployment
❌ **Issue #1**: "rep8 video preview streaming does not return to live streaming after capture, still freezes"
❌ **Issue #2**: "gui still laggy at all points"

## Root Cause Analysis

### Rep8 Freeze - Thread Synchronization Flaw
**Problem**: Sleeping doesn't guarantee thread cleanup
**Current broken code**:
```python
# capture_local_still():
streaming = False  # Just set flag
time.sleep(5.0)    # Hope thread stops...
picam2 = Picamera2()  # May conflict with unclosed instance!
```

**Why it fails**: No actual synchronization - streaming thread may still have active Picamera2

**Architectural fix needed**:
```python
# Module level:
picam2_instance = None
streaming_stopped_event = threading.Event()

# In capture:
streaming = False
streaming_stopped_event.wait(timeout=10)  # Wait for actual stop signal
# Now safe to create new instance

# In streaming thread cleanup:
picam2.stop(); picam2.close()
streaming_stopped_event.set()  # Signal we're actually stopped
```

### GUI Lag - Event Queue Saturation
**Problem**: after_idle() called for EVERY frame, even if not displayed
**Current broken architecture**:
```python
# network_manager.video_receiver():
for every_frame:  # 240 times/sec
    gui.root.after_idle(update_video_display_safe, ...)  # Queue even if not shown!

# update_video_display_safe():
if time_since_last < min_interval:
    return  # Too soon, but already queued!
```

**Why it fails**: Tkinter event loop processes all 240 queued calls/sec, even if 90% just return

**Architectural fix needed**:
```python
# Module level per camera:
update_pending = {}  # Track if update already queued

# In video receiver:
if not update_pending.get(ip, False):
    update_pending[ip] = True
    gui.root.after_idle(update_video_display_safe, ...)
# Else: Skip queuing entirely!

# In update_video_display_safe():
try:
    # Do update
finally:
    update_pending[ip] = False  # Allow next update to queue
```

## Implementation Plan

### Fix #1: Rep8 - Proper Thread Synchronization
**Files**: `local_camera_slave.py`
**Changes**:
1. Add module-level `threading.Event()` for stop signal  
2. Add module-level `picam2_instance` reference
3. In streaming thread: signal event on cleanup
4. In capture: wait for event before creating new instance
5. Properly manage single Picamera2 instance

### Fix #2: GUI - Gate Event Queue Calls
**Files**: `master/camera_gui/core/network_manager.py`
**Changes**:
1. Add `self.update_pending = {}` dict in __init__
2. In `process_video_frame`: Check pending flag before after_idle()
3. In `update_video_display_safe`: Clear pending flag in finally block
4. This prevents queue saturation entirely

## Expected Results
- **Rep8**: Proper synchronization = no Picamera2 conflicts = video resumes reliably
- **GUI**: 90% reduction in Tkinter event queue load = smooth responsiveness

## Why These Will Work
1. **Rep8**: Threading.Event provides actual synchronization, not hope
2. **GUI**: Prevents queue saturation at source, not just inside handler

Ready to implement these architectural fixes?
