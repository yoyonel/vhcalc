import numpy as np
import pytest
from PIL import Image
from imagehash import ImageHash, phash

from vhcalc.tools.imghash import rawframe_to_imghash, FRAME_SIZE


def test_rawframe_to_imghash_integration():
    """
    Test the integration of numpy, Pillow, and imagehash.
    This ensures that recent updates to these libraries do not break the core hashing functionality.
    """
    # Create a random raw frame
    frame_width = FRAME_SIZE
    frame_height = FRAME_SIZE
    frame_size = frame_width * frame_height

    # Generate random bytes
    rng = np.random.default_rng(seed=42)
    raw_frame_data = rng.bytes(frame_size)

    # Calculate hash
    result_hash = rawframe_to_imghash(raw_frame_data, frame_width, frame_height, phash)

    # Verify result type
    assert isinstance(result_hash, ImageHash)

    # Verify the hash is not empty/zero (unless by extreme chance)
    # Convert to hex string
    hex_hash = str(result_hash)
    assert len(hex_hash) > 0

    # Manually reconstruct to verify logic
    arr = np.frombuffer(raw_frame_data, dtype=np.uint8).reshape((frame_width, frame_height))
    img = Image.fromarray(arr)
    expected_hash = phash(img)

    assert result_hash == expected_hash

def test_numpy_pillow_compatibility():
    """
    Explicitly test Numpy array to PIL Image conversion, as this is a common failure point
    during major version upgrades.
    """
    # Create a numpy array
    arr = np.zeros((100, 100), dtype=np.uint8)
    arr[25:75, 25:75] = 255

    # Convert to PIL Image
    img = Image.fromarray(arr)

    # Basic checks
    assert img.size == (100, 100)
    assert img.mode == 'L'

    # Check pixel values
    assert img.getpixel((0, 0)) == 0
    assert img.getpixel((50, 50)) == 255
