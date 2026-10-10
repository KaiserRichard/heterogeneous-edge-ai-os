#include "hea_clock_sync.h"

#include <math.h>
#include <stdio.h>
#include <string.h>

static unsigned checks;
#define CHECK(expr) do { ++checks; if (!(expr)) { \
    fprintf(stderr, "%s:%d: %s\n", __FILE__, __LINE__, #expr); return 1; \
} } while (0)

static int near(double actual, double expected, double tolerance)
{
    return fabs(actual - expected) <= tolerance;
}

static int test_samples_and_bias(void)
{
    struct hea_clock_estimate e;
    struct hea_clock_sample s = {1000000000000ull, 1000000000250ull,
                                 1000000000350ull, 1000000000200ull};
    CHECK(hea_clock_sample(&s, &e) == 0 && near(e.offset_us, 200.0, 0.01) && e.delay_us == 100u);
    s.t4_pi_us = 1000000000300ull;
    CHECK(hea_clock_sample(&s, &e) == 0 && near(e.offset_us, 150.0, 0.01) && e.delay_us == 200u);
    s.t2_mcu_us = 1000000000150ull;
    CHECK(hea_clock_sample(&s, &e) == 0 && near(e.offset_us, 100.0, 0.01));
    s.t4_pi_us = 1000000000000ull;
    CHECK(hea_clock_sample(&s, &e) != 0); /* negative delay */
    s = (struct hea_clock_sample){0u, UINT64_C(9007199254740993),
                                  UINT64_C(9007199254740993),
                                  UINT64_C(18014398509481985)};
    CHECK(hea_clock_sample(&s, &e) == 0 && near(e.offset_us, 0.5, 0.01));
    return 0;
}

static int test_filter_and_fit(void)
{
    struct hea_clock_estimate storage[4], min;
    struct hea_clock_filter f;
    struct hea_clock_fit fit;
    const double offset = -37.5, drift = 2.5e-6;
    unsigned i;
    CHECK(hea_clock_filter_init(&f, storage, 4u, 10000000000ull) == 0);
    for (i = 0u; i < 6u; ++i) {
        uint64_t t = 1000000000000ull + (uint64_t)i * 1000000000ull;
        double y = offset + drift * ((double)i * 1000000000.0 - 5000000050.0);
        int64_t delta = (int64_t)(y >= 0.0 ? y + 0.5 : y - 0.5);
        struct hea_clock_sample s = {t, 0u, 0u, t + 100u};
        /* Encode a rounded integer offset without converting absolute time. */
        s.t2_mcu_us = delta < 0 ? t + 50u - (uint64_t)(-delta)
                                : t + 50u + (uint64_t)delta;
        s.t3_mcu_us = s.t2_mcu_us + 1u;
        CHECK(hea_clock_filter_add(&f, &s) == 0);
    }
    CHECK(f.count == 4u);
    CHECK(hea_clock_filter_min(&f, &min) == 0 && min.delay_us == 99u &&
          min.reference_pi_us == 1002000000050ull);
    CHECK(hea_clock_fit(&f, 1005000000050ull, &fit) == 0);
    CHECK(fit.sample_count == 4u && near(fit.drift_ppm, 2.5, 0.001));
    printf("  fit: offset=%.6f us drift=%.6f ppm rms=%.6f us max=%.6f us\n",
           fit.offset_us, fit.drift_ppm, fit.rms_residual_us, fit.max_residual_us);
    CHECK(near(fit.offset_us, offset, 0.01));
    CHECK(fit.rms_residual_us < 0.05 && fit.max_residual_us < 0.05);
    return 0;
}

static int test_jitter_and_singular(void)
{
    struct hea_clock_estimate storage[8];
    struct hea_clock_filter f;
    struct hea_clock_fit fit;
    unsigned i;
    CHECK(hea_clock_filter_init(&f, storage, 8u, 10000u) == 0);
    for (i = 0u; i < 4u; ++i) {
        uint64_t t = 1000u + (uint64_t)i * 100u;
        struct hea_clock_sample s = {t, t + 20u + (i & 1u), t + 20u + (i & 1u), t + 100u};
        CHECK(hea_clock_filter_add(&f, &s) == 0);
    }
    CHECK(hea_clock_fit(&f, 1000u, &fit) == 0 && fit.rms_residual_us <= 0.55);
    CHECK(hea_clock_filter_init(&f, storage, 8u, 0u) == 0);
    {
        struct hea_clock_sample s = {1u, 21u, 21u, 101u};
        CHECK(hea_clock_filter_add(&f, &s) == 0);
        s.t1_pi_us = 2u;
        s.t2_mcu_us = 22u;
        s.t3_mcu_us = 22u;
        s.t4_pi_us = 102u;
        CHECK(hea_clock_filter_add(&f, &s) == 0);
        CHECK(hea_clock_fit(&f, 1u, &fit) != 0);
    }
    return 0;
}

static int test_filter_age_and_regression(void)
{
    struct hea_clock_estimate storage[4], before;
    struct hea_clock_filter f;
    struct hea_clock_sample s = {200u, 200u, 200u, 200u};
    CHECK(hea_clock_filter_init(&f, storage, 4u, 10u) == 0);
    CHECK(hea_clock_filter_add(&f, &s) == 0 && f.count == 1u);
    before = storage[0];
    s = (struct hea_clock_sample){0u, 0u, 0u, 0u};
    CHECK(hea_clock_filter_add(&f, &s) != 0 && f.count == 1u);
    CHECK(storage[0].reference_pi_us == before.reference_pi_us &&
          storage[0].delay_us == before.delay_us);
    s = (struct hea_clock_sample){211u, 211u, 211u, 211u};
    CHECK(hea_clock_filter_add(&f, &s) == 0 && f.count == 1u);
    CHECK(storage[0].reference_pi_us == 211u);
    return 0;
}

static int test_large_fit_reference(void)
{
    struct hea_clock_estimate storage[2];
    struct hea_clock_filter f;
    struct hea_clock_fit fit;
    uint64_t base = UINT64_C(1152921504606846976); /* 2^60 */
    struct hea_clock_sample s = {base, base + 100u, base + 100u, base};
    CHECK(hea_clock_filter_init(&f, storage, 2u, UINT64_MAX) == 0);
    CHECK(hea_clock_filter_add(&f, &s) == 0);
    s = (struct hea_clock_sample){base + 1u, base + 102u, base + 102u, base + 1u};
    CHECK(hea_clock_filter_add(&f, &s) == 0);
    CHECK(hea_clock_fit(&f, 0u, &fit) == 0);
    /* At reference zero the intercept is necessarily huge; the centered fit
     * must still preserve the unit timestamp spread and return successfully. */
    CHECK(near(fit.drift, 1.0, 0.000001) &&
          near(fit.offset_us, -(double)base + 100.0, 256.0));
    CHECK(fit.sample_count == 2u && fit.rms_residual_us < 0.01);
    return 0;
}

static int test_invalid_large_and_wrap(void)
{
    struct hea_clock_estimate e = {9.0, 9u, 9u};
    struct hea_clock_sample bad = {10u, 20u, 30u, 5u};
    struct hea_clock_wrap w;
    uint64_t out = 77u;
    CHECK(hea_clock_sample(&bad, &e) != 0 && e.offset_us == 9.0);
    bad = (struct hea_clock_sample){UINT64_MAX - 100u, UINT64_MAX - 50u,
                                   UINT64_MAX - 40u, UINT64_MAX - 1u};
    CHECK(hea_clock_sample(&bad, &e) == 0 && isfinite(e.offset_us));
    hea_clock_wrap_init(&w, UINT32_MAX - 5u);
    CHECK(hea_clock_wrap_extend(&w, 3u, &out) == 0 && out == UINT64_C(0x100000003));
    CHECK(hea_clock_wrap_extend(&w, 3u, &out) == 0 && out == UINT64_C(0x100000003));
    CHECK(hea_clock_wrap_extend(&w, UINT32_C(0x80000003), &out) != 0 && out == UINT64_C(0x100000003));
    CHECK(hea_clock_wrap_extend(&w, 4u, &out) == 0 && out == UINT64_C(0x100000004));
    CHECK(hea_clock_wrap_extend(&w, 2u, &out) != 0 && out == UINT64_C(0x100000004));

    {
        struct hea_clock_wrap sample_wrap;
        struct hea_clock_estimate estimate;
        uint64_t t2, t3;
        hea_clock_wrap_init(&sample_wrap, UINT32_MAX - 100u);
        CHECK(hea_clock_wrap_extend(&sample_wrap, UINT32_MAX - 50u, &t2) == 0);
        CHECK(hea_clock_wrap_extend(&sample_wrap, 25u, &t3) == 0);
        {
            struct hea_clock_sample sample = {UINT32_MAX - 100u, t2, t3,
                                              (uint64_t)(UINT32_MAX - 100u) + 200u};
            CHECK(hea_clock_sample(&sample, &estimate) == 0 &&
                  estimate.delay_us == 124u);
        }
    }
    return 0;
}

int main(void)
{
    if (test_samples_and_bias() || test_filter_and_fit() ||
        test_jitter_and_singular() || test_filter_age_and_regression() ||
        test_large_fit_reference() || test_invalid_large_and_wrap()) return 1;
    printf("clock-sync tests passed (%u checks; tolerances offset/drift 0.01 us, jitter 0.55 us, drift 0.001 ppm)\n", checks);
    return 0;
}
