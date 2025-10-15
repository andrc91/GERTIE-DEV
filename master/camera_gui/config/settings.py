"""
Centralized configuration management - Integrated with shared config
"""

import os
import json
import logging
from pathlib import Path

# Try to import from shared config first, fallback to local config
try:
    import sys
    project_root = Path(__file__).resolve().parents[3]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from shared.config import MASTER_IP, CONTROL_PORT, VIDEO_PORT, STILL_PORT, HEARTBEAT_PORT, SLAVES, IMAGE_DIR
    print("Using Shared Configuration")
    USING_SHARED_CONFIG = True
except Exception as e:
    print("⚠️ Shared config not found, using local configuration ({e})")
    USING_SHARED_CONFIG = False

# Base configuration
class Config:
    # Network settings - Use shared config if available
    if USING_SHARED_CONFIG:
        MASTER_IP = MASTER_IP
        CONTROL_PORT = CONTROL_PORT 
        VIDEO_PORT = VIDEO_PORT
        STILL_PORT = STILL_PORT
        HEARTBEAT_PORT = HEARTBEAT_PORT
        SLAVES = SLAVES
        IMAGE_DIR = IMAGE_DIR
    else:
        # Fallback configuration
        MASTER_IP = "192.168.0.200"
        CONTROL_PORT = 5001
        VIDEO_PORT = 5002
        STILL_PORT = 6000
        HEARTBEAT_PORT = 5003
        SLAVES = {
            "rep1": {"ip": "192.168.0.201"},
            "rep2": {"ip": "192.168.0.202"},
            "rep3": {"ip": "192.168.0.203"},
            "rep4": {"ip": "192.168.0.204"},
            "rep5": {"ip": "192.168.0.205"},
            "rep6": {"ip": "192.168.0.206"},
            "rep7": {"ip": "192.168.0.207"},
            "rep8": {"ip": "127.0.0.1"},
        }
        IMAGE_DIR = "../captured_images"
    
    # GUI settings
    WINDOW_SIZE = "1600x900"
    NUM_ROWS = 2
    NUM_COLS = 4
    GALLERY_WIDTH = 300
    
    # Performance settings
    PERFORMANCE_FLAGS = {
        'FAST_VIDEO_UPDATES': True,
        'ASYNC_STILL_CAPTURE': True,
        'OPTIMIZED_GALLERY': True,
        'REDUCED_LOGGING': True,
        'FRAME_SKIP': True,
    }
    
    # Feature flags
    FEATURE_FLAGS = {
        'ENHANCED_CAMERA_CONTROLS': True,
        'AUTO_START_STREAMS': False,  # DISABLED to prevent auto-commands
        'GALLERY_LEFT_PANEL': True,
        'SYSTEM_MENU': True,
        'DEVICE_NAMING': True,
    }
    
    # Directories - Use absolute paths for better integration
    CONFIG_DIR = "../config_files"

# Global instances
config = Config()
camera_settings = {}
device_names = {}

def load_all_settings():
    """Load all persistent settings"""
    load_camera_settings()
    load_device_names()
    create_directories()

def load_camera_settings():
    """Load camera settings from file asynchronously"""
    def _load_thread():
        try:
            settings_file = Path(config.IMAGE_DIR) / 'camera_settings.json'
            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    camera_settings.update(loaded_settings)
                logging.info("Camera settings loaded")
        except Exception as e:
            logging.error(f"Error loading camera settings: {e}")
    
    # Run load in background thread to avoid blocking GUI
    import threading
    load_thread = threading.Thread(target=_load_thread, daemon=True)
    load_thread.start()
    # Wait briefly for initial load at startup
    load_thread.join(timeout=0.1)

def save_camera_settings():
    """Save camera settings to file asynchronously"""
    def _save_thread():
        try:
            settings_file = Path(config.IMAGE_DIR) / 'camera_settings.json'
            # Make a copy to avoid thread safety issues
            settings_copy = camera_settings.copy()
            with open(settings_file, 'w') as f:
                json.dump(settings_copy, f, indent=2)
            logging.info("Camera settings saved successfully")
        except Exception as e:
            logging.error(f"Error saving camera settings: {e}")
    
    # Run save in background thread to avoid blocking GUI
    import threading
    save_thread = threading.Thread(target=_save_thread, daemon=True)
    save_thread.start()

def load_device_names():
    """Load device names asynchronously"""
    def _load_thread():
        global device_names
        try:
            names_file = Path(config.IMAGE_DIR) / 'device_names.json'
            if names_file.exists():
                with open(names_file, 'r') as f:
                    device_names = json.load(f)
            else:
                device_names = {}
        except Exception as e:
            logging.error(f"Error loading device names: {e}")
            device_names = {}
    
    # Run load in background thread
    import threading
    load_thread = threading.Thread(target=_load_thread, daemon=True)
    load_thread.start()
    # Wait briefly for initial load
    load_thread.join(timeout=0.1)
            # Initialize default names
            for i, (name, slave_info) in enumerate(config.SLAVES.items()):
                device_names[slave_info["ip"]] = name
    except Exception as e:
        logging.error(f"Error loading device names: {e}")

def save_device_names():
    """Save device names"""
    try:
        names_file = Path(config.IMAGE_DIR) / 'device_names.json'
        with open(names_file, 'w') as f:
            json.dump(device_names, f, indent=2)
    except Exception as e:
        logging.error(f"Error saving device names: {e}")

def create_directories():
    """Create necessary directories"""
    Path(config.IMAGE_DIR).mkdir(exist_ok=True)
    Path(config.CONFIG_DIR).mkdir(exist_ok=True)
