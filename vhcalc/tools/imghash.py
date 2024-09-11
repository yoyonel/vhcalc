import binascii
from typing import Callable, Final

import imagehash
import numpy as np
from imagehash import ImageHash
from PIL import Image

FRAME_SIZE: Final[int] = 32


def imghash_to_bytes(imghash: ImageHash) -> bytes:
    """
    >>> import numpy as np
    >>> img_hash = ImageHash(np.array([\
        np.array([ True,  True, False,  True, False,  True, False,  True]), \
        np.array([False, False, False, False, False, False, False, False]), \
        np.array([False, False, False, False, False, False, False, False]), \
        np.array([False, False, False, False, False, False, False, False]), \
        np.array([False, False, False, False, False, False, False, False]), \
        np.array([False, False, False, False, False, False, False, False]), \
        np.array([False, False, False, False, False, False, False, False]), \
        np.array([False, False, False, False, False, False, False, False])]))
    >>> str(img_hash)
    'd500000000000000'
    >>> imghash_to_bytes(img_hash)
    b'\\xd5\\x00\\x00\\x00\\x00\\x00\\x00\\x00'
    """
    bin_array_to_hex = str(imghash)
    return binascii.a2b_hex(bin_array_to_hex)


def bytes_to_imghash(raw_bytes: bytes) -> ImageHash:
    """

    Args:
        raw_bytes (bytes): raw bytes to hash

    Returns:
        ImageHash: Image hash representation of binaries input

    Examples:
        >>> import numpy as np
        >>> img_hash = ImageHash(np.array([\
            np.array([ True,  True, False,  True, False,  True, False,  True]), \
            np.array([False, False, False, False, False, False, False, False]), \
            np.array([False, False, False, False, False, False, False, False]), \
            np.array([False, False, False, False, False, False, False, False]), \
            np.array([False, False, False, False, False, False, False, False]), \
            np.array([False, False, False, False, False, False, False, False]), \
            np.array([False, False, False, False, False, False, False, False]), \
            np.array([False, False, False, False, False, False, False, False])]))
        >>> imghash_reconstructed = bytes_to_imghash(b'\\xd5\\x00\\x00\\x00\\x00\\x00\\x00\\x00')
        >>> str(imghash_reconstructed)
        'd500000000000000'
    """
    return imagehash.hex_to_hash(binascii.b2a_hex(raw_bytes).decode())


def rawframe_to_imghash(
    raw_frame: bytes,
    frame_width: int = FRAME_SIZE,
    frame_height: int = FRAME_SIZE,
    fn_imagehash: Callable[[Image.Image], ImageHash] = imagehash.phash,
) -> imagehash.ImageHash:
    """Apply a Perceptual Hash computation on raw image frame.

    >>> rawframe_to_imghash(bytearray((128,)*(FRAME_SIZE**2)))
    array([[ True, False, False, False, False, False, False, False],
           [False, False, False, False, False, False, False, False],
           [False, False, False, False, False, False, False, False],
           [False, False, False, False, False, False, False, False],
           [False, False, False, False, False, False, False, False],
           [False, False, False, False, False, False, False, False],
           [False, False, False, False, False, False, False, False],
           [False, False, False, False, False, False, False, False]])
    """
    return fn_imagehash(
        Image.fromarray(
            # https://docs.scipy.org/doc/numpy-1.14.0/reference/generated/numpy.frombuffer.html
            np.frombuffer(
                raw_frame, dtype=np.uint8, count=frame_width * frame_height
            ).reshape(frame_width, frame_height)
        )
    )
