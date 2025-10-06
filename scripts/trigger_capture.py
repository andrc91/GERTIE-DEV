#!/usr/bin/env python3
"""
Trigger Capture Script
Captures a still image using the same pipeline as still_capture.py
"""

import argparse
import sys
import os
import cv2
import numpy as np
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from picamera2 import Picamera2
    from shared.transforms import apply_unified_transforms_for_still, get_device_name_from_ip, load_device_settings
except ImportError as e:
    print(f"Error: Missing dependencies: {e}")
    print("This script requires picamera2 and the shared transforms module")
    sys.exit(1)

def build_camera_controls(settings):
    """Build Picamera2 controls from settings"""
    controls = {"FrameRate": settings.get('fps', 30)}
    
    # Basic image controls
    gui_brightness = settings.get('brightness', 0)
    if gui_brightness != 0:
        if -50 <= gui_brightness <= 50:
            brightness_val = gui_brightness / 50.0
            controls["Brightness"] = brightness_val
    
    if settings.get('contrast', 50) != 50:
        controls["Contrast"] = settings['contrast'] / 50.0
        
    if settings.get('saturation', 50) != 50:
        controls["Saturation"] = settings['saturation'] / 50.0
    
    if settings.get('iso', 100) != 100:
        controls["AnalogueGain"] = settings['iso'] / 100.0
    
    return controls

def trigger_capture(output_path):
    """Trigger a still capture using the same pipeline as still_capture.py"""
    try:
        device_name = get_device_name_from_ip()
        settings = load_device_settings(device_name)
        
        print(f"Capturing still image for device: {device_name}")
        
        # Initialize camera for high resolution still capture
        picam2 = Picamera2()
        
        # Configure for maximum resolution still
        still_config = picam2.create_still_configuration(
            main={"size": (4608, 2592)},
            controls=build_camera_controls(settings)
        )
        picam2.configure(still_config)
        picam2.start()
        
        # Let camera settle
        time.sleep(1)
        
        # Capture full resolution image
        image_array = picam2.capture_array()
        
        # Apply transforms using the still capture pipeline
        processed_image = apply_unified_transforms_for_still(image_array, device_name)
        
        # Save processed image
        success = cv2.imwrite(output_path, processed_image)
        
        picam2.stop()
        picam2.close()
        
        if success and os.path.exists(output_path):
            print(f"Still image saved: {output_path}")
            return True
        else:
            print("Failed to save still image")
            return False
            
    except Exception as e:
        print(f"Error capturing still image: {e}")
        try:
            if 'picam2' in locals():
                picam2.stop()
                picam2.close()
        except:
            pass
        return False

def main():
    parser = argparse.ArgumentParser(description="Trigger still capture")
    parser.add_argument("--out", required=True, help="Output file path")
    args = parser.parse_args()
    
    success = trigger_capture(args.out)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
