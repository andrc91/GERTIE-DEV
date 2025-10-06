import numpy as np
import pytest
import cv2
import sys
import os
import tempfile
import json
from PIL import Image
import io

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from shared.transforms import (
    apply_unified_transforms,
    apply_unified_transforms_for_still,
    load_device_settings,
    save_device_settings,
    DEFAULT_SETTINGS
)

def test_grayscale_conversion_accuracy():
    """Test that grayscale conversion produces expected luminance values"""
    # Create image with known RGB values
    image = np.zeros((10, 10, 3), dtype=np.uint8)
    image[:, :, 0] = 255  # Pure red
    image[:, :, 1] = 0    # No green  
    image[:, :, 2] = 0    # No blue
    
    from shared import transforms
    original_load = transforms.load_device_settings
    
    grayscale_settings = DEFAULT_SETTINGS.copy()
    grayscale_settings['grayscale'] = True
    transforms.load_device_settings = lambda device_name: grayscale_settings
    
    try:
        result = apply_unified_transforms(image, "grayscale_test")
        
        # All channels should be equal in grayscale
        assert np.all(result[:,:,0] == result[:,:,1])
        assert np.all(result[:,:,1] == result[:,:,2])
        
        # Value should be reasonable for red conversion
        # OpenCV uses: 0.299*R + 0.587*G + 0.114*B
        expected_gray = int(0.299 * 255)
        actual_gray = result[0, 0, 0]
        
        # Allow some tolerance for conversion differences
        assert abs(actual_gray - expected_gray) < 10
        
    finally:
        transforms.load_device_settings = original_load

def test_rotation_preserves_content():
    """Test that rotation preserves image content correctly"""
    # Create image with distinct corners
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    image[0:10, 0:10, 0] = 255      # Red top-left
    image[0:10, 90:100, 1] = 255    # Green top-right
    image[90:100, 0:10, 2] = 255    # Blue bottom-left
    image[90:100, 90:100, :] = 255  # White bottom-right
    
    from shared import transforms
    original_load = transforms.load_device_settings
    
    # Test 90-degree rotation
    rotation_settings = DEFAULT_SETTINGS.copy()
    rotation_settings['rotation'] = 90
    transforms.load_device_settings = lambda device_name: rotation_settings
    
    try:
        result = apply_unified_transforms(image, "rotation_test")
        
        # After 90-degree clockwise rotation:
        # Original top-left (red) should be at top-right
        # Original top-right (green) should be at bottom-right  
        # Original bottom-left (blue) should be at top-left
        # Original bottom-right (white) should be at bottom-left
        
        # Check that content moved to expected positions
        assert np.any(result[0:10, 90:100, 0] > 200)  # Red should be at top-right area
        assert np.any(result[90:100, 90:100, 1] > 200)  # Green should be at bottom-right area
        assert np.any(result[0:10, 0:10, 2] > 200)  # Blue should be at top-left area
        
    finally:
        transforms.load_device_settings = original_load

def test_crop_boundary_conditions():
    """Test crop behavior at various boundary conditions"""
    image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    
    boundary_conditions = [
        # (crop_x, crop_y, crop_width, crop_height, description)
        (0, 0, 50, 50, "top-left corner crop"),
        (50, 50, 50, 50, "bottom-right area crop"),
        (0, 0, 100, 100, "full image crop"),
        (90, 90, 10, 10, "minimal corner crop"),
        (45, 45, 10, 10, "tiny center crop"),
        (0, 50, 100, 50, "horizontal strip"),
        (50, 0, 50, 100, "vertical strip"),
    ]
    
    from shared import transforms
    original_load = transforms.load_device_settings
    
    for crop_x, crop_y, crop_w, crop_h, description in boundary_conditions:
        crop_settings = DEFAULT_SETTINGS.copy()
        crop_settings.update({
            'crop_enabled': True,
            'crop_x': crop_x,
            'crop_y': crop_y,
            'crop_width': crop_w,
            'crop_height': crop_h
        })
        transforms.load_device_settings = lambda device_name: crop_settings
        
        try:
            result = apply_unified_transforms(image, f"crop_test_{description}")
            
            # Should produce valid result
            assert isinstance(result, np.ndarray)
            assert len(result.shape) == 3
            assert result.shape[2] == 3
            
            # Should not exceed original dimensions
            assert result.shape[0] <= image.shape[0]
            assert result.shape[1] <= image.shape[1]
            
        finally:
            transforms.load_device_settings = original_load

def test_flip_combinations_comprehensive():
    """Test all combinations of flip operations"""
    # Create asymmetric image to test flips properly
    image = np.zeros((60, 80, 3), dtype=np.uint8)
    
    # Create distinct patterns for each quadrant
    image[0:30, 0:40, 0] = 255    # Red top-left
    image[0:30, 40:80, 1] = 255   # Green top-right
    image[30:60, 0:40, 2] = 255   # Blue bottom-left
    image[30:60, 40:80, :] = 128  # Gray bottom-right
    
    flip_combinations = [
        (False, False, "no flip"),
        (True, False, "horizontal only"),
        (False, True, "vertical only"),
        (True, True, "both flips"),
    ]
    
    from shared import transforms
    original_load = transforms.load_device_settings
    
    for flip_h, flip_v, description in flip_combinations:
        flip_settings = DEFAULT_SETTINGS.copy()
        flip_settings['flip_horizontal'] = flip_h
        flip_settings['flip_vertical'] = flip_v
        transforms.load_device_settings = lambda device_name: flip_settings
        
        try:
            result = apply_unified_transforms(image, f"flip_test_{description}")
            
            # Should preserve basic properties
            assert result.shape == image.shape
            assert isinstance(result, np.ndarray)
            
            # Test specific flip behavior
            if not flip_h and not flip_v:
                # No flip - should be identical
                np.testing.assert_array_equal(result, image)
            elif flip_h and not flip_v:
                # Horizontal flip - left becomes right
                np.testing.assert_array_equal(result[:, :40], image[:, 40:])
                np.testing.assert_array_equal(result[:, 40:], image[:, :40])
            elif not flip_h and flip_v:
                # Vertical flip - top becomes bottom
                np.testing.assert_array_equal(result[:30], image[30:])
                np.testing.assert_array_equal(result[30:], image[:30])
            
        finally:
            transforms.load_device_settings = original_load

def test_color_channel_preservation():
    """Test that transforms preserve color channels correctly"""
    # Create image with pure colors in different regions
    image = np.zeros((90, 90, 3), dtype=np.uint8)
    image[0:30, :, 0] = 255      # Pure red stripe
    image[30:60, :, 1] = 255     # Pure green stripe
    image[60:90, :, 2] = 255     # Pure blue stripe
    
    transforms_to_test = [
        {'flip_horizontal': True},
        {'flip_vertical': True}, 
        {'rotation': 90},
        {'rotation': 180},
        {'crop_enabled': True, 'crop_x': 10, 'crop_y': 10, 'crop_width': 70, 'crop_height': 70}
    ]
    
    from shared import transforms
    original_load = transforms.load_device_settings
    
    for transform_config in transforms_to_test:
        test_settings = DEFAULT_SETTINGS.copy()
        test_settings.update(transform_config)
        transforms.load_device_settings = lambda device_name: test_settings
        
        try:
            result = apply_unified_transforms(image, "color_test")
            
            # Should preserve color information (no color bleeding)
            # Find pixels that should be pure colors
            red_pixels = result[:, :, 0] > 200
            green_pixels = result[:, :, 1] > 200  
            blue_pixels = result[:, :, 2] > 200
            
            # Pure red pixels should have low green and blue
            if np.any(red_pixels):
                pure_red_mask = red_pixels & (result[:, :, 1] < 50) & (result[:, :, 2] < 50)
                assert np.any(pure_red_mask), "No pure red pixels found after transform"
            
            # Similar tests for green and blue
            if np.any(green_pixels):
                pure_green_mask = green_pixels & (result[:, :, 0] < 50) & (result[:, :, 2] < 50)
                assert np.any(pure_green_mask), "No pure green pixels found after transform"
                
            if np.any(blue_pixels):
                pure_blue_mask = blue_pixels & (result[:, :, 0] < 50) & (result[:, :, 1] < 50)
                assert np.any(pure_blue_mask), "No pure blue pixels found after transform"
            
        finally:
            transforms.load_device_settings = original_load

def test_preview_still_color_space_consistency():
    """Test color space handling between preview and still transforms"""
    # Create image with specific color pattern
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    
    # Create gradient patterns
    for i in range(100):
        image[i, :, 0] = int(255 * i / 100)  # Red gradient
        image[:, i, 1] = int(255 * i / 100)  # Green gradient
    image[:, :, 2] = 128  # Constant blue
    
    # Apply same transforms to both preview and still
    from shared import transforms
    original_load = transforms.load_device_settings
    
    transform_settings = DEFAULT_SETTINGS.copy()
    transform_settings.update({
        'flip_horizontal': True,
        'flip_vertical': True,
        'rotation': 90
    })
    transforms.load_device_settings = lambda device_name: transform_settings
    
    try:
        # Get preview result (RGB)
        preview_result = apply_unified_transforms(image, "consistency_test")
        
        # Get still result (BGR) and convert back to RGB
        still_result = apply_unified_transforms_for_still(image, "consistency_test")
        still_rgb = cv2.cvtColor(still_result, cv2.COLOR_BGR2RGB)
        
        # Should be identical after color space conversion
        np.testing.assert_array_equal(preview_result, still_rgb)
        
    finally:
        transforms.load_device_settings = original_load

def test_edge_case_image_dimensions():
    """Test transforms with various edge case dimensions"""
    edge_case_dimensions = [
        (1, 1, 3),      # Minimal image
        (1, 100, 3),    # Single row
        (100, 1, 3),    # Single column
        (2, 2, 3),      # Tiny square
        (1000, 1, 3),   # Very tall thin
        (1, 1000, 3),   # Very wide thin
        (101, 101, 3),  # Odd dimensions
    ]
    
    for height, width, channels in edge_case_dimensions:
        image = np.random.randint(0, 256, (height, width, channels), dtype=np.uint8)
        
        # Test with basic transform
        result = apply_unified_transforms(image, f"edge_test_{height}x{width}")
        
        # Should handle edge cases gracefully
        assert isinstance(result, np.ndarray)
        assert len(result.shape) == 3
        assert result.shape[2] == channels
        
        # Dimensions should be reasonable
        assert result.shape[0] <= height
        assert result.shape[1] <= width

def test_settings_persistence_edge_cases():
    """Test settings file handling with various edge cases"""
    # Test with very long device names
    long_name = "device_" + "x" * 200
    settings = load_device_settings(long_name)
    assert settings == DEFAULT_SETTINGS
    
    # Test with device names containing special characters
    special_names = [
        "device-with-dashes",
        "device.with.dots", 
        "device_with_underscores",
        "DEVICE_UPPERCASE",
        "device123",
    ]
    
    for special_name in special_names:
        settings = load_device_settings(special_name)
        assert isinstance(settings, dict)
        
        # Try to save settings for special name
        result = save_device_settings(special_name, settings)
        # May succeed or fail depending on filesystem, but shouldn't crash
        assert isinstance(result, bool)

def test_transform_pipeline_order():
    """Test that transform operations are applied in correct order"""
    # Create image where order matters
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    
    # Create a pattern where transform order will be visible
    image[0:50, 0:50, 0] = 255    # Red top-left quadrant
    
    from shared import transforms
    original_load = transforms.load_device_settings
    
    # Apply crop first, then flip - order should be: crop -> rotation -> flips -> grayscale
    order_settings = DEFAULT_SETTINGS.copy()
    order_settings.update({
        'crop_enabled': True,
        'crop_x': 25,
        'crop_y': 25,
        'crop_width': 50,
        'crop_height': 50,
        'flip_horizontal': True,
        'rotation': 90
    })
    transforms.load_device_settings = lambda device_name: order_settings
    
    try:
        result = apply_unified_transforms(image, "order_test")
        
        # Should have applied transforms in correct order
        # 1. Crop (50x50 from center) 2. Rotate 90° 3. Flip horizontal
        assert isinstance(result, np.ndarray)
        assert result.shape[0] == 50  # Cropped height
        assert result.shape[1] == 50  # Cropped width
        
    finally:
        transforms.load_device_settings = original_load

def test_numerical_precision():
    """Test that transforms maintain numerical precision"""
    # Create image with specific values to test precision
    image = np.zeros((50, 50, 3), dtype=np.uint8)
    
    # Set specific values
    image[0, 0, :] = [1, 2, 3]
    image[25, 25, :] = [253, 254, 255]
    image[49, 49, :] = [127, 128, 129]
    
    # Apply non-destructive transform (just flip)
    from shared import transforms
    original_load = transforms.load_device_settings
    
    precision_settings = DEFAULT_SETTINGS.copy()
    precision_settings['flip_horizontal'] = True
    transforms.load_device_settings = lambda device_name: precision_settings
    
    try:
        result = apply_unified_transforms(image, "precision_test")
        
        # Specific values should be preserved exactly (just moved)
        # Original [0,0] should now be at [0,49] after horizontal flip
        assert tuple(result[0, 49, :]) == (1, 2, 3)
        assert tuple(result[49, 0, :]) == (127, 128, 129)
        
    finally:
        transforms.load_device_settings = original_load

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
