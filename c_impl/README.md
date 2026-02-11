# vhcalc-c (Suckless C11 Implementation)

A high-performance, minimalist, and portable C11 implementation of the `vhcalc` video hashing tool. This implementation strictly adheres to "suckless" principles: simplicity, clarity, and zero unnecessary dependencies.

## Architecture

*   **Language:** C11 (ISO/IEC 9899:2011)
*   **Build System:** Standard POSIX Make + Just (for modern command running)
*   **Dependencies:**
    *   C Standard Library (`stdlib`, `math`, `stdio`, `getopt`, `string`)
    *   Runtime Dependency: `ffmpeg` (must be in PATH) for video decoding and image scaling.
*   **Principles:**
    *   **No Frameworks:** Logic is implemented from scratch using standard libraries.
    *   **Simplicity:** No complex abstractions or object hierarchies. Direct data manipulation.
    *   **Portability:** Compiles with GCC/Clang on POSIX systems.

## Usage

### Building

```bash
# Using Just (Recommended)
just build

# Using Make directly
make
```

### Running

```bash
./build/vhcalc [OPTIONS] [INPUT_STREAM]
```

**Options:**
*   `-m, --image-hashing-method METHOD`: Hashing method (default: PerceptualHashing).
*   `-d, --decompress`: Decompress image hashes from binary streams.
*   `-h, --help`: Show help.
*   `-v, --version`: Show version.

**Example:**

```bash
cat video.mkv | ./build/vhcalc | ./build/vhcalc --decompress
```

## Algorithm: Perceptual Hashing (pHash)

The tool implements a variation of the pHash algorithm optimized for video frames.

### Steps:
1.  **Preprocessing:** The input video frame is resized to 32x32 pixels and converted to grayscale using `ffmpeg`.
2.  **Discrete Cosine Transform (DCT-II):**
    A 32x32 DCT-II is applied to the image to separate frequency components.
    Formula (1D):

    $$ X_k = \sum_{n=0}^{N-1} x_n \cos\left[\frac{\pi}{N}\left(n+\frac{1}{2}\right)k\right] $$

    This is applied first to rows, then to columns.
3.  **Low-Frequency Extraction:**
    The top-left 8x8 coefficients (representing low frequencies) are extracted. These contain the structural information of the image.
4.  **Median Computation:**
    The median value of the 64 coefficients is computed.
5.  **Hash Generation:**
    A 64-bit hash is constructed. Each bit corresponds to one coefficient:
    *   1 if coefficient > median
    *   0 if coefficient <= median

This method is robust against small changes, noise, and scaling, making it suitable for perceptual video hashing.
