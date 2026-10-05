#ifndef TEST_COMMON_H
#define TEST_COMMON_H

#include <stdio.h>
#include <stdlib.h>

static int g_test_failures = 0;
static int g_test_count = 0;

#define TEST_ASSERT(cond) do { \
    g_test_count++; \
    if (!(cond)) { \
        fprintf(stderr, "  [FAIL] %s:%d: Assertion '%s' failed.\n", __FILE__, __LINE__, #cond); \
        g_test_failures++; \
    } \
} while (0)

#define TEST_ASSERT_EQ(a, b) do { \
    g_test_count++; \
    if ((a) != (b)) { \
        fprintf(stderr, "  [FAIL] %s:%d: Expected %s == %s, got %lld != %lld\n", \
                __FILE__, __LINE__, #a, #b, (long long)(a), (long long)(b)); \
        g_test_failures++; \
    } \
} while (0)

#define TEST_REPORT() do { \
    if (g_test_failures == 0) { \
        printf("[PASS] All %d assertions passed successfully.\n", g_test_count); \
    } else { \
        fprintf(stderr, "[FAIL] %d of %d assertions failed!\n", g_test_failures, g_test_count); \
    } \
} while (0)

#endif /* TEST_COMMON_H */
