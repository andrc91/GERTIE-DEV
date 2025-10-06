#!/usr/bin/env python3
"""
Capture Preview Frame Script
Captures a frame from the video preview stream using the same transforms as video
"""

import argparse
import sys
import os
import cv2
import numpy as np
from PIL import Image

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from picamera2 import Picamera2
    from shared.transforms import apply_unified_transforms, get_device_name_from_ip
except ImportError as e:
    print(f"Error: Missing dependencies: {e}")
    print("This script requires picamera2 and the shared transforms module")
    sys.exit(1)

def capture_preview_frame(output_path):
    """Capture a preview frame using the same pipeline as video stream"""
    try:
        device_name = get_device_name_from_ip()
        print(f"Capturing preview frame for device: {device_name}")
        
        # Initialize camera for preview (lower resolution like video stream)
        picam2 = Picamera2()
        
        # Use preview configuration similar to video stream
        preview_config = picam2.create_preview_configuration(
            main={"size": (640, 480), "format": "RGB888"}
        )
        picam2.configure(preview_config)
        picam2.start()
        
        # Let camera settle
        import time
        time.sleep(1)
        
        # Capture frame
        frame = picam2.capture_array()
        
        # Apply the same transforms as video stream
        transformed_frame = apply_unified_transforms(frame, device_name)
        
        # Save as PNG for lossless comparison
        image = Image.fromarray(transformed_frame)
        image.save(output_path)
        
        picam2.stop()
        picam2.close()
        
        print(f"Preview frame saved: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error capturing preview frame: {e}")
        try:
            if 'picam2' in locals():
                picam2.stop()
                picam2.close()
        except:
            pass
        return False

def main():
    parser = argparse.ArgumentParser(description="Capture preview frame")
    parser.add_argument("--out", required=True, help="Output file path")
    args = parser.parse_args()
    
    success = capture_preview_frame(args.out)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
