#include "test_framework.h"
#include "../src/imghash.c"
#include "test_vectors.h"
#include <stdint.h>
#include <stdio.h>
#include <string.h>

void test_phash_vectors(void) {
    for (int i = 0; i < NUM_VECTORS; i++) {
        uint64_t actual = phash_compute(test_vectors[i].image);
        ASSERT_EQ_UINT64(test_vectors[i].expected_hash, actual);
    }
}

void test_dct32_properties(void) {
    double input[32*32];
    double output[32*32];

    // Test 1: All ones (DC component only)
    for (int i=0; i<32*32; i++) input[i] = 1.0;
    dct32(input, output);

    // DC component (0,0) should be 32*32 = 1024.0
    // Based on the unscaled DCT-II implementation:
    // Row DCT: [32, 0, ..., 0]
    // Col DCT on that: [1024, 0, ..., 0]
    ASSERT_DOUBLE_EQ(1024.0, output[0], 1e-5);
    for (int i=1; i<32*32; i++) {
        ASSERT_DOUBLE_EQ(0.0, output[i], 1e-5);
    }

    // Test 2: All zeros
    for (int i=0; i<32*32; i++) input[i] = 0.0;
    dct32(input, output);
    for (int i=0; i<32*32; i++) {
        ASSERT_DOUBLE_EQ(0.0, output[i], 1e-5);
    }
}

void test_phash_edge_cases(void) {
    uint8_t image[32*32];

    // Case 1: All zeros
    memset(image, 0, 32*32);
    // DCT will be all 0. Median 0. 0 > 0 is false. Hash 0.
    ASSERT_EQ_UINT64(0ULL, phash_compute(image));

    // Case 2: All ones (255)
    memset(image, 255, 32*32);
    // DCT DC=1024*255, others 0.
    // Median 0.
    // (0,0) > 0 -> 1. Others 0.
    ASSERT_EQ_UINT64(0x8000000000000000ULL, phash_compute(image));
}

int main(void) {
    RUN_TEST(test_phash_vectors);
    RUN_TEST(test_dct32_properties);
    RUN_TEST(test_phash_edge_cases);
    TEST_REPORT();
}
