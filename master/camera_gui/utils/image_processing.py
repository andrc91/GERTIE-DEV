"""
Image processing utilities
"""

import cv2
import numpy as np
from PIL import Image


def resize_for_display(image, target_size=(280, 210)):
    """Resize image for GUI display"""
    if isinstance(image, Image.Image):
        return image.resize(target_size, Image.Resampling.NEAREST)
    elif isinstance(image, np.ndarray):
        return cv2.resize(image, target_size)
    else:
        raise ValueError("Unsupported image type")


def fix_color_channels(image):
    """Fix BGR to RGB color channel order"""
    if isinstance(image, Image.Image):
        r, g, b = image.split()
        return Image.merge("RGB", (b, g, r))
    elif isinstance(image, np.ndarray):
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    else:
        raise ValueError("Unsupported image type")


def apply_transforms(image, transforms):
    """Apply image transforms (flip, rotate, etc.)"""
    if not transforms:
        return image
    
    result = image.copy() if isinstance(image, np.ndarray) else image.copy()
    
    # Apply flip transforms
    if transforms.get('flip_horizontal', False):
        if isinstance(result, np.ndarray):
            result = cv2.flip(result, 1)
        else:
            result = result.transpose(Image.FLIP_LEFT_RIGHT)
    
    if transforms.get('flip_vertical', False):
        if isinstance(result, np.ndarray):
            result = cv2.flip(result, 0)
        else:
            result = result.transpose(Image.FLIP_TOP_BOTTOM)
    
    # Apply rotation
    rotation = transforms.get('rotation', 0)
    if rotation != 0:
        if isinstance(result, np.ndarray):
            if rotation == 90:
                result = cv2.rotate(result, cv2.ROTATE_90_CLOCKWISE)
            elif rotation == 180:
                result = cv2.rotate(result, cv2.ROTATE_180)
            elif rotation == 270:
                result = cv2.rotate(result, cv2.ROTATE_90_COUNTERCLOCKWISE)
        else:
            result = result.rotate(-rotation, expand=True)
    
    # Apply grayscale
    if transforms.get('grayscale', False):
        if isinstance(result, np.ndarray):
            if len(result.shape) == 3:
                result = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
                result = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
        else:
            result = result.convert('L').convert('RGB')
    
    return result
