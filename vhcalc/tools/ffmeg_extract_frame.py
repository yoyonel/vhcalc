"""
"""
from typing import Final

import imagehash
import numpy as np
from PIL import Image

FRAME_SIZE: Final[int] = 32


def rawframe_to_imghash(
    raw_frame: bytes,
    frame_width: int = FRAME_SIZE,
    frame_height: int = FRAME_SIZE,
) -> imagehash.ImageHash:
    return imagehash.phash(
        Image.fromarray(
            # https://docs.scipy.org/doc/numpy-1.14.0/reference/generated/numpy.frombuffer.html
            np.frombuffer(
                raw_frame, dtype=np.uint8, count=frame_width * frame_height
            ).reshape(frame_width, frame_height)
        )
    )
