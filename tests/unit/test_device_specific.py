import numpy as np
import pytest
import cv2
import sys
import os
import json
import tempfile
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from shared.transforms import (
    apply_unified_transforms,
    apply_unified_transforms_for_still, 
    load_device_settings,
    save_device_settings,
    DEFAULT_SETTINGS,
    get_device_name_from_ip
)

def test_device_rep1_specific_settings():
    """Test device-specific settings for rep1"""
    image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    result = apply_unified_transforms(image, "rep1")
    assert isinstance(result, np.ndarray)

def test_device_rep2_specific_settings():
    """Test device-specific settings for rep2"""
    image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    result = apply_unified_transforms(image, "rep2")
    assert isinstance(result, np.ndarray)

def test_device_rep3_specific_settings():
    """Test device-specific settings for rep3"""
    image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    result = apply_unified_transforms(image, "rep3")
    assert isinstance(result, np.ndarray)

def test_device_rep4_specific_settings():
    """Test device-specific settings for rep4"""
    image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    result = apply_unified_transforms(image, "rep4")
    assert isinstance(result, np.ndarray)

def test_device_rep5_specific_settings():
    """Test device-specific settings for rep5"""
    image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    result = apply_unified_transforms(image, "rep5")
    assert isinstance(result, np.ndarray)

def test_device_rep6_specific_settings():
    """Test device-specific settings for rep6"""
    image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    result = apply_unified_transforms(image, "rep6")
    assert isinstance(result, np.ndarray)

def test_device_rep7_specific_settings():
    """Test device-specific settings for rep7"""
    image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    result = apply_unified_transforms(image, "rep7")
    assert isinstance(result, np.ndarray)

def test_device_rep8_specific_settings():
    """Test device-specific settings for rep8"""
    image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    result = apply_unified_transforms(image, "rep8")
    assert isinstance(result, np.ndarray)

def test_brightness_setting_minus_50():
    """Test brightness at minimum value (-50)"""
    image = np.random.randint(100, 200, (50, 50, 3), dtype=np.uint8)
    
    from shared import transforms
    original_load = transforms.load_device_settings
    
    settings = DEFAULT_SETTINGS.copy()
    settings['brightness'] = -50
    transforms.load_device_settings = lambda device_name: settings
    
    try:
        result = apply_unified_transforms(image, "brightness_min_test")
        assert isinstance(result, np.ndarray)
    finally:
        transforms.load_device_settings = original_load

def test_brightness_setting_plus_50():
    """Test brightness at maximum value (+50)"""
    image = np.random.randint(50, 150, (50, 50, 3), dtype=np.uint8)
    
    from shared import transforms
    original_load = transforms.load_device_settings
    
    settings = DEFAULT_SETTINGS.copy()
    settings['brightness'] = 50
    transforms.load_device_settings = lambda device_name: settings
    
    try:
        result = apply_unified_transforms(image, "brightness_max_test")
        assert isinstance(result, np.ndarray)
    finally:
        transforms.load_device_settings = original_load

def test_brightness_setting_zero():
    """Test brightness at neutral value (0)"""
    image = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
    
    from shared import transforms
    original_load = transforms.load_device_settings
    
    settings = DEFAULT_SETTINGS.copy()
    settings['brightness'] = 0
    transforms.load_device_settings = lambda device_name: settings
    
    try:
        result = apply_unified_transforms(image, "brightness_neutral_test")
        assert isinstance(result, np.ndarray)
    finally:
        transforms.load_device_settings = original_load

def test_contrast_setting_variations():
    """Test various contrast settings"""
    image = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
    
    contrast_values = [0, 25, 50, 75, 100]
    
    from shared import transforms
    original_load = transforms.load_device_settings
    
    for contrast in contrast_values:
        settings = DEFAULT_SETTINGS.copy()
        settings['contrast'] = contrast
        transforms.load_device_settings = lambda device_name: settings
        
        try:
            result = apply_unified_transforms(image, f"contrast_{contrast}_test")
            assert isinstance(result, np.ndarray)
        finally:
            transforms.load_device_settings = original_load

def test_saturation_setting_variations():
    """Test various saturation settings"""
    image = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
    
    saturation_values = [0, 25, 50, 75, 100]
    
    from shared import transforms
    original_load = transforms.load_device_settings
    
    for saturation in saturation_values:
        settings = DEFAULT_SETTINGS.copy()
        settings['saturation'] = saturation
        transforms.load_device_settings = lambda device_name: settings
        
        try:
            result = apply_unified_transforms(image, f"saturation_{saturation}_test")
            assert isinstance(result, np.ndarray)
        finally:
            transforms.load_device_settings = original_load

def test_iso_setting_variations():
    """Test various ISO settings"""
    image = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
    
    iso_values = [100, 200, 400, 800, 1600]
    
    from shared import transforms
    original_load = transforms.load_device_settings
    
    for iso in iso_values:
        settings = DEFAULT_SETTINGS.copy()
        settings['iso'] = iso
        transforms.load_device_settings = lambda device_name: settings
        
        try:
            result = apply_unified_transforms(image, f"iso_{iso}_test")
            assert isinstance(result, np.ndarray)
        finally:
            transforms.load_device_settings = original_load

def test_jpeg_quality_variations():
    """Test various JPEG quality settings"""
    image = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
    
    quality_values = [50, 70, 80, 90, 95, 100]
    
    from shared import transforms
    original_load = transforms.load_device_settings
    
    for quality in quality_values:
        settings = DEFAULT_SETTINGS.copy()
        settings['jpeg_quality'] = quality
        transforms.load_device_settings = lambda device_name: settings
        
        try:
            result = apply_unified_transforms(image, f"quality_{quality}_test")
            assert isinstance(result, np.ndarray)
        finally:
            transforms.load_device_settings = original_load

def test_fps_setting_variations():
    """Test various FPS settings"""
    image = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
    
    fps_values = [15, 24, 30, 60]
    
    from shared import transforms
    original_load = transforms.load_device_settings
    
    for fps in fps_values:
        settings = DEFAULT_SETTINGS.copy()
        settings['fps'] = fps
        transforms.load_device_settings = lambda device_name: settings
        
        try:
            result = apply_unified_transforms(image, f"fps_{fps}_test")
            assert isinstance(result, np.ndarray)
        finally:
            transforms.load_device_settings = original_load

def test_resolution_setting_variations():
    """Test various resolution settings"""
    image = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
    
    resolution_values = ['640x480', '1280x720', '1920x1080', '4608x2592']
    
    from shared import transforms
    original_load = transforms.load_device_settings
    
    for resolution in resolution_values:
        settings = DEFAULT_SETTINGS.copy()
        settings['resolution'] = resolution
        transforms.load_device_settings = lambda device_name: settings
        
        try:
            result = apply_unified_transforms(image, f"resolution_{resolution}_test")
            assert isinstance(result, np.ndarray)
        finally:
            transforms.load_device_settings = original_load

def test_white_balance_variations():
    """Test various white balance settings"""
    image = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
    
    wb_values = ['auto', 'daylight', 'cloudy', 'tungsten', 'fluorescent']
    
    from shared import transforms
    original_load = transforms.load_device_settings
    
    for wb in wb_values:
        settings = DEFAULT_SETTINGS.copy()
        settings['white_balance'] = wb
        transforms.load_device_settings = lambda device_name: settings
        
        try:
            result = apply_unified_transforms(image, f"wb_{wb}_test")
            assert isinstance(result, np.ndarray)
        finally:
            transforms.load_device_settings = original_load

def test_crop_corner_positions():
    """Test crop at different corner positions"""
    image = np.random.randint(0, 256, (200, 200, 3), dtype=np.uint8)
    
    corner_crops = [
        {'crop_x': 0, 'crop_y': 0, 'crop_width': 50, 'crop_height': 50},      # Top-left
        {'crop_x': 150, 'crop_y': 0, 'crop_width': 50, 'crop_height': 50},    # Top-right
        {'crop_x': 0, 'crop_y': 150, 'crop_width': 50, 'crop_height': 50},    # Bottom-left
        {'crop_x': 150, 'crop_y': 150, 'crop_width': 50, 'crop_height': 50},  # Bottom-right
        {'crop_x': 75, 'crop_y': 75, 'crop_width': 50, 'crop_height': 50},    # Center
    ]
    
    from shared import transforms
    original_load = transforms.load_device_settings
    
    for i, crop_params in enumerate(corner_crops):
        settings = DEFAULT_SETTINGS.copy()
        settings['crop_enabled'] = True
        settings.update(crop_params)
        transforms.load_device_settings = lambda device_name: settings
        
        try:
            result = apply_unified_transforms(image, f"corner_crop_{i}_test")
            assert isinstance(result, np.ndarray)
            assert result.shape == (50, 50, 3)
        finally:
            transforms.load_device_settings = original_load

def test_rotation_combinations_with_flips():
    """Test rotation combined with different flip combinations"""
    image = np.random.randint(0, 256, (80, 80, 3), dtype=np.uint8)
    
    combinations = [
        {'rotation': 0, 'flip_horizontal': True, 'flip_vertical': False},
        {'rotation': 0, 'flip_horizontal': False, 'flip_vertical': True},
        {'rotation': 90, 'flip_horizontal': True, 'flip_vertical': False},
        {'rotation': 90, 'flip_horizontal': False, 'flip_vertical': True},
        {'rotation': 180, 'flip_horizontal': True, 'flip_vertical': False},
        {'rotation': 180, 'flip_horizontal': False, 'flip_vertical': True},
        {'rotation': 270, 'flip_horizontal': True, 'flip_vertical': False},
        {'rotation': 270, 'flip_horizontal': False, 'flip_vertical': True},
    ]
    
    from shared import transforms
    original_load = transforms.load_device_settings
    
    for i, combo in enumerate(combinations):
        settings = DEFAULT_SETTINGS.copy()
        settings.update(combo)
        transforms.load_device_settings = lambda device_name: settings
        
        try:
            result = apply_unified_transforms(image, f"rotation_flip_combo_{i}_test")
            assert isinstance(result, np.ndarray)
        finally:
            transforms.load_device_settings = original_load

def test_preview_vs_still_different_sizes():
    """Test preview vs still consistency with different image sizes"""
    sizes = [(100, 100), (200, 150), (320, 240), (640, 480)]
    
    from shared import transforms
    original_load = transforms.load_device_settings
    
    settings = DEFAULT_SETTINGS.copy()
    settings.update({'flip_horizontal': True, 'flip_vertical': True})
    transforms.load_device_settings = lambda device_name: settings
    
    try:
        for width, height in sizes:
            image = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
            
            preview_result = apply_unified_transforms(image, f"preview_size_{width}x{height}")
            still_result = apply_unified_transforms_for_still(image, f"still_size_{width}x{height}")
            
            # Convert still result back to RGB
            still_rgb = cv2.cvtColor(still_result, cv2.COLOR_BGR2RGB)
            
            # Should be identical
            np.testing.assert_array_equal(preview_result, still_rgb)
            
    finally:
        transforms.load_device_settings = original_load

def test_grayscale_with_all_rotations():
    """Test grayscale conversion combined with all rotation angles"""
    image = np.random.randint(0, 256, (60, 60, 3), dtype=np.uint8)
    
    rotations = [0, 90, 180, 270]
    
    from shared import transforms
    original_load = transforms.load_device_settings
    
    for rotation in rotations:
        settings = DEFAULT_SETTINGS.copy()
        settings['grayscale'] = True
        settings['rotation'] = rotation
        transforms.load_device_settings = lambda device_name: settings
        
        try:
            result = apply_unified_transforms(image, f"grayscale_rotation_{rotation}_test")
            
            assert isinstance(result, np.ndarray)
            # Should be grayscale (all channels equal)
            assert np.all(result[:,:,0] == result[:,:,1])
            assert np.all(result[:,:,1] == result[:,:,2])
            
        finally:
            transforms.load_device_settings = original_load

def test_crop_with_all_rotations():
    """Test crop combined with all rotation angles"""
    image = np.random.randint(0, 256, (120, 120, 3), dtype=np.uint8)
    
    rotations = [0, 90, 180, 270]
    
    from shared import transforms
    original_load = transforms.load_device_settings
    
    for rotation in rotations:
        settings = DEFAULT_SETTINGS.copy()
        settings.update({
            'crop_enabled': True,
            'crop_x': 20,
            'crop_y': 20,
            'crop_width': 80,
            'crop_height': 80,
            'rotation': rotation
        })
        transforms.load_device_settings = lambda device_name: settings
        
        try:
            result = apply_unified_transforms(image, f"crop_rotation_{rotation}_test")
            assert isinstance(result, np.ndarray)
            # After crop then rotation, should have rotated the cropped region
            assert result.shape[0] == 80  # Height after crop
            assert result.shape[1] == 80  # Width after crop
            
        finally:
            transforms.load_device_settings = original_load

def test_all_settings_combinations():
    """Test various combinations of all available settings"""
    image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    
    test_combinations = [
        # Realistic camera configurations
        {'brightness': 10, 'contrast': 60, 'saturation': 45, 'flip_horizontal': True},
        {'brightness': -10, 'contrast': 40, 'rotation': 90, 'grayscale': True},
        {'crop_enabled': True, 'crop_x': 25, 'crop_y': 25, 'crop_width': 50, 'crop_height': 50, 'flip_vertical': True},
        {'rotation': 180, 'flip_horizontal': True, 'flip_vertical': True, 'brightness': 5},
        {'grayscale': True, 'contrast': 70, 'saturation': 30, 'jpeg_quality': 90},
    ]
    
    from shared import transforms
    original_load = transforms.load_device_settings
    
    for i, combo in enumerate(test_combinations):
        settings = DEFAULT_SETTINGS.copy()
        settings.update(combo)
        transforms.load_device_settings = lambda device_name: settings
        
        try:
            result = apply_unified_transforms(image, f"settings_combo_{i}_test")
            assert isinstance(result, np.ndarray)
            assert len(result.shape) == 3
            assert result.shape[2] == 3
            
        finally:
            transforms.load_device_settings = original_load

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
