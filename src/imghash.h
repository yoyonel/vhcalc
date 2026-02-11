#ifndef IMGHASH_H
#define IMGHASH_H

#include <stdint.h>
#include <stddef.h>

/**
 * Computes the Perceptual Hash (phash) of a 32x32 grayscale image.
 *
 * @param image Pointer to the 32x32 grayscale image data (row-major).
 * @return The 64-bit phash value.
 */
uint64_t phash_compute(const uint8_t *image);

#endif // IMGHASH_H
