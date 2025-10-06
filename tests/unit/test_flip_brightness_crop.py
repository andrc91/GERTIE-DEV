import numpy as np
import pytest
from PIL import Image, ImageEnhance

def make_img():
    return Image.fromarray(np.tile(np.arange(0, 256, 32, dtype=np.uint8), (8, 1)))

def test_vertical_flip():
    img = make_img()
    flipped = img.transpose(Image.FLIP_TOP_BOTTOM)
    assert np.all(np.array(img)[0] == np.array(flipped)[-1])

def test_brightness_up_down():
    img = make_img().convert("RGB")
    mean = np.array(img).mean()
    bright = ImageEnhance.Brightness(img).enhance(1.5)
    dark = ImageEnhance.Brightness(img).enhance(0.5)
    assert np.array(bright).mean() > mean
    assert np.array(dark).mean() < mean

def test_crop_region():
    img = make_img()
    cropped = img.crop((0, 0, 2, 2))
    assert cropped.size == (2, 2)
