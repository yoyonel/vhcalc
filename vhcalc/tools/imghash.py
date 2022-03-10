import binascii

from imagehash import ImageHash


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
