import numpy as np
import pytest
import cv2
import sys
import os
from hypothesis import given, strategies as st
from hypothesis import settings as hyp_settings

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from shared.transforms import apply_unified_transforms, apply_crop_rgb, apply_rotation_rgb, DEFAULT_SETTINGS

@given(
    width=st.integers(min_value=50, max_value=1000),
    height=st.integers(min_value=50, max_value=1000),
    channels=st.just(3)
)
@hyp_settings(max_examples=20)
def test_transform_preserves_image_format(width, height, channels):
    """Property test: transforms should preserve basic image properties"""
    # Create random image
    image = np.random.randint(0, 256, (height, width, channels), dtype=np.uint8)
    
    # Apply transforms (should not crash)
    result = apply_unified_transforms(image, "test_device")
    
    # Basic properties should be preserved
    assert isinstance(result, np.ndarray)
    assert result.dtype == np.uint8
    assert len(result.shape) == 3
    assert result.shape[2] == 3  # RGB channels

@given(
    crop_x=st.integers(min_value=0, max_value=50),
    crop_y=st.integers(min_value=0, max_value=50),
    crop_width=st.integers(min_value=10, max_value=100),
    crop_height=st.integers(min_value=10, max_value=100)
)
@hyp_settings(max_examples=15)
def test_crop_with_random_parameters(crop_x, crop_y, crop_width, crop_height):
    """Property test: crop should work with various valid parameters"""
    image = np.random.randint(0, 256, (150, 150, 3), dtype=np.uint8)
    
    settings = {
        'crop_x': crop_x,
        'crop_y': crop_y, 
        'crop_width': crop_width,
        'crop_height': crop_height
    }
    
    result = apply_crop_rgb(image, settings)
    
    # Result should be smaller than or equal to original
    assert result.shape[0] <= image.shape[0]
    assert result.shape[1] <= image.shape[1]
    assert result.shape[2] == image.shape[2]
    
    # Result should have expected dimensions (within bounds)
    expected_h = min(crop_height, image.shape[0] - crop_y)
    expected_w = min(crop_width, image.shape[1] - crop_x)
    assert result.shape[0] <= expected_h + 1  # Allow small variance
    assert result.shape[1] <= expected_w + 1

@given(rotation=st.sampled_from([0, 90, 180, 270]))
@hyp_settings(max_examples=10)
def test_rotation_with_all_angles(rotation):
    """Property test: rotation should work with all valid angles"""
    # Use square image for rotation testing
    image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    
    result = apply_rotation_rgb(image, rotation)
    
    # Basic properties preserved
    assert isinstance(result, np.ndarray)
    assert result.dtype == np.uint8
    assert len(result.shape) == 3
    assert result.shape[2] == 3

@given(
    flip_h=st.booleans(),
    flip_v=st.booleans(),
    grayscale=st.booleans(),
    rotation=st.sampled_from([0, 90, 180, 270])
)
@hyp_settings(max_examples=25)
def test_combined_transforms_random(flip_h, flip_v, grayscale, rotation):
    """Property test: combination of transforms should work reliably"""
    image = np.random.randint(0, 256, (80, 80, 3), dtype=np.uint8)
    
    # Mock settings with random transform combination
    from shared import transforms
    original_load = transforms.load_device_settings
    
    test_settings = DEFAULT_SETTINGS.copy()
    test_settings.update({
        'flip_horizontal': flip_h,
        'flip_vertical': flip_v,
        'grayscale': grayscale,
        'rotation': rotation,
        'crop_enabled': False  # Disable crop for simplicity in fuzz test
    })
    
    transforms.load_device_settings = lambda device_name: test_settings
    
    try:
        result = apply_unified_transforms(image, "fuzz_test_device")
        
        # Should not crash and preserve basic properties
        assert isinstance(result, np.ndarray)
        assert result.dtype == np.uint8
        assert len(result.shape) == 3
        assert result.shape[2] == 3
        
        # If grayscale, all channels should be equal
        if grayscale:
            assert np.all(result[:,:,0] == result[:,:,1])
            assert np.all(result[:,:,1] == result[:,:,2])
            
    finally:
        transforms.load_device_settings = original_load

def test_extreme_image_sizes():
    """Test transform functions with extreme (but valid) image sizes"""
    
    # Test with very small image
    tiny_image = np.random.randint(0, 256, (10, 10, 3), dtype=np.uint8)
    result = apply_unified_transforms(tiny_image, "test_device")
    assert result.shape == tiny_image.shape
    
    # Test with very wide image
    wide_image = np.random.randint(0, 256, (10, 500, 3), dtype=np.uint8)
    result = apply_unified_transforms(wide_image, "test_device")
    assert result.shape == wide_image.shape
    
    # Test with very tall image
    tall_image = np.random.randint(0, 256, (500, 10, 3), dtype=np.uint8)
    result = apply_unified_transforms(tall_image, "test_device")
    assert result.shape == tall_image.shape

def test_edge_pixel_values():
    """Test transforms with edge pixel values (0, 255)"""
    
    # All black image
    black_image = np.zeros((50, 50, 3), dtype=np.uint8)
    result = apply_unified_transforms(black_image, "test_device")
    assert isinstance(result, np.ndarray)
    
    # All white image
    white_image = np.full((50, 50, 3), 255, dtype=np.uint8)
    result = apply_unified_transforms(white_image, "test_device")
    assert isinstance(result, np.ndarray)
    
    # Checkerboard pattern
    checker = np.zeros((50, 50, 3), dtype=np.uint8)
    checker[::2, ::2] = 255
    checker[1::2, 1::2] = 255
    result = apply_unified_transforms(checker, "test_device")
    assert isinstance(result, np.ndarray)

def test_single_pixel_image():
    """Test with minimal valid image size"""
    pixel_image = np.array([[[255, 128, 64]]], dtype=np.uint8)
    
    # Should not crash even with 1x1 image
    result = apply_unified_transforms(pixel_image, "test_device")
    assert isinstance(result, np.ndarray)
    assert result.shape == (1, 1, 3)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
