import numpy as np
import pytest
import cv2
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from shared.transforms import apply_unified_transforms, apply_unified_transforms_for_still, DEFAULT_SETTINGS

def create_test_image(width=100, height=100):
    """Create a test image with known patterns"""
    # Create RGB image with distinct colors
    image = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Top half red, bottom half blue
    image[:height//2, :, 0] = 255  # Red channel
    image[height//2:, :, 2] = 255  # Blue channel
    
    # Add some gradient for flip testing
    for i in range(width):
        image[:, i, 1] = int(255 * i / width)  # Green gradient
    
    return image

def test_no_transforms():
    """Test that image passes through unchanged with default settings"""
    image = create_test_image()
    result = apply_unified_transforms(image, "test_device")
    np.testing.assert_array_equal(image, result)

def test_horizontal_flip():
    """Test horizontal flip transform"""
    image = create_test_image()
    
    # Mock settings with horizontal flip
    import json
    import tempfile
    test_settings = DEFAULT_SETTINGS.copy()
    test_settings['flip_horizontal'] = True
    
    # Create temporary settings file
    with tempfile.NamedTemporaryFile(mode='w', suffix='_settings.json', delete=False) as f:
        json.dump(test_settings, f)
        settings_file = f.name
    
    try:
        # Monkey patch the load function to use our test settings
        from shared import transforms
        original_load = transforms.load_device_settings
        transforms.load_device_settings = lambda device_name: test_settings
        
        result = apply_unified_transforms(image, "test_device")
        
        # Check that horizontal flip was applied
        expected = cv2.flip(image, 1)
        np.testing.assert_array_equal(result, expected)
        
    finally:
        transforms.load_device_settings = original_load
        os.unlink(settings_file)

def test_vertical_flip():
    """Test vertical flip transform"""
    image = create_test_image()
    
    test_settings = DEFAULT_SETTINGS.copy()
    test_settings['flip_vertical'] = True
    
    from shared import transforms
    original_load = transforms.load_device_settings
    transforms.load_device_settings = lambda device_name: test_settings
    
    try:
        result = apply_unified_transforms(image, "test_device")
        expected = cv2.flip(image, 0)
        np.testing.assert_array_equal(result, expected)
    finally:
        transforms.load_device_settings = original_load

def test_both_flips():
    """Test both horizontal and vertical flips together"""
    image = create_test_image()
    
    test_settings = DEFAULT_SETTINGS.copy()
    test_settings['flip_horizontal'] = True
    test_settings['flip_vertical'] = True
    
    from shared import transforms
    original_load = transforms.load_device_settings
    transforms.load_device_settings = lambda device_name: test_settings
    
    try:
        result = apply_unified_transforms(image, "test_device")
        expected = cv2.flip(cv2.flip(image, 1), 0)  # Apply both flips
        np.testing.assert_array_equal(result, expected)
    finally:
        transforms.load_device_settings = original_load

def test_crop_transform():
    """Test crop transform"""
    image = create_test_image(100, 100)
    
    test_settings = DEFAULT_SETTINGS.copy()
    test_settings['crop_enabled'] = True
    test_settings['crop_x'] = 10
    test_settings['crop_y'] = 10  
    test_settings['crop_width'] = 50
    test_settings['crop_height'] = 50
    
    from shared import transforms
    original_load = transforms.load_device_settings
    transforms.load_device_settings = lambda device_name: test_settings
    
    try:
        result = apply_unified_transforms(image, "test_device")
        assert result.shape == (50, 50, 3)
        expected = image[10:60, 10:60]
        np.testing.assert_array_equal(result, expected)
    finally:
        transforms.load_device_settings = original_load

def test_rotation_90():
    """Test 90-degree rotation"""
    image = create_test_image(50, 50)
    
    test_settings = DEFAULT_SETTINGS.copy()
    test_settings['rotation'] = 90
    
    from shared import transforms
    original_load = transforms.load_device_settings
    transforms.load_device_settings = lambda device_name: test_settings
    
    try:
        result = apply_unified_transforms(image, "test_device")
        expected = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        np.testing.assert_array_equal(result, expected)
    finally:
        transforms.load_device_settings = original_load

def test_grayscale_transform():
    """Test grayscale transform"""
    image = create_test_image()
    
    test_settings = DEFAULT_SETTINGS.copy()
    test_settings['grayscale'] = True
    
    from shared import transforms
    original_load = transforms.load_device_settings
    transforms.load_device_settings = lambda device_name: test_settings
    
    try:
        result = apply_unified_transforms(image, "test_device")
        # Should still be 3-channel but grayscale
        assert result.shape == image.shape
        # All channels should be equal in grayscale
        assert np.all(result[:,:,0] == result[:,:,1])
        assert np.all(result[:,:,1] == result[:,:,2])
    finally:
        transforms.load_device_settings = original_load

def test_preview_vs_still_consistency():
    """Test that preview and still transforms produce consistent results"""
    image = create_test_image()
    
    test_settings = DEFAULT_SETTINGS.copy()
    test_settings['flip_horizontal'] = True
    test_settings['flip_vertical'] = True
    test_settings['rotation'] = 90
    
    from shared import transforms
    original_load = transforms.load_device_settings
    transforms.load_device_settings = lambda device_name: test_settings
    
    try:
        preview_result = apply_unified_transforms(image, "test_device")
        still_result = apply_unified_transforms_for_still(image, "test_device")
        
        # Convert still result back to RGB for comparison
        still_rgb = cv2.cvtColor(still_result, cv2.COLOR_BGR2RGB)
        
        # Should be identical after color space conversion
        np.testing.assert_array_equal(preview_result, still_rgb)
    finally:
        transforms.load_device_settings = original_load

if __name__ == "__main__":
    pytest.main([__file__])
