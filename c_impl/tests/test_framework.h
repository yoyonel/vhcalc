#ifndef TEST_FRAMEWORK_H
#define TEST_FRAMEWORK_H

#include <stdio.h>
#include <string.h>

static int tests_run = 0;
static int tests_failed = 0;

#define ASSERT_EQ_UINT64(expected, actual) do { \
    if ((expected) != (actual)) { \
        printf("FAIL: %s:%d: Expected 0x%016lx, got 0x%016lx\n", __FILE__, __LINE__, (unsigned long)(expected), (unsigned long)(actual)); \
        tests_failed++; \
        return; \
    } \
} while(0)

#define RUN_TEST(test) do { \
    printf("Running %s... ", #test); \
    int failed_before = tests_failed; \
    test(); \
    if (tests_failed == failed_before) { \
        printf("PASS\n"); \
    } \
    tests_run++; \
} while(0)

#define TEST_REPORT() do { \
    printf("\n%d tests run, %d failed.\n", tests_run, tests_failed); \
    if (tests_failed > 0) return 1; \
    return 0; \
} while(0)

#endif // TEST_FRAMEWORK_H
