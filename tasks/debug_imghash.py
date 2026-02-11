import numpy as np
from PIL import Image
import imagehash
import scipy.fftpack

def inspect_black():
    img = Image.new('L', (32, 32), color=0)
    h = imagehash.phash(img)
    print(f"Hash: {h} (hex: {str(h)})")

    # Replicate logic
    pixels = np.asarray(img)
    dct = scipy.fftpack.dct(scipy.fftpack.dct(pixels, axis=0), axis=1)
    dctlowfreq = dct[:8, :8]
    med = np.median(dctlowfreq)
    diff = dctlowfreq > med

    print("DCT low freq top left 4x4:")
    print(dctlowfreq[:4,:4])
    print(f"Median: {med}")
    print("Diff:")
    print(diff.astype(int))

if __name__ == "__main__":
    inspect_black()
