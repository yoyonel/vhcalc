#include "test_framework.h"
#include "imghash.h"
#include "test_vectors.h"
#include <stdint.h>
#include <stdio.h>

void test_phash_vectors(void) {
    for (int i = 0; i < NUM_VECTORS; i++) {
        uint64_t actual = phash_compute(test_vectors[i].image);
        printf("Test vector '%s': ", test_vectors[i].name);
        ASSERT_EQ_UINT64(test_vectors[i].expected_hash, actual);
    }
}

int main(void) {
    RUN_TEST(test_phash_vectors);
    TEST_REPORT();
}
