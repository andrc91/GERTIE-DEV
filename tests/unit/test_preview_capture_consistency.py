import numpy as np
import pytest
import cv2
import sys
import os
from PIL import Image
from skimage.metrics import structural_similarity as ssim

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from shared.transforms import apply_unified_transforms, apply_unified_transforms_for_still, DEFAULT_SETTINGS

def create_realistic_test_image(width=640, height=480):
    """Create a realistic test image that simulates camera capture"""
    # Create an image with various patterns to test transforms thoroughly
    image = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Add vertical stripes (for horizontal flip testing)
    for i in range(0, width, 40):
        image[:, i:i+20, 0] = 200  # Red stripes
    
    # Add horizontal stripes (for vertical flip testing)  
    for i in range(0, height, 30):
        image[i:i+15, :, 1] = 200  # Green stripes
    
    # Add a corner pattern (for crop testing)
    image[0:50, 0:50, 2] = 255      # Blue corner
    image[-50:, -50:, :] = 255      # White corner
    
    # Add diagonal gradient (for rotation testing)
    for i in range(min(width, height)):
        image[i, i, :] = 128
    
    return image

def compare_images_ssim(img1, img2):
    """Compare two images using SSIM"""
    # Ensure images are same size
    if img1.shape != img2.shape:
        img2_resized = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
    else:
        img2_resized = img2
    
    # Convert to grayscale for SSIM
    if len(img1.shape) == 3:
        img1_gray = cv2.cvtColor(img1, cv2.COLOR_RGB2GRAY)
        img2_gray = cv2.cvtColor(img2_resized, cv2.COLOR_RGB2GRAY)
    else:
        img1_gray = img1
        img2_gray = img2_resized
    
    return ssim(img1_gray, img2_gray)

def test_preview_vs_capture_consistency_flip_vertical():
    """Test that preview and capture produce identical results with vertical flip"""
    image = create_realistic_test_image()
    
    # Settings with vertical flip
    test_settings = DEFAULT_SETTINGS.copy()
    test_settings['flip_vertical'] = True
    
    # Mock the settings loading
    from shared import transforms
    original_load = transforms.load_device_settings
    transforms.load_device_settings = lambda device_name: test_settings
    
    try:
        # Simulate preview transform (RGB output)
        preview_result = apply_unified_transforms(image, "test_device")
        
        # Simulate capture transform (BGR output, but we'll convert back)
        capture_result = apply_unified_transforms_for_still(image, "test_device")
        capture_rgb = cv2.cvtColor(capture_result, cv2.COLOR_BGR2RGB)
        
        # They should be identical
        ssim_score = compare_images_ssim(preview_result, capture_rgb)
        assert ssim_score >= 0.98, f"SSIM {ssim_score:.3f} < 0.98 for vertical flip"
        
    finally:
        transforms.load_device_settings = original_load

def test_preview_vs_capture_consistency_flip_horizontal():
    """Test that preview and capture produce identical results with horizontal flip"""
    image = create_realistic_test_image()
    
    test_settings = DEFAULT_SETTINGS.copy()
    test_settings['flip_horizontal'] = True
    
    from shared import transforms
    original_load = transforms.load_device_settings
    transforms.load_device_settings = lambda device_name: test_settings
    
    try:
        preview_result = apply_unified_transforms(image, "test_device")
        capture_result = apply_unified_transforms_for_still(image, "test_device")
        capture_rgb = cv2.cvtColor(capture_result, cv2.COLOR_BGR2RGB)
        
        ssim_score = compare_images_ssim(preview_result, capture_rgb)
        assert ssim_score >= 0.98, f"SSIM {ssim_score:.3f} < 0.98 for horizontal flip"
        
    finally:
        transforms.load_device_settings = original_load

def test_preview_vs_capture_consistency_both_flips():
    """Test consistency with both flips enabled"""
    image = create_realistic_test_image()
    
    test_settings = DEFAULT_SETTINGS.copy()
    test_settings['flip_horizontal'] = True
    test_settings['flip_vertical'] = True
    
    from shared import transforms
    original_load = transforms.load_device_settings
    transforms.load_device_settings = lambda device_name: test_settings
    
    try:
        preview_result = apply_unified_transforms(image, "test_device")
        capture_result = apply_unified_transforms_for_still(image, "test_device")
        capture_rgb = cv2.cvtColor(capture_result, cv2.COLOR_BGR2RGB)
        
        ssim_score = compare_images_ssim(preview_result, capture_rgb)
        assert ssim_score >= 0.98, f"SSIM {ssim_score:.3f} < 0.98 for both flips"
        
    finally:
        transforms.load_device_settings = original_load

def test_preview_vs_capture_consistency_crop():
    """Test consistency with cropping enabled"""
    image = create_realistic_test_image(200, 200)  # Smaller image for crop test
    
    test_settings = DEFAULT_SETTINGS.copy()
    test_settings['crop_enabled'] = True
    test_settings['crop_x'] = 20
    test_settings['crop_y'] = 20
    test_settings['crop_width'] = 100
    test_settings['crop_height'] = 100
    
    from shared import transforms
    original_load = transforms.load_device_settings
    transforms.load_device_settings = lambda device_name: test_settings
    
    try:
        preview_result = apply_unified_transforms(image, "test_device")
        capture_result = apply_unified_transforms_for_still(image, "test_device")
        capture_rgb = cv2.cvtColor(capture_result, cv2.COLOR_BGR2RGB)
        
        # Verify crop was applied
        assert preview_result.shape == (100, 100, 3), f"Preview shape {preview_result.shape} != (100, 100, 3)"
        assert capture_rgb.shape == (100, 100, 3), f"Capture shape {capture_rgb.shape} != (100, 100, 3)"
        
        ssim_score = compare_images_ssim(preview_result, capture_rgb)
        assert ssim_score >= 0.98, f"SSIM {ssim_score:.3f} < 0.98 for crop"
        
    finally:
        transforms.load_device_settings = original_load

def test_preview_vs_capture_consistency_rotation():
    """Test consistency with rotation"""
    image = create_realistic_test_image(100, 100)  # Square image for rotation
    
    test_settings = DEFAULT_SETTINGS.copy()
    test_settings['rotation'] = 90
    
    from shared import transforms
    original_load = transforms.load_device_settings
    transforms.load_device_settings = lambda device_name: test_settings
    
    try:
        preview_result = apply_unified_transforms(image, "test_device")
        capture_result = apply_unified_transforms_for_still(image, "test_device")
        capture_rgb = cv2.cvtColor(capture_result, cv2.COLOR_BGR2RGB)
        
        ssim_score = compare_images_ssim(preview_result, capture_rgb)
        assert ssim_score >= 0.98, f"SSIM {ssim_score:.3f} < 0.98 for rotation"
        
    finally:
        transforms.load_device_settings = original_load

def test_preview_vs_capture_consistency_complex():
    """Test consistency with multiple transforms applied"""
    image = create_realistic_test_image(200, 150)
    
    test_settings = DEFAULT_SETTINGS.copy()
    test_settings['crop_enabled'] = True
    test_settings['crop_x'] = 10
    test_settings['crop_y'] = 10
    test_settings['crop_width'] = 120
    test_settings['crop_height'] = 80
    test_settings['flip_horizontal'] = True
    test_settings['flip_vertical'] = True
    test_settings['rotation'] = 180
    
    from shared import transforms
    original_load = transforms.load_device_settings
    transforms.load_device_settings = lambda device_name: test_settings
    
    try:
        preview_result = apply_unified_transforms(image, "test_device")
        capture_result = apply_unified_transforms_for_still(image, "test_device")
        capture_rgb = cv2.cvtColor(capture_result, cv2.COLOR_BGR2RGB)
        
        ssim_score = compare_images_ssim(preview_result, capture_rgb)
        assert ssim_score >= 0.98, f"SSIM {ssim_score:.3f} < 0.98 for complex transforms"
        
    finally:
        transforms.load_device_settings = original_load

def test_brightness_histogram_consistency():
    """Test that brightness distribution is preserved between preview and capture"""
    image = create_realistic_test_image()
    
    # Settings with transforms that should NOT affect brightness
    test_settings = DEFAULT_SETTINGS.copy()
    test_settings['flip_horizontal'] = True
    test_settings['flip_vertical'] = True
    
    from shared import transforms
    original_load = transforms.load_device_settings
    transforms.load_device_settings = lambda device_name: test_settings
    
    try:
        preview_result = apply_unified_transforms(image, "test_device")
        capture_result = apply_unified_transforms_for_still(image, "test_device")
        capture_rgb = cv2.cvtColor(capture_result, cv2.COLOR_BGR2RGB)
        
        # Compare brightness histograms
        preview_gray = cv2.cvtColor(preview_result, cv2.COLOR_RGB2GRAY)
        capture_gray = cv2.cvtColor(capture_rgb, cv2.COLOR_RGB2GRAY)
        
        preview_hist = cv2.calcHist([preview_gray], [0], None, [256], [0, 256])
        capture_hist = cv2.calcHist([capture_gray], [0], None, [256], [0, 256])
        
        # Compare histograms using correlation
        correlation = cv2.compareHist(preview_hist, capture_hist, cv2.HISTCMP_CORREL)
        assert correlation >= 0.99, f"Histogram correlation {correlation:.3f} < 0.99"
        
    finally:
        transforms.load_device_settings = original_load

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
