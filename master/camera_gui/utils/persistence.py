"""
Data persistence utilities
"""

import json
import logging
from pathlib import Path
from config.settings import config


def save_json_data(filename, data):
    """Save data to JSON file"""
    try:
        filepath = Path(config.CONFIG_DIR) / filename
        filepath.parent.mkdir(exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logging.info(f"Saved data to {filepath}")
        return True
        
    except Exception as e:
        logging.error(f"Error saving {filename}: {e}")
        return False


def load_json_data(filename, default=None):
    """Load data from JSON file"""
    try:
        filepath = Path(config.CONFIG_DIR) / filename
        
        if filepath.exists():
            with open(filepath, 'r') as f:
                data = json.load(f)
            logging.info(f"Loaded data from {filepath}")
            return data
        else:
            logging.info(f"File {filepath} not found, using default")
            return default or {}
            
    except Exception as e:
        logging.error(f"Error loading {filename}: {e}")
        return default or {}


def save_camera_templates(templates):
    """Save camera settings templates"""
    return save_json_data('camera_templates.json', templates)


def load_camera_templates():
    """Load camera settings templates"""
    return load_json_data('camera_templates.json', {})
