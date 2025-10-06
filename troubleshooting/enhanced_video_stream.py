#!/usr/bin/env python3
"""
ENHANCED Video Stream Script for rep5, rep6, rep7 - DEBUGGING VERSION
Adds extensive logging and error handling to diagnose streaming issues
"""

import os
import io
import json
import time
import socket
import threading
import logging
import datetime
import cv2
import numpy as np

# Configure more detailed logging
logging.basicConfig(
    level=logging.INFO,  # Changed to INFO for more detailed logs
    format='%(asctime)s - %(levelname)s - [%(threadName)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/tmp/video_stream_debug.log', mode='a')
    ]
)

logger = logging.getLogger(__name__)

try:
    from picamera2 import Picamera2
    logger.info("✅ Picamera2 imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import Picamera2: {e}")
    exit(1)

# Import from config with robust fallback
try:
    import sys
    sys.path.insert(0, "/home/andrc1/camera_system_integrated_final")
    from shared.config import MASTER_IP, VIDEO_PORT, get_slave_ports, HEARTBEAT_PORT
    logger.info("✅ Successfully imported from shared.config")
except ImportError as e:
    logger.warning(f"❌ Failed to import shared.config: {e}, using fallback")
    MASTER_IP = "192.168.0.200"
    VIDEO_PORT = 5002
    HEARTBEAT_PORT = 5003
    
    def get_slave_ports(ip: str):
        if ip == "127.0.0.1" or ip.startswith("127."):
            return {"control": 5011, "video": 5012, "video_control": 5014, "still": 6010, "heartbeat": 5013}
        else:
            return {"control": 5001, "video": 5002, "video_control": 5004, "still": 6000, "heartbeat": 5003}

# Global variables
streaming = False
streaming_lock = threading.Lock()
jpeg_quality = 80
camera_initialized = False
picam2 = None

def get_local_ip():
    """Get the local IP address"""
    try:
        # Connect to a dummy address to get local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        logger.info(f"Local IP detected: {local_ip}")
        return local_ip
    except Exception as e:
        logger.error(f"Failed to get local IP: {e}")
        return "127.0.0.1"

def initialize_camera():
    """Initialize camera with detailed error reporting"""
    global picam2, camera_initialized
    
    logger.info("🎥 Initializing camera...")
    
    try:
        # Check camera hardware first
        try:
            import subprocess
            result = subprocess.run(['vcgencmd', 'get_camera'], capture_output=True, text=True)
            logger.info(f"Camera hardware check: {result.stdout.strip()}")
        except Exception as e:
            logger.warning(f"Could not check camera hardware: {e}")
        
        # Check camera device files
        import os
        video_devices = [f for f in os.listdir('/dev') if f.startswith('video')]
        logger.info(f"Available video devices: {video_devices}")
        
        # Initialize Picamera2
        picam2 = Picamera2()
        logger.info("✅ Picamera2 object created")
        
        # Get camera info
        try:
            camera_info = picam2.camera_info
            logger.info(f"Camera info: {camera_info}")
        except Exception as e:
            logger.warning(f"Could not get camera info: {e}")
        
        # Configure camera
        video_config = picam2.create_video_configuration(
            main={"size": (640, 480), "format": "RGB888"},
            controls={"FrameRate": 30}
        )
        picam2.configure(video_config)
        logger.info("✅ Camera configured")
        
        # Start camera
        picam2.start()
        logger.info("✅ Camera started")
        
        # Let camera settle
        time.sleep(2.0)
        
        # Test frame capture
        test_frame = picam2.capture_array()
        logger.info(f"✅ Test frame captured: {test_frame.shape}")
        
        camera_initialized = True
        logger.info("🎥 Camera initialization complete!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Camera initialization failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False

def start_stream():
    """Enhanced video stream with detailed logging"""
    global streaming, jpeg_quality, picam2, camera_initialized
    
    logger.info("🚀 Starting video stream...")
    
    with streaming_lock:
        if streaming:
            logger.warning("Video stream already running")
            return
        streaming = True

    sock = None

    try:
        # Initialize camera if not already done
        if not camera_initialized:
            if not initialize_camera():
                logger.error("❌ Cannot start stream - camera initialization failed")
                with streaming_lock:
                    streaming = False
                return
        
        # Setup UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        logger.info("✅ Video socket created")
        
        logger.info(f"🎯 Streaming to {MASTER_IP}:{VIDEO_PORT}")
        
        # Test network connectivity
        try:
            test_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            test_sock.settimeout(1.0)
            test_sock.sendto(b"TEST", (MASTER_IP, VIDEO_PORT))
            test_sock.close()
            logger.info("✅ Network connectivity to master confirmed")
        except Exception as e:
            logger.warning(f"⚠️ Network test failed: {e}")
        
        # Main streaming loop
        frame_count = 0
        last_time = time.time()
        error_count = 0
        
        logger.info("🎬 Starting streaming loop...")
        
        while True:
            with streaming_lock:
                if not streaming:
                    logger.info("Stream stop requested, breaking loop")
                    break
            
            try:
                # Capture frame
                frame = picam2.capture_array()
                
                # Convert RGB to BGR for OpenCV
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                
                # Encode as JPEG
                encode_params = [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality]
                success, encoded = cv2.imencode(".jpg", frame, encode_params)
                
                if success:
                    frame_data = encoded.tobytes()
                    sock.sendto(frame_data, (MASTER_IP, VIDEO_PORT))
                    
                    frame_count += 1
                    error_count = 0  # Reset error count on success
                    
                    # Performance monitoring (every 150 frames = ~5 seconds at 30fps)
                    if frame_count % 150 == 0:
                        current_time = time.time()
                        actual_fps = 150 / (current_time - last_time)
                        logger.info(f"📊 Streaming: {actual_fps:.1f} fps, frame size: {len(frame_data)} bytes, total frames: {frame_count}")
                        last_time = current_time
                else:
                    logger.error("❌ Frame encoding failed")
                    error_count += 1
                
                # Frame rate control
                time.sleep(0.033)  # ~30 FPS
                
                # Exit if too many consecutive errors
                if error_count > 100:
                    logger.error("❌ Too many consecutive errors, stopping stream")
                    break
                
            except Exception as e:
                logger.error(f"❌ Error in streaming loop: {e}")
                error_count += 1
                if error_count > 50:
                    logger.error("❌ Too many errors, stopping stream")
                    break
                time.sleep(0.1)  # Brief pause on error
                
    except Exception as e:
        logger.error(f"❌ Critical error in video streaming: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        
    finally:
        # Cleanup
        if sock:
            try:
                sock.close()
                logger.info("✅ Video socket closed")
            except:
                pass
                
        with streaming_lock:
            streaming = False
        
        logger.info("🛑 Video stream stopped")

def stop_stream():
    """Stop video streaming"""
    global streaming
    
    logger.info("🛑 Video stream stop requested")
    
    with streaming_lock:
        if not streaming:
            logger.info("Video stream not running")
            return
        streaming = False

def handle_video_commands():
    """Handle video-specific commands with detailed logging"""
    global streaming, jpeg_quality
    
    logger.info("🎛️ Starting video command handler...")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        local_ip = get_local_ip()
        ports = get_slave_ports(local_ip)
        video_control_port = ports['video_control']
        
        sock.bind(("0.0.0.0", video_control_port))
        logger.info(f"✅ Video command handler listening on port {video_control_port}")
    except OSError as e:
        logger.error(f"❌ Failed to bind video command port: {e}")
        return

    while True:
        try:
            data, addr = sock.recvfrom(1024)
            command = data.decode().strip()
            logger.info(f"📨 Video command received: '{command}' from {addr[0]}")

            if command == "START_STREAM":
                logger.info("🎬 Processing START_STREAM command")
                if not streaming:
                    threading.Thread(target=start_stream, daemon=True, name="VideoStream").start()
                    logger.info("✅ Video stream thread started")
                else:
                    logger.info("ℹ️ Video stream already running")
                
            elif command == "STOP_STREAM":
                logger.info("🛑 Processing STOP_STREAM command")
                stop_stream()
                
            elif command == "RESTART_STREAM_WITH_SETTINGS":
                logger.info("🔄 Processing RESTART_STREAM_WITH_SETTINGS command")
                stop_stream()
                time.sleep(2.0)
                threading.Thread(target=start_stream, daemon=True, name="VideoStream").start()
                
            elif command.startswith("SET_QUALITY_"):
                try:
                    quality = int(command.split('_')[2])
                    if 20 <= quality <= 100:
                        jpeg_quality = quality
                        logger.info(f"🎚️ JPEG quality set to {quality}")
                    else:
                        logger.warning(f"⚠️ Invalid quality value: {quality}")
                except:
                    logger.error(f"❌ Invalid quality command: {command}")
            else:
                logger.warning(f"⚠️ Unknown command: {command}")
                    
        except Exception as e:
            logger.error(f"❌ Error handling video command: {e}")

def send_video_heartbeat():
    """Send heartbeat to master GUI with detailed logging"""
    logger.info("💓 Starting video heartbeat sender...")
    
    heartbeat_count = 0
    error_count = 0
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            logger.info(f"💓 Sending heartbeats to {MASTER_IP}:{HEARTBEAT_PORT}")
            
            while True:
                try:
                    sock.sendto(b"HEARTBEAT", (MASTER_IP, HEARTBEAT_PORT))
                    heartbeat_count += 1
                    error_count = 0
                    
                    # Log every 60 heartbeats (1 minute)
                    if heartbeat_count % 60 == 0:
                        logger.info(f"💓 Heartbeat count: {heartbeat_count}")
                    
                    time.sleep(1.0)
                except Exception as e:
                    error_count += 1
                    if error_count % 10 == 1:  # Log every 10th error
                        logger.error(f"💔 Heartbeat send error #{error_count}: {e}")
                    time.sleep(1.0)
    except Exception as e:
        logger.error(f"❌ Heartbeat socket error: {e}")

def main():
    """Main function with enhanced initialization"""
    logger.info("🚀 Starting enhanced video stream service...")
    logger.info(f"Master IP: {MASTER_IP}")
    logger.info(f"Video Port: {VIDEO_PORT}")
    logger.info(f"Heartbeat Port: {HEARTBEAT_PORT}")
    
    # Get local configuration
    local_ip = get_local_ip()
    ports = get_slave_ports(local_ip)
    logger.info(f"Local ports: {ports}")
    
    try:
        # Initialize camera early
        if initialize_camera():
            logger.info("✅ Camera pre-initialization successful")
        else:
            logger.error("❌ Camera pre-initialization failed - service will start but streaming will fail")
        
        # Start heartbeat and video command handler
        heartbeat_thread = threading.Thread(target=send_video_heartbeat, daemon=True, name="Heartbeat")
        command_thread = threading.Thread(target=handle_video_commands, daemon=True, name="Commands")
        
        heartbeat_thread.start()
        command_thread.start()
        
        logger.info("✅ All threads started successfully")
        
        # Keep main thread alive and monitor
        while True:
            time.sleep(30)  # Check every 30 seconds
            
            # Log status
            with streaming_lock:
                stream_status = "STREAMING" if streaming else "IDLE"
            
            logger.info(f"📊 Service status: {stream_status}, Camera: {'OK' if camera_initialized else 'FAILED'}")
            
    except KeyboardInterrupt:
        logger.info("🛑 Service stopped by user")
        stop_stream()
    except Exception as e:
        logger.error(f"❌ Error in main: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main()
