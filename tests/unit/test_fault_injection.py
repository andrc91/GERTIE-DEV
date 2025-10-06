import numpy as np
import pytest
import cv2
import sys
import os
from unittest.mock import patch, MagicMock
import tempfile
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from shared.transforms import (
    apply_unified_transforms, 
    apply_unified_transforms_for_still,
    load_device_settings,
    save_device_settings,
    DEFAULT_SETTINGS
)

def create_test_image():
    """Create standard test image"""
    return np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)

def test_file_system_unavailable():
    """Test behavior when file system operations fail"""
    
    with patch('builtins.open', side_effect=OSError("File system unavailable")):
        # Should use default settings when file load fails
        settings = load_device_settings("test_device")
        assert settings == DEFAULT_SETTINGS
        
        # Should handle save failures gracefully
        result = save_device_settings("test_device", settings)
        assert result == False

def test_corrupted_settings_file():
    """Test behavior with corrupted JSON settings"""
    
    # Create temporary corrupted file
    with tempfile.NamedTemporaryFile(mode='w', suffix='_settings.json', delete=False) as f:
        f.write("{ invalid json content }")
        temp_file = f.name
    
    try:
        # Mock the settings file path
        with patch('shared.transforms.load_device_settings') as mock_load:
            mock_load.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
            
            # Should fall back to defaults when JSON is corrupted
            image = create_test_image()
            result = apply_unified_transforms(image, "test_device")
            assert isinstance(result, np.ndarray)
            
    finally:
        os.unlink(temp_file)

def test_opencv_import_failure():
    """Test behavior when OpenCV operations fail"""
    
    image = create_test_image()
    
    # Mock cv2.flip to fail
    with patch('cv2.flip', side_effect=Exception("OpenCV error")):
        with patch('shared.transforms.load_device_settings') as mock_load:
            test_settings = DEFAULT_SETTINGS.copy()
            test_settings['flip_horizontal'] = True
            mock_load.return_value = test_settings
            
            # Should handle OpenCV failures gracefully
            result = apply_unified_transforms(image, "test_device")
            # Should fall back to original image
            assert isinstance(result, np.ndarray)

def test_memory_allocation_failure():
    """Test behavior with simulated memory issues"""
    
    image = create_test_image()
    
    # Mock numpy operations to fail (simulating memory issues)
    with patch('numpy.array', side_effect=MemoryError("Out of memory")):
        # Should handle memory errors gracefully
        result = apply_unified_transforms(image, "test_device")
        # Should return something (possibly original or error fallback)
        assert result is not None

def test_invalid_device_name():
    """Test with various invalid device names"""
    
    image = create_test_image()
    
    invalid_names = [
        "",           # Empty string
        None,         # None value
        123,          # Number
        "very_long_device_name_that_exceeds_normal_limits_" * 10,  # Very long name
        "device/with/slashes",  # Path-like name
        "device with spaces",   # Spaces
        "device\nwith\nnewlines",  # Newlines
    ]
    
    for invalid_name in invalid_names:
        # Should not crash with invalid device names
        try:
            result = apply_unified_transforms(image, invalid_name)
            assert isinstance(result, np.ndarray)
        except Exception as e:
            # If it throws an exception, it should be handled gracefully
            assert "device" in str(e).lower() or "name" in str(e).lower()

def test_malformed_settings():
    """Test with various malformed settings dictionaries"""
    
    image = create_test_image()
    
    malformed_settings = [
        {},  # Empty settings
        {"invalid_key": "invalid_value"},  # Unknown keys
        {"flip_horizontal": "not_boolean"},  # Wrong type
        {"crop_x": "not_integer"},  # Wrong type for numeric field
        {"rotation": 45},  # Invalid rotation value
        {"brightness": 1000},  # Out of range value
        None,  # None instead of dict
    ]
    
    from shared import transforms
    original_load = transforms.load_device_settings
    
    for bad_settings in malformed_settings:
        transforms.load_device_settings = lambda device_name: bad_settings
        
        try:
            result = apply_unified_transforms(image, "test_device")
            # Should either work or fail gracefully
            assert isinstance(result, np.ndarray)
        except (TypeError, ValueError, AttributeError) as e:
            # Expected exceptions for malformed data
            pass
        finally:
            transforms.load_device_settings = original_load

def test_extremely_large_crop():
    """Test with crop dimensions larger than image"""
    
    image = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
    
    # Settings with crop larger than image
    from shared import transforms
    original_load = transforms.load_device_settings
    
    oversized_settings = DEFAULT_SETTINGS.copy()
    oversized_settings.update({
        'crop_enabled': True,
        'crop_x': 0,
        'crop_y': 0,
        'crop_width': 1000,  # Much larger than 50px image
        'crop_height': 1000
    })
    
    transforms.load_device_settings = lambda device_name: oversized_settings
    
    try:
        result = apply_unified_transforms(image, "test_device")
        # Should handle oversized crop gracefully
        assert isinstance(result, np.ndarray)
        # Should not be larger than original
        assert result.shape[0] <= image.shape[0]
        assert result.shape[1] <= image.shape[1]
    finally:
        transforms.load_device_settings = original_load

def test_negative_crop_values():
    """Test with negative crop coordinates"""
    
    image = create_test_image()
    
    from shared import transforms
    original_load = transforms.load_device_settings
    
    negative_settings = DEFAULT_SETTINGS.copy()
    negative_settings.update({
        'crop_enabled': True,
        'crop_x': -50,    # Negative coordinates
        'crop_y': -30,
        'crop_width': 50,
        'crop_height': 50
    })
    
    transforms.load_device_settings = lambda device_name: negative_settings
    
    try:
        result = apply_unified_transforms(image, "test_device")
        # Should handle negative coordinates gracefully
        assert isinstance(result, np.ndarray)
    finally:
        transforms.load_device_settings = original_load

def test_concurrent_transform_calls():
    """Test multiple concurrent transform operations"""
    
    import threading
    import time
    
    image = create_test_image()
    results = []
    errors = []
    
    def transform_worker(worker_id):
        try:
            for i in range(5):  # Multiple calls per worker
                result = apply_unified_transforms(image, f"worker_{worker_id}")
                results.append((worker_id, i, result.shape))
                time.sleep(0.01)  # Small delay
        except Exception as e:
            errors.append((worker_id, str(e)))
    
    # Start multiple worker threads
    threads = []
    for i in range(3):
        t = threading.Thread(target=transform_worker, args=(i,))
        threads.append(t)
        t.start()
    
    # Wait for all threads to complete
    for t in threads:
        t.join(timeout=10)
    
    # Should have some successful results
    assert len(results) > 0
    # Should not have critical errors (some minor ones might be OK)
    assert len(errors) < len(results)

def test_resource_exhaustion_simulation():
    """Test behavior under simulated resource exhaustion"""
    
    image = create_test_image()
    
    # Simulate various resource exhaustion scenarios
    with patch('cv2.cvtColor', side_effect=Exception("GPU memory exhausted")):
        # Should handle GPU/OpenCV resource issues
        result = apply_unified_transforms(image, "test_device")
        assert isinstance(result, np.ndarray)
    
    with patch('numpy.copy', side_effect=MemoryError("System memory exhausted")):
        # Should handle system memory issues  
        result = apply_unified_transforms(image, "test_device")
        assert result is not None

def test_settings_file_permissions():
    """Test behavior when settings file has permission issues"""
    
    with patch('builtins.open', side_effect=PermissionError("Permission denied")):
        # Should handle permission errors gracefully
        settings = load_device_settings("restricted_device")
        assert settings == DEFAULT_SETTINGS
        
        # Should handle save permission errors
        result = save_device_settings("restricted_device", settings)
        assert result == False

def test_disk_full_simulation():
    """Test behavior when disk is full during save operations"""
    
    settings = DEFAULT_SETTINGS.copy()
    
    with patch('builtins.open', side_effect=OSError("No space left on device")):
        # Should handle disk full errors gracefully
        result = save_device_settings("test_device", settings)
        assert result == False

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
