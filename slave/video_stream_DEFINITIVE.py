#!/usr/bin/env python3
"""
DEFINITIVE FIX - Video Stream for rep1-7
Fixes: 1) RGB->BGR color conversion, 2) Brightness preservation on flip
"""

import os
import json
import time
import socket
import threading
import logging
import cv2
import numpy as np
from picamera2 import Picamera2

# Configure logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

# Import configuration
try:
    import sys
    sys.path.insert(0, "/home/andrc1/camera_system_integrated_final")
    from shared.config import MASTER_IP, VIDEO_PORT, get_slave_ports, HEARTBEAT_PORT
except ImportError:
    MASTER_IP = "192.168.0.200"
    VIDEO_PORT = 5002
    HEARTBEAT_PORT = 5003
    def get_slave_ports(ip):
        return {"control": 5001, "video": 5002, "video_control": 5004, "still": 6000, "heartbeat": 5003}

# Global variables
streaming = False
streaming_lock = threading.Lock()
jpeg_quality = 80

def apply_simple_transforms(rgb_frame):
    """
    DEFINITIVE: Apply transforms with guaranteed RGB->BGR conversion
    Input: RGB frame from Picamera2
    Output: BGR frame for OpenCV/JPEG encoding
    """
    try:
        # Step 1: ALWAYS convert RGB to BGR first
        bgr_frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)
        
        # Step 2: Load settings and apply transforms
        from shared.transforms import load_device_settings, get_device_name_from_ip
        device_name = get_device_name_from_ip()
        settings = load_device_settings(device_name)
        
        # Step 3: Apply frame transforms (not camera controls)
        if settings.get('flip_horizontal', False):
            bgr_frame = cv2.flip(bgr_frame, 1)
        if settings.get('flip_vertical', False):
            bgr_frame = cv2.flip(bgr_frame, 0)
        if settings.get('rotation', 0) == 90:
            bgr_frame = cv2.rotate(bgr_frame, cv2.ROTATE_90_CLOCKWISE)
        elif settings.get('rotation', 0) == 180:
            bgr_frame = cv2.rotate(bgr_frame, cv2.ROTATE_180)
        elif settings.get('rotation', 0) == 270:
            bgr_frame = cv2.rotate(bgr_frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        if settings.get('grayscale', False):
            gray = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2GRAY)
            bgr_frame = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
            
        return bgr_frame
        
    except Exception as e:
        logging.error(f"Transform error: {e}")
        # Fallback: at minimum convert RGB to BGR
        return cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)

def build_camera_controls():
    """Build camera controls (hardware only, no transforms)"""
    try:
        from shared.transforms import load_device_settings, get_device_name_from_ip
        device_name = get_device_name_from_ip()
        settings = load_device_settings(device_name)
        
        controls = {"FrameRate": settings.get('fps', 30)}
        
        # Only camera hardware controls
        if settings.get('brightness', 50) != 50:
            controls["Brightness"] = (settings['brightness'] - 50) / 50.0
        if settings.get('contrast', 50) != 50:
            controls["Contrast"] = settings['contrast'] / 50.0
        if settings.get('saturation', 50) != 50:
            controls["Saturation"] = settings['saturation'] / 50.0
        if settings.get('iso', 100) != 100:
            controls["AnalogueGain"] = settings['iso'] / 100.0
            
        return controls
    except:
        return {"FrameRate": 30}

def start_stream():
    """Start video streaming with definitive fixes"""
    global streaming, jpeg_quality
    
    with streaming_lock:
        if streaming:
            return
        streaming = True

    picam2 = None
    sock = None

    try:
        # Initialize camera
        picam2 = Picamera2()
        
        # Configure with camera controls only
        video_config = picam2.create_video_configuration(
            main={"size": (640, 480), "format": "RGB888"},
            controls=build_camera_controls()
        )
        picam2.configure(video_config)
        picam2.start()
        time.sleep(2.0)
        
        # Setup UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        logging.info("DEFINITIVE: Video streaming started with RGB->BGR conversion")
        
        while True:
            with streaming_lock:
                if not streaming:
                    break
            
            try:
                # Capture RGB frame
                rgb_frame = picam2.capture_array()
                
                # DEFINITIVE: Apply transforms with guaranteed color conversion
                bgr_frame = apply_simple_transforms(rgb_frame)
                
                # Encode and send
                success, encoded = cv2.imencode(".jpg", bgr_frame, [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality])
                if success:
                    sock.sendto(encoded.tobytes(), (MASTER_IP, VIDEO_PORT))
                
                time.sleep(0.1)  # 10 FPS
                
            except Exception as e:
                logging.error(f"Video loop error: {e}")
                break
                
    except Exception as e:
        logging.error(f"Video streaming error: {e}")
        
    finally:
        if picam2:
            try:
                picam2.stop()
                picam2.close()
            except:
                pass
        if sock:
            try:
                sock.close()
            except:
                pass
        with streaming_lock:
            streaming = False

def stop_stream():
    """Stop video streaming"""
    global streaming
    with streaming_lock:
        streaming = False

def handle_video_commands():
    """Handle video commands with brightness-safe processing"""
    global streaming, jpeg_quality
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        local_ip = socket.gethostbyname(socket.gethostname())
        ports = get_slave_ports(local_ip)
        sock.bind(("0.0.0.0", ports['video_control']))
    except:
        return

    while True:
        try:
            data, addr = sock.recvfrom(1024)
            command = data.decode().strip()

            if command == "START_STREAM":
                if not streaming:
                    threading.Thread(target=start_stream, daemon=True).start()
            elif command == "STOP_STREAM":
                stop_stream()
            elif command.startswith("SET_ALL_SETTINGS_"):
                handle_settings_safe(command)
            elif command.startswith("SET_QUALITY_"):
                try:
                    quality = int(command.split('_')[2])
                    if 20 <= quality <= 100:
                        jpeg_quality = quality
                except:
                    pass
                    
        except Exception as e:
            logging.error(f"Command handler error: {e}")

def handle_settings_safe(command):
    """Handle settings with brightness preservation"""
    try:
        # Parse settings
        json_part = command[17:]
        new_settings = json.loads(json_part)
        
        from shared.transforms import save_device_settings, load_device_settings, get_device_name_from_ip
        device_name = get_device_name_from_ip()
        current_settings = load_device_settings(device_name)
        
        # DEFINITIVE FIX: Only restart if camera controls change
        camera_controls_changed = False
        transform_only_changes = False
        
        for key, value in new_settings.items():
            if key in current_settings:
                old_val = current_settings[key]
                current_settings[key] = value
                
                # Categorize changes
                if key in ['brightness', 'contrast', 'saturation', 'iso', 'fps']:
                    if old_val != value:
                        camera_controls_changed = True
                        logging.info(f"CAMERA CONTROL CHANGED: {key} {old_val}->{value}")
                elif key in ['flip_horizontal', 'flip_vertical', 'rotation', 'grayscale']:
                    if old_val != value:
                        transform_only_changes = True
                        logging.info(f"TRANSFORM CHANGED: {key} {old_val}->{value}")
        
        # Save settings
        save_device_settings(device_name, current_settings)
        
        # DEFINITIVE: Only restart camera if hardware controls changed
        if camera_controls_changed:
            logging.info("RESTARTING: Camera controls changed")
            stop_stream()
            time.sleep(2)
            threading.Thread(target=start_stream, daemon=True).start()
        elif transform_only_changes:
            logging.info("NO RESTART: Only transforms changed - brightness preserved")
        
    except Exception as e:
        logging.error(f"Settings error: {e}")

def send_heartbeat():
    """Send heartbeat"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            while True:
                try:
                    sock.sendto(b"HEARTBEAT", (MASTER_IP, HEARTBEAT_PORT))
                    time.sleep(1.0)
                except:
                    time.sleep(1.0)
    except:
        pass

def main():
    """Main function"""
    logging.info("Starting DEFINITIVE video stream service...")
    
    try:
        threading.Thread(target=send_heartbeat, daemon=True).start()
        threading.Thread(target=handle_video_commands, daemon=True).start()
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        stop_stream()

if __name__ == "__main__":
    main()
