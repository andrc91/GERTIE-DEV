import numpy as np
import pytest
import time
import sys
import os
from pytest import mark

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from shared.transforms import (
    apply_unified_transforms,
    apply_unified_transforms_for_still, 
    apply_crop_rgb,
    apply_rotation_rgb,
    DEFAULT_SETTINGS
)

def create_benchmark_image(width=640, height=480):
    """Create a realistic benchmark image similar to camera output"""
    # Create image with realistic camera-like content
    image = np.random.randint(50, 200, (height, width, 3), dtype=np.uint8)
    
    # Add some structure (simulate real scene)
    # Horizontal lines (simulate horizons, edges)
    for i in range(0, height, 30):
        image[i:i+2, :, :] = 180
    
    # Vertical lines  
    for i in range(0, width, 40):
        image[:, i:i+2, :] = 160
    
    return image

def create_high_res_image():
    """Create high resolution image similar to still capture"""
    return create_benchmark_image(4608, 2592)

def create_preview_image():
    """Create preview resolution image"""
    return create_benchmark_image(640, 480)

# Basic transform performance tests

def benchmark_wrapper(func):
    """Simple benchmark wrapper when pytest-benchmark is not available"""
    def wrapper():
        start_time = time.time()
        result = func()
        end_time = time.time()
        print(f"Execution time: {end_time - start_time:.4f}s")
        return result
    return wrapper

def test_no_transform_performance():
    """Benchmark baseline performance with no transforms"""
    image = create_preview_image()
    
    @benchmark_wrapper
    def no_transform():
        return apply_unified_transforms(image, "benchmark_device")
    
    result = no_transform()
    assert isinstance(result, np.ndarray)
    assert result.shape == image.shape

def test_horizontal_flip_performance():
    """Benchmark horizontal flip performance"""
    image = create_preview_image()
    
    from shared import transforms
    original_load = transforms.load_device_settings
    
    flip_settings = DEFAULT_SETTINGS.copy()
    flip_settings['flip_horizontal'] = True
    transforms.load_device_settings = lambda device_name: flip_settings
    
    try:
        @benchmark_wrapper
        def flip_transform():
            return apply_unified_transforms(image, "benchmark_device")
        
        result = flip_transform()
        assert isinstance(result, np.ndarray)
    finally:
        transforms.load_device_settings = original_load

def test_vertical_flip_performance():
    """Benchmark vertical flip performance"""
    image = create_preview_image()
    
    from shared import transforms
    original_load = transforms.load_device_settings
    
    flip_settings = DEFAULT_SETTINGS.copy()
    flip_settings['flip_vertical'] = True
    transforms.load_device_settings = lambda device_name: flip_settings
    
    try:
        @benchmark_wrapper
        def flip_transform():
            return apply_unified_transforms(image, "benchmark_device")
        
        result = flip_transform()
        assert isinstance(result, np.ndarray)
    finally:
        transforms.load_device_settings = original_load

def test_both_flips_performance():
    """Benchmark performance with both flips enabled"""
    image = create_preview_image()
    
    from shared import transforms
    original_load = transforms.load_device_settings
    
    flip_settings = DEFAULT_SETTINGS.copy()
    flip_settings['flip_horizontal'] = True
    flip_settings['flip_vertical'] = True
    transforms.load_device_settings = lambda device_name: flip_settings
    
    try:
        @benchmark_wrapper
        def both_flips():
            return apply_unified_transforms(image, "benchmark_device")
        
        result = both_flips()
        assert isinstance(result, np.ndarray)
    finally:
        transforms.load_device_settings = original_load

def test_rotation_90_performance():
    """Benchmark 90-degree rotation performance"""
    image = create_preview_image()
    
    from shared import transforms
    original_load = transforms.load_device_settings
    
    rotation_settings = DEFAULT_SETTINGS.copy()
    rotation_settings['rotation'] = 90
    transforms.load_device_settings = lambda device_name: rotation_settings
    
    try:
        @benchmark_wrapper
        def rotate_90():
            return apply_unified_transforms(image, "benchmark_device")
        
        result = rotate_90()
        assert isinstance(result, np.ndarray)
    finally:
        transforms.load_device_settings = original_load

def test_rotation_180_performance():
    """Benchmark 180-degree rotation performance"""
    image = create_preview_image()
    
    from shared import transforms
    original_load = transforms.load_device_settings
    
    rotation_settings = DEFAULT_SETTINGS.copy()
    rotation_settings['rotation'] = 180
    transforms.load_device_settings = lambda device_name: rotation_settings
    
    try:
        @benchmark_wrapper
        def rotate_180():
            return apply_unified_transforms(image, "benchmark_device")
        
        result = rotate_180()
        assert isinstance(result, np.ndarray)
    finally:
        transforms.load_device_settings = original_load

def test_small_crop_performance():
    """Benchmark small crop performance"""
    image = create_preview_image()
    
    from shared import transforms
    original_load = transforms.load_device_settings
    
    crop_settings = DEFAULT_SETTINGS.copy()
    crop_settings.update({
        'crop_enabled': True,
        'crop_x': 100,
        'crop_y': 100,
        'crop_width': 200,
        'crop_height': 200
    })
    transforms.load_device_settings = lambda device_name: crop_settings
    
    try:
        @benchmark_wrapper
        def small_crop():
            return apply_unified_transforms(image, "benchmark_device")
        
        result = small_crop()
        assert isinstance(result, np.ndarray)
    finally:
        transforms.load_device_settings = original_load

def test_large_crop_performance():
    """Benchmark large crop performance"""
    image = create_preview_image()
    
    from shared import transforms
    original_load = transforms.load_device_settings
    
    crop_settings = DEFAULT_SETTINGS.copy()
    crop_settings.update({
        'crop_enabled': True,
        'crop_x': 50,
        'crop_y': 50,
        'crop_width': 500,
        'crop_height': 350
    })
    transforms.load_device_settings = lambda device_name: crop_settings
    
    try:
        @benchmark_wrapper
        def large_crop():
            return apply_unified_transforms(image, "benchmark_device")
        
        result = large_crop()
        assert isinstance(result, np.ndarray)
    finally:
        transforms.load_device_settings = original_load

def test_complex_transform_performance():
    """Benchmark complex multi-transform performance"""
    image = create_preview_image()
    
    from shared import transforms
    original_load = transforms.load_device_settings
    
    complex_settings = DEFAULT_SETTINGS.copy()
    complex_settings.update({
        'crop_enabled': True,
        'crop_x': 50,
        'crop_y': 50,
        'crop_width': 400,
        'crop_height': 300,
        'flip_horizontal': True,
        'flip_vertical': True,
        'rotation': 90,
        'grayscale': True
    })
    transforms.load_device_settings = lambda device_name: complex_settings
    
    try:
        @benchmark_wrapper
        def complex_transform():
            return apply_unified_transforms(image, "benchmark_device")
        
        result = complex_transform()
        assert isinstance(result, np.ndarray)
    finally:
        transforms.load_device_settings = original_load

def test_high_resolution_performance():
    """Benchmark high resolution image performance"""
    image = create_high_res_image()
    
    @benchmark_wrapper
    def high_res_transform():
        return apply_unified_transforms_for_still(image, "benchmark_device")
    
    result = high_res_transform()
    assert isinstance(result, np.ndarray)

def test_preview_vs_still_performance_comparison():
    """Compare preview vs still capture transform performance"""
    preview_image = create_preview_image()
    high_res_image = create_high_res_image()
    
    # Time preview transform
    start_time = time.time()
    preview_result = apply_unified_transforms(preview_image, "benchmark_device")
    preview_time = time.time() - start_time
    
    # Time still transform
    @benchmark_wrapper
    def still_transform():
        return apply_unified_transforms_for_still(high_res_image, "benchmark_device")
    
    still_result = still_transform()
    
    # Basic validation
    assert isinstance(preview_result, np.ndarray)
    assert isinstance(still_result, np.ndarray)
    
    # Performance should scale reasonably with resolution
    # High res image is ~36x larger (4608*2592 vs 640*480 = 36.45x)
    # Transform time should not be proportionally worse
    print(f"Preview transform time: {preview_time:.4f}s")

# Memory usage tests
def test_memory_efficiency():
    """Test that transforms don't use excessive memory"""
    import tracemalloc
    
    image = create_preview_image()
    
    tracemalloc.start()
    
    # Apply transform
    result = apply_unified_transforms(image, "memory_test_device")
    
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    # Memory usage should be reasonable (less than 100MB for preview image)
    peak_mb = peak / (1024 * 1024)
    assert peak_mb < 100, f"Peak memory usage too high: {peak_mb:.1f}MB"
    
    # Result should be valid
    assert isinstance(result, np.ndarray)

def test_transform_latency_consistency():
    """Test that transform latency is consistent across multiple calls"""
    image = create_preview_image()
    
    times = []
    for i in range(10):
        start_time = time.time()
        result = apply_unified_transforms(image, "latency_test_device")
        end_time = time.time()
        times.append(end_time - start_time)
        
        assert isinstance(result, np.ndarray)
    
    # Calculate timing statistics
    avg_time = sum(times) / len(times)
    max_time = max(times)
    min_time = min(times)
    
    # Latency should be consistent (max shouldn't be more than 3x min)
    consistency_ratio = max_time / min_time if min_time > 0 else float('inf')
    assert consistency_ratio < 3.0, f"Inconsistent latency: {consistency_ratio:.2f}x variation"
    
    # Average latency should be reasonable (less than 100ms for preview)
    assert avg_time < 0.1, f"Average latency too high: {avg_time:.3f}s"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--benchmark-only"])
