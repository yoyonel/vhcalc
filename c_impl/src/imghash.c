/**
 * @file imghash.c
 * @brief Implementation of Perceptual Hashing (pHash) algorithm.
 *
 * This implementation uses the Discrete Cosine Transform (DCT) to convert the image
 * into the frequency domain. It then extracts the low-frequency components (top-left 8x8)
 * and generates a 64-bit hash based on the median value of these coefficients.
 */

#include "imghash.h"
#include <stdint.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/**
 * @brief Computes the 32x32 Discrete Cosine Transform (DCT-II).
 *
 * This function implements a separable 2D DCT using two 1D DCT passes (rows then columns).
 * The formula used for the 1D DCT is:
 *
 * X_k = sum_{n=0}^{N-1} x_n * cos((pi/N) * (n + 0.5) * k)
 *
 * Note: This implementation does not include the standard scaling factors (alpha_k),
 * as the relative order of coefficients (for median comparison) is preserved without them.
 *
 * @param input Pointer to the 32x32 input array (row-major).
 * @param output Pointer to the 32x32 output array (row-major).
 */
static void dct32(const double *input, double *output) {
    double temp[32 * 32];

    // 1D DCT on rows
    for (int y = 0; y < 32; y++) {
        for (int k = 0; k < 32; k++) {
            double sum = 0.0;
            for (int n = 0; n < 32; n++) {
                sum += input[y * 32 + n] * cos((M_PI / 32.0) * (n + 0.5) * k);
            }
            if (fabs(sum) < 1e-6) sum = 0.0;
            temp[y * 32 + k] = sum;
        }
    }

    // 1D DCT on cols of temp
    for (int x = 0; x < 32; x++) {
        for (int k = 0; k < 32; k++) {
            double sum = 0.0;
            for (int n = 0; n < 32; n++) {
                sum += temp[n * 32 + x] * cos((M_PI / 32.0) * (n + 0.5) * k);
            }
            if (fabs(sum) < 1e-6) sum = 0.0;
            output[k * 32 + x] = sum;
        }
    }
}

static int compare_doubles(const void *a, const void *b) {
    double da = *(const double *)a;
    double db = *(const double *)b;
    if (da > db) return 1;
    if (da < db) return -1;
    return 0;
}

/**
 * @brief Computes the 64-bit Perceptual Hash of an image.
 *
 * Algorithm steps:
 * 1. Convert the input 32x32 grayscale image to double precision.
 * 2. Apply a 32x32 DCT-II to transform the image to the frequency domain.
 * 3. Extract the top-left 8x8 low-frequency coefficients (representing the structural information).
 * 4. Compute the median value of these 64 coefficients.
 * 5. Construct the 64-bit hash:
 *    - For each coefficient (row-major order):
 *      - If coefficient > median, set the corresponding bit to 1.
 *      - Otherwise, set the bit to 0.
 *
 * @param image Pointer to the 32x32 grayscale image data.
 * @return The 64-bit perceptual hash.
 */
uint64_t phash_compute(const uint8_t *image) {
    double input[32 * 32];
    double dct_output[32 * 32];
    double low_freq[8 * 8];
    double sorted_low_freq[8 * 8];

    // Convert to double
    for (int i = 0; i < 32 * 32; i++) {
        input[i] = (double)image[i];
    }

    dct32(input, dct_output);

    // Extract 8x8 top-left
    for (int y = 0; y < 8; y++) {
        for (int x = 0; x < 8; x++) {
            low_freq[y * 8 + x] = dct_output[y * 32 + x];
        }
    }

    // Compute median
    memcpy(sorted_low_freq, low_freq, sizeof(low_freq));
    qsort(sorted_low_freq, 64, sizeof(double), compare_doubles);

    // Median of 64 elements (even) is average of indices 31 and 32
    double median = (sorted_low_freq[31] + sorted_low_freq[32]) / 2.0;


    // Compute hash
    uint64_t hash = 0;
    uint64_t one = 1;
    for (int i = 0; i < 64; i++) {
        if (low_freq[i] > median) {
            hash |= (one << (63 - i)); // MSB first (index 0 is MSB)
        }
    }

    return hash;
}
