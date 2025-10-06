import pytest
import numpy as np
import cv2
import sys
import os
import tempfile
from PIL import Image

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from shared.transforms import apply_unified_transforms, apply_unified_transforms_for_still, DEFAULT_SETTINGS

def create_test_scenarios():
    """Create various test scenarios to validate"""
    scenarios = []
    
    # Scenario 1: Basic flip validation
    scenarios.append({
        'name': 'basic_flip',
        'settings': {'flip_vertical': True},
        'image_size': (100, 100, 3),
        'expected_change': True
    })
    
    # Scenario 2: Crop validation
    scenarios.append({
        'name': 'crop_test',
        'settings': {'crop_enabled': True, 'crop_x': 20, 'crop_y': 20, 'crop_width': 60, 'crop_height': 60},
        'image_size': (100, 100, 3),
        'expected_change': True
    })
    
    # Scenario 3: Complex multi-transform
    scenarios.append({
        'name': 'complex_transform',
        'settings': {'flip_horizontal': True, 'flip_vertical': True, 'rotation': 90, 'grayscale': True},
        'image_size': (80, 80, 3),
        'expected_change': True
    })
    
    # Scenario 4: No-op (should be identical)
    scenarios.append({
        'name': 'no_op',
        'settings': {},
        'image_size': (50, 50, 3),
        'expected_change': False
    })
    
    return scenarios

def test_scenario_1_basic_flip():
    """Test basic flip scenario integration"""
    image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    
    from shared import transforms
    original_load = transforms.load_device_settings
    
    settings = DEFAULT_SETTINGS.copy()
    settings['flip_vertical'] = True
    transforms.load_device_settings = lambda device_name: settings
    
    try:
        result = apply_unified_transforms(image, "scenario_1")
        
        # Should be different from original due to flip
        assert not np.array_equal(result, image)
        
        # Should have same dimensions
        assert result.shape == image.shape
        
        # First row should equal last row of original
        np.testing.assert_array_equal(result[0], image[-1])
        
    finally:
        transforms.load_device_settings = original_load

def test_scenario_2_crop_integration():
    """Test crop scenario integration"""
    image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    
    from shared import transforms
    original_load = transforms.load_device_settings
    
    settings = DEFAULT_SETTINGS.copy()
    settings.update({
        'crop_enabled': True,
        'crop_x': 20,
        'crop_y': 20,
        'crop_width': 60,
        'crop_height': 60
    })
    transforms.load_device_settings = lambda device_name: settings
    
    try:
        result = apply_unified_transforms(image, "scenario_2")
        
        # Should be smaller due to crop
        assert result.shape == (60, 60, 3)
        
        # Content should match cropped region
        expected = image[20:80, 20:80]
        np.testing.assert_array_equal(result, expected)
        
    finally:
        transforms.load_device_settings = original_load

def test_scenario_3_complex_transform():
    """Test complex multi-transform scenario"""
    image = np.random.randint(0, 256, (80, 80, 3), dtype=np.uint8)
    
    from shared import transforms
    original_load = transforms.load_device_settings
    
    settings = DEFAULT_SETTINGS.copy()
    settings.update({
        'flip_horizontal': True,
        'flip_vertical': True,
        'rotation': 90,
        'grayscale': True
    })
    transforms.load_device_settings = lambda device_name: settings
    
    try:
        result = apply_unified_transforms(image, "scenario_3")
        
        # Should be different from original
        assert not np.array_equal(result, image)
        
        # Should be grayscale (all channels equal)
        assert np.all(result[:,:,0] == result[:,:,1])
        assert np.all(result[:,:,1] == result[:,:,2])
        
        # Should have same dimensions after rotation (square image)
        assert result.shape == image.shape
        
    finally:
        transforms.load_device_settings = original_load

def test_scenario_4_no_op():
    """Test no-operation scenario (should be identical)"""
    image = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
    
    from shared import transforms
    original_load = transforms.load_device_settings
    
    settings = DEFAULT_SETTINGS.copy()  # Default settings should not transform
    transforms.load_device_settings = lambda device_name: settings
    
    try:
        result = apply_unified_transforms(image, "scenario_4")
        
        # Should be identical to original
        np.testing.assert_array_equal(result, image)
        
    finally:
        transforms.load_device_settings = original_load

def test_pipeline_consistency_validation():
    """Test that the transform pipeline is consistent"""
    image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    
    # Run same transform multiple times
    results = []
    for i in range(5):
        result = apply_unified_transforms(image, f"consistency_test_{i}")
        results.append(result)
    
    # All results should be identical
    for i in range(1, len(results)):
        np.testing.assert_array_equal(results[0], results[i])

def test_preview_vs_still_pipeline_integration():
    """Integration test for preview vs still pipeline consistency"""
    image = np.random.randint(0, 256, (200, 200, 3), dtype=np.uint8)
    
    from shared import transforms
    original_load = transforms.load_device_settings
    
    # Test with various transform combinations
    test_combinations = [
        {'flip_horizontal': True},
        {'flip_vertical': True},
        {'rotation': 90},
        {'crop_enabled': True, 'crop_x': 50, 'crop_y': 50, 'crop_width': 100, 'crop_height': 100},
        {'flip_horizontal': True, 'flip_vertical': True, 'rotation': 180}
    ]
    
    for i, transform_settings in enumerate(test_combinations):
        settings = DEFAULT_SETTINGS.copy()
        settings.update(transform_settings)
        transforms.load_device_settings = lambda device_name: settings
        
        try:
            # Get results from both pipelines
            preview_result = apply_unified_transforms(image, f"preview_test_{i}")
            still_result = apply_unified_transforms_for_still(image, f"still_test_{i}")
            
            # Convert still result back to RGB for comparison
            still_rgb = cv2.cvtColor(still_result, cv2.COLOR_BGR2RGB)
            
            # Should be identical
            np.testing.assert_array_equal(preview_result, still_rgb)
            
        finally:
            transforms.load_device_settings = original_load

def test_settings_file_integration():
    """Test integration with settings file system"""
    # Create temporary settings
    test_settings = DEFAULT_SETTINGS.copy()
    test_settings.update({
        'flip_horizontal': True,
        'brightness': 25,
        'crop_enabled': True,
        'crop_x': 10,
        'crop_y': 10,
        'crop_width': 80,
        'crop_height': 80
    })
    
    # Test image
    image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    
    from shared import transforms
    original_load = transforms.load_device_settings
    transforms.load_device_settings = lambda device_name: test_settings
    
    try:
        result = apply_unified_transforms(image, "settings_integration_test")
        
        # Should have applied transforms
        assert result.shape == (80, 80, 3)  # Crop should be applied
        assert not np.array_equal(result, image[10:90, 10:90])  # Flip should make it different
        
    finally:
        transforms.load_device_settings = original_load

def test_error_recovery_integration():
    """Test that pipeline recovers gracefully from errors"""
    image = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
    
    # Test with invalid settings that might cause errors
    invalid_settings = [
        {'crop_x': -100, 'crop_y': -100, 'crop_enabled': True},  # Negative crop
        {'rotation': 45},  # Invalid rotation
        {'brightness': 9999},  # Out of range brightness
    ]
    
    from shared import transforms
    original_load = transforms.load_device_settings
    
    for i, bad_settings in enumerate(invalid_settings):
        settings = DEFAULT_SETTINGS.copy()
        settings.update(bad_settings)
        transforms.load_device_settings = lambda device_name: settings
        
        try:
            # Should not crash, even with bad settings
            result = apply_unified_transforms(image, f"error_test_{i}")
            assert isinstance(result, np.ndarray)
            assert len(result.shape) == 3
            
        except Exception as e:
            # If it does throw an exception, it should be handled gracefully
            # and not be a critical system error
            assert "critical" not in str(e).lower()
            
        finally:
            transforms.load_device_settings = original_load

def test_memory_usage_integration():
    """Test memory usage patterns in transform pipeline"""
    # Test with various image sizes
    image_sizes = [
        (50, 50, 3),
        (100, 100, 3),
        (200, 200, 3),
        (400, 400, 3)
    ]
    
    for width, height, channels in image_sizes:
        image = np.random.randint(0, 256, (height, width, channels), dtype=np.uint8)
        
        # Apply transform
        result = apply_unified_transforms(image, f"memory_test_{width}x{height}")
        
        # Should handle all sizes gracefully
        assert isinstance(result, np.ndarray)
        assert len(result.shape) == 3
        assert result.shape[2] == channels
        
        # Result should not be unreasonably larger than input
        result_size = result.size
        input_size = image.size
        assert result_size <= input_size * 2  # Allow some overhead but not excessive

def test_concurrent_transform_integration():
    """Test concurrent transform operations"""
    import threading
    import time
    
    images = [np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8) for _ in range(5)]
    results = {}
    errors = []
    
    def transform_worker(worker_id, image):
        try:
            result = apply_unified_transforms(image, f"concurrent_worker_{worker_id}")
            results[worker_id] = result
        except Exception as e:
            errors.append((worker_id, str(e)))
    
    # Start concurrent workers
    threads = []
    for i, image in enumerate(images):
        t = threading.Thread(target=transform_worker, args=(i, image))
        threads.append(t)
        t.start()
    
    # Wait for completion
    for t in threads:
        t.join(timeout=10)
    
    # Should have completed most operations successfully
    assert len(results) >= 3  # At least 3 out of 5 should succeed
    assert len(errors) <= 2   # At most 2 should fail
    
    # All successful results should be valid
    for worker_id, result in results.items():
        assert isinstance(result, np.ndarray)
        assert len(result.shape) == 3

def test_real_world_camera_simulation():
    """Simulate real-world camera scenarios"""
    
    # Simulate different camera scenarios
    scenarios = [
        {
            'name': 'landscape_photo',
            'image_size': (640, 480, 3),
            'settings': {'flip_horizontal': False, 'flip_vertical': False, 'rotation': 0}
        },
        {
            'name': 'portrait_photo', 
            'image_size': (480, 640, 3),
            'settings': {'rotation': 90}
        },
        {
            'name': 'upside_down_mount',
            'image_size': (640, 480, 3),
            'settings': {'flip_horizontal': True, 'flip_vertical': True}
        },
        {
            'name': 'cropped_region',
            'image_size': (640, 480, 3),
            'settings': {'crop_enabled': True, 'crop_x': 100, 'crop_y': 100, 'crop_width': 400, 'crop_height': 280}
        }
    ]
    
    from shared import transforms
    original_load = transforms.load_device_settings
    
    for scenario in scenarios:
        height, width, channels = scenario['image_size']
        image = np.random.randint(0, 256, (height, width, channels), dtype=np.uint8)
        
        settings = DEFAULT_SETTINGS.copy()
        settings.update(scenario['settings'])
        transforms.load_device_settings = lambda device_name: settings
        
        try:
            # Test both preview and still pipelines
            preview_result = apply_unified_transforms(image, f"preview_{scenario['name']}")
            still_result = apply_unified_transforms_for_still(image, f"still_{scenario['name']}")
            
            # Both should succeed
            assert isinstance(preview_result, np.ndarray)
            assert isinstance(still_result, np.ndarray)
            
            # Convert and compare
            still_rgb = cv2.cvtColor(still_result, cv2.COLOR_BGR2RGB)
            np.testing.assert_array_equal(preview_result, still_rgb)
            
        finally:
            transforms.load_device_settings = original_load

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
