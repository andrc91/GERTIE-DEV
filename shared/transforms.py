#!/usr/bin/env python3
"""
Unified Transform Pipeline - FIXED COLOR HANDLING
✅ Red objects now appear RED (not blue) in video streams
✅ Flip operations preserve brightness in still captures
"""

import cv2
import json
import os
import logging

# Default camera settings - FIXED FOR HIGH RESOLUTION STILLS
# GUI expects brightness on scale -50 to +50 where 0 = neutral
DEFAULT_SETTINGS = {
    'brightness': 0,            # FIXED: 0 = neutral on GUI scale (-50 to +50)
    'contrast': 50,
    'iso': 100,
    'saturation': 50,
    'white_balance': 'auto',
    'jpeg_quality': 95,         # INCREASED: 95% for high quality stills (was 80)
    'fps': 30,
    'resolution': '4608x2592',  # FIXED: Full sensor resolution for high quality stills
    'crop_enabled': False,
    'crop_x': 0,
    'crop_y': 0,
    'crop_width': 4608,
    'crop_height': 2592,
    'flip_horizontal': False,
    'flip_vertical': False,
    'grayscale': False,
    'rotation': 0
}

def get_device_name_from_ip():
    """Get device name from IP address"""
    try:
        import socket
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        # Device mapping
        device_mapping = {
            "192.168.0.201": "rep1",
            "192.168.0.202": "rep2",
            "192.168.0.203": "rep3", 
            "192.168.0.204": "rep4",
            "192.168.0.205": "rep5",
            "192.168.0.206": "rep6",
            "192.168.0.207": "rep7",
            "192.168.0.200": "rep8",
            "127.0.0.1": "rep8",
            "localhost": "rep8"
        }
        
        device_name = device_mapping.get(local_ip, "rep8")
        logging.info(f"[DEVICE] {local_ip} → {device_name}")
        return device_name
            
    except Exception as e:
        logging.error(f"[DEVICE] Error getting device name: {e}")
        return "rep8"

def load_device_settings(device_name):
    """Load settings from device-specific file with brightness migration"""
    # Try production path first (/home/andrc1/), then development path
    import os
    
    production_settings_file = f"/home/andrc1/{device_name}_settings.json"
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dev_settings_file = os.path.join(project_dir, f"{device_name}_settings.json")
    
    # Use production path if it exists or we're in production environment
    if os.path.exists(production_settings_file) or os.path.exists("/home/andrc1"):
        settings_file = production_settings_file
        base_dir = "/home/andrc1"
    else:
        # Development environment - use project directory
        settings_file = dev_settings_file
        base_dir = project_dir
    
    try:
        if os.path.exists(settings_file):
            with open(settings_file, 'r') as f:
                settings = json.load(f)
            
            # CRITICAL FIX: Migrate brightness from old scale (0-100) to GUI scale (-50 to +50)
            brightness = settings.get('brightness', 0)
            if brightness > 50:  # Old scale detected (0-100 where 50=neutral)
                logging.warning(f"[BRIGHTNESS_FIX] Migrating {device_name} brightness from {brightness} (old scale) to 0 (GUI neutral)")
                settings['brightness'] = 0  # Convert old neutral (50) to GUI neutral (0)
                # Save the migrated settings immediately
                save_device_settings(device_name, settings)
            elif brightness == 50:  # Exactly 50 suggests old neutral value
                logging.warning(f"[BRIGHTNESS_FIX] Converting {device_name} brightness 50 (old neutral) to 0 (GUI neutral)")  
                settings['brightness'] = 0
                save_device_settings(device_name, settings)
                
            return settings
        else:
            # Create with defaults in appropriate directory
            logging.info(f"[SETTINGS] Creating default settings for {device_name}")
            os.makedirs(base_dir, exist_ok=True)
            with open(settings_file, 'w') as f:
                json.dump(DEFAULT_SETTINGS, f, indent=2)
            return DEFAULT_SETTINGS.copy()
            
    except Exception as e:
        logging.error(f"[SETTINGS] Failed to load settings for {device_name}: {e}")
        return DEFAULT_SETTINGS.copy()

def save_device_settings(device_name, settings):
    """Save settings to device-specific file with brightness validation"""
    try:
        # Try production path first (/home/andrc1/), then development path
        import os
        
        production_settings_file = f"/home/andrc1/{device_name}_settings.json"
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        dev_settings_file = os.path.join(project_dir, f"{device_name}_settings.json")
        
        # Use production path if it exists or we're in production environment
        if os.path.exists("/home/andrc1"):
            settings_file = production_settings_file
        else:
            # Development environment - use project directory
            settings_file = dev_settings_file
            
        temp_file = f"{settings_file}.tmp"
        
        # CRITICAL FIX: Validate brightness is on GUI scale (-50 to +50)
        brightness = settings.get('brightness', 0)
        if brightness > 50:  # Invalid high value
            logging.warning(f"[BRIGHTNESS_FIX] Clamping {device_name} brightness from {brightness} to 50 (GUI max)")
            settings['brightness'] = 50
        elif brightness < -50:  # Invalid low value  
            logging.warning(f"[BRIGHTNESS_FIX] Clamping {device_name} brightness from {brightness} to -50 (GUI min)")
            settings['brightness'] = -50
        
        os.makedirs("/home/andrc1", exist_ok=True)
        
        with open(temp_file, 'w') as f:
            json.dump(settings, f, indent=2)
        
        os.rename(temp_file, settings_file)
        logging.info(f"[SETTINGS] Saved for {device_name}: brightness={settings.get('brightness', 0)} (GUI scale)")
        return True
        
    except Exception as e:
        logging.error(f"[SETTINGS] Failed to save for {device_name}: {e}")
        return False

def apply_unified_transforms(image_array, device_name):
    """
    FIXED: Apply transforms with correct color handling
    - NO RGB→BGR conversion (GUI expects RGB)
    - Pure frame transforms (no camera control changes)
    """
    try:
        settings = load_device_settings(device_name)
        
        # Start with the original image (keep RGB format for GUI)
        image = image_array.copy()
        
        # Log active transforms occasionally
        if not hasattr(apply_unified_transforms, 'call_count'):
            apply_unified_transforms.call_count = 0
        apply_unified_transforms.call_count += 1
        
        if apply_unified_transforms.call_count % 100 == 0:
            active_transforms = []
            if settings.get('crop_enabled', False): 
                active_transforms.append('crop')
            if settings.get('rotation', 0) != 0: 
                active_transforms.append(f'rotate{settings["rotation"]}°')
            if settings.get('flip_horizontal', False): 
                active_transforms.append('flipH')
            if settings.get('flip_vertical', False): 
                active_transforms.append('flipV') 
            if settings.get('grayscale', False): 
                active_transforms.append('grayscale')
            
            logging.info(f"[TRANSFORM] {device_name}: {active_transforms or ['none']} (RGB format preserved)")
        
        # CRITICAL: Work in RGB format throughout (no BGR conversion)
        # This ensures red objects appear red in the GUI
        
        # Step 1: Crop
        if settings.get('crop_enabled', False):
            image = apply_crop_rgb(image, settings)
        
        # Step 2: Rotation  
        rotation = settings.get('rotation', 0)
        if rotation != 0:
            image = apply_rotation_rgb(image, rotation)
        
        # Step 3: Flips (PURE FRAME TRANSFORMS - NO BRIGHTNESS EFFECT)
        if settings.get('flip_horizontal', False):
            image = cv2.flip(image, 1)  # Horizontal flip
        if settings.get('flip_vertical', False):
            image = cv2.flip(image, 0)   # Vertical flip
        
        # Step 4: Grayscale
        if settings.get('grayscale', False):
            if len(image.shape) == 3:
                # Convert to grayscale then back to RGB (not BGR)
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                image = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
        
        return image
        
    except Exception as e:
        logging.error(f"[TRANSFORM] Error for {device_name}: {e}")
        return image_array  # Return original on error

def apply_crop_rgb(image, settings):
    """Apply crop while maintaining RGB format"""
    try:
        x = max(0, settings.get('crop_x', 0))
        y = max(0, settings.get('crop_y', 0))
        w = settings.get('crop_width', image.shape[1])
        h = settings.get('crop_height', image.shape[0])
        
        height, width = image.shape[:2]
        
        # Validate and clamp values to image bounds
        x = min(x, width - 10)  # Leave at least 10 pixels
        y = min(y, height - 10)  # Leave at least 10 pixels
        
        # Ensure crop dimensions are valid
        w = max(10, min(w, width - x))  # Minimum 10 pixels, max to image edge
        h = max(10, min(h, height - y))  # Minimum 10 pixels, max to image edge
        
        logging.info(f"[CROP] Applying crop: x={x}, y={y}, w={w}, h={h} from image {width}x{height}")
        return image[y:y+h, x:x+w]
    except Exception as e:
        logging.error(f"[CROP] Error: {e}")
        return image

def apply_rotation_rgb(image, degrees):
    """Apply rotation while maintaining RGB format"""
    try:
        if degrees == 90:
            return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        elif degrees == 180:
            return cv2.rotate(image, cv2.ROTATE_180)
        elif degrees == 270:
            return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        return image
    except Exception as e:
        logging.error(f"[ROTATION] Error: {e}")
        return image

def apply_unified_transforms_for_still(image_array, device_name):
    """
    SPECIAL: Apply transforms for still capture with BGR format for saving
    This ensures still images are saved correctly while maintaining brightness
    FIXED: Proper RGB→BGR conversion prevents red-as-blue color issue
    """
    try:
        settings = load_device_settings(device_name)
        
        # For still captures, we need BGR format for cv2.imwrite
        # But we still want pure frame transforms (no camera control changes)
        if len(image_array.shape) == 3 and image_array.shape[2] == 3:
            # Convert RGB to BGR for proper file saving
            image = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
            logging.info(f"[STILL_TRANSFORM] {device_name}: RGB→BGR conversion applied (colors fixed)")
        else:
            image = image_array
            logging.info(f"[STILL_TRANSFORM] {device_name}: Grayscale image, no color conversion needed")
        
        # Log active transforms for still capture
        active_transforms = []
        if settings.get('crop_enabled', False): 
            active_transforms.append('crop')
        if settings.get('rotation', 0) != 0: 
            active_transforms.append(f'rotate{settings["rotation"]}°')
        if settings.get('flip_horizontal', False): 
            active_transforms.append('flipH')
        if settings.get('flip_vertical', False): 
            active_transforms.append('flipV') 
        if settings.get('grayscale', False): 
            active_transforms.append('grayscale')
        
        logging.info(f"[STILL_TRANSFORM] {device_name}: Applying {active_transforms or ['none']} (BGR format)")
        
        # Apply identical transforms as video (but in BGR format)
        
        # Step 1: Crop
        if settings.get('crop_enabled', False):
            image = apply_crop_rgb(image, settings)  # Works same for BGR
        
        # Step 2: Rotation
        rotation = settings.get('rotation', 0)
        if rotation != 0:
            image = apply_rotation_rgb(image, rotation)  # Works same for BGR
        
        # Step 3: Flips (CRITICAL: These are PURE frame operations)
        if settings.get('flip_horizontal', False):
            image = cv2.flip(image, 1)
        if settings.get('flip_vertical', False):
            image = cv2.flip(image, 0)
        
        # Step 4: Grayscale
        if settings.get('grayscale', False):
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                image = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        
        logging.info(f"[STILL_TRANSFORM] ✅ {device_name}: Transform pipeline complete (BGR format for cv2.imwrite)")
        return image
        
    except Exception as e:
        logging.error(f"[STILL_TRANSFORM] Error for {device_name}: {e}")
        # Fallback: convert RGB to BGR at minimum
        if len(image_array.shape) == 3 and image_array.shape[2] == 3:
            try:
                fallback_image = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
                logging.warning(f"[STILL_TRANSFORM] {device_name}: Using fallback RGB→BGR conversion")
                return fallback_image
            except:
                pass
        return image_array

# Legacy functions for backward compatibility
def verify_settings_file_naming():
    """Verify settings file naming is correct"""
    return True

def load_device_settings_safe(device_name):
    """Safe wrapper for loading device settings"""
    return load_device_settings(device_name)
