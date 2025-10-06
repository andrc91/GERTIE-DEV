import pytest
import subprocess
from PIL import Image
import numpy as np
from skimage.metrics import structural_similarity as ssim
import os
import sys

def grab(p):
    return Image.open(p).convert("RGB")

def compare(a, b):
    a = np.array(a)
    b = np.array(b.resize(a.size))
    return ssim(a, b, channel_axis=2)

@pytest.mark.integration
def test_preview_matches_capture(tmp_path):
    """Test that preview frame matches captured still image"""
    p = tmp_path / "p.png"
    f = tmp_path / "f.jpg"
    
    # First check if the capture scripts exist
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    preview_script = os.path.join(project_root, "scripts", "capture_preview_frame.py")
    capture_script = os.path.join(project_root, "scripts", "trigger_capture.py")
    
    if not os.path.exists(preview_script):
        pytest.skip(f"Preview script not found: {preview_script}")
    if not os.path.exists(capture_script):
        pytest.skip(f"Capture script not found: {capture_script}")
    
    try:
        subprocess.check_call(["python3", preview_script, "--out", str(p)], timeout=30)
        subprocess.check_call(["python3", capture_script, "--out", str(f)], timeout=30)
        
        ssim_score = compare(grab(p), grab(f))
        assert ssim_score >= 0.98, f"SSIM score {ssim_score:.3f} below threshold 0.98"
        
    except subprocess.TimeoutExpired:
        pytest.fail("Capture scripts timed out")
    except subprocess.CalledProcessError as e:
        pytest.fail(f"Capture script failed: {e}")
