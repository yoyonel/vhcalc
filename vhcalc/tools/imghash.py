import binascii
from typing import Final

import imagehash
import numpy as np
from imagehash import ImageHash
from PIL import Image

FRAME_SIZE: Final[int] = 32


def imghash_to_bytes(imghash: ImageHash) -> bytes:
    """
    >>> import numpy as np
    >>> imghash_to_bytes(ImageHash(np.array([\
        np.array([ True,  True, False,  True, False,  True, False,  True]), \
        np.array([False, False, False, False, False, False, False, False]), \
        np.array([False, False, False, False, False, False, False, False]), \
        np.array([False, False, False, False, False, False, False, False]), \
        np.array([False, False, False, False, False, False, False, False]), \
        np.array([False, False, False, False, False, False, False, False]), \
        np.array([False, False, False, False, False, False, False, False]), \
        np.array([False, False, False, False, False, False, False, False])])))
    b'\\xd5\\x00\\x00\\x00\\x00\\x00\\x00\\x00'
    """
    return binascii.a2b_hex(str(imghash))


def rawframe_to_imghash(
    raw_frame: bytes,
    frame_width: int = FRAME_SIZE,
    frame_height: int = FRAME_SIZE,
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
    return imagehash.phash(
        Image.fromarray(
            # https://docs.scipy.org/doc/numpy-1.14.0/reference/generated/numpy.frombuffer.html
            np.frombuffer(
                raw_frame, dtype=np.uint8, count=frame_width * frame_height
            ).reshape(frame_width, frame_height)
        )
    )
