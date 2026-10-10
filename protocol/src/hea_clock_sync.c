#include "hea_clock_sync.h"

#include <float.h>
#include <math.h>
#include <stddef.h>

static int signed_difference(uint64_t a, uint64_t b, int64_t *difference)
{
    if (a >= b) {
        uint64_t magnitude = a - b;
        if (magnitude > (uint64_t)INT64_MAX) return -1;
        *difference = (int64_t)magnitude;
    } else {
        uint64_t magnitude = b - a;
        if (magnitude > (uint64_t)INT64_MAX) return -1;
        *difference = -(int64_t)magnitude;
    }
    return 0;
}

int hea_clock_sample(const struct hea_clock_sample *sample,
                     struct hea_clock_estimate *estimate)
{
    int64_t t2_minus_t1, t3_minus_t4;
    uint64_t pi_elapsed, mcu_elapsed;
    if (sample == NULL || estimate == NULL || sample->t4_pi_us < sample->t1_pi_us ||
        sample->t3_mcu_us < sample->t2_mcu_us)
        return -1;
    if (signed_difference(sample->t2_mcu_us, sample->t1_pi_us, &t2_minus_t1) != 0 ||
        signed_difference(sample->t3_mcu_us, sample->t4_pi_us, &t3_minus_t4) != 0)
        return -1;
    pi_elapsed = sample->t4_pi_us - sample->t1_pi_us;
    mcu_elapsed = sample->t3_mcu_us - sample->t2_mcu_us;
    if (pi_elapsed < mcu_elapsed) return -1; /* negative delay is unusable */

    if (sample->t1_pi_us > UINT64_MAX - pi_elapsed / 2u) return -1;
    /* Combine the exact integer differences before converting.  In particular,
     * converting each term to double first can lose a low bit at 2^53. */
    estimate->offset_us = (double)(((long double)t2_minus_t1 +
                                    (long double)t3_minus_t4) / 2.0L);
    estimate->delay_us = pi_elapsed - mcu_elapsed;
    estimate->reference_pi_us = sample->t1_pi_us + pi_elapsed / 2u;
    if (!isfinite(estimate->offset_us)) return -1;
    return 0;
}

int hea_clock_filter_init(struct hea_clock_filter *filter,
                          struct hea_clock_estimate *storage,
                          size_t capacity, uint64_t window_us)
{
    if (filter == NULL || storage == NULL || capacity == 0u) return -1;
    filter->samples = storage;
    filter->capacity = capacity;
    filter->count = 0u;
    filter->window_us = window_us;
    return 0;
}

int hea_clock_filter_add(struct hea_clock_filter *filter,
                         const struct hea_clock_sample *sample)
{
    struct hea_clock_estimate estimate;
    size_t i, write_index;
    uint64_t newest_reference;
    if (filter == NULL || sample == NULL || filter->samples == NULL ||
        filter->capacity == 0u || hea_clock_sample(sample, &estimate) != 0)
        return -1;

    /* A sample from before the newest retained reference is a regression, not
     * an old sample to admit.  Reject it without changing the filter state. */
    if (filter->count != 0u) {
        newest_reference = filter->samples[0].reference_pi_us;
        for (i = 1u; i < filter->count; ++i)
            if (filter->samples[i].reference_pi_us > newest_reference)
                newest_reference = filter->samples[i].reference_pi_us;
        if (estimate.reference_pi_us < newest_reference) return -1;
    }

    /* The newest reference defines age. Equality at the boundary is retained. */
    for (i = 0u; i < filter->count;) {
        uint64_t age = estimate.reference_pi_us >= filter->samples[i].reference_pi_us
                           ? estimate.reference_pi_us - filter->samples[i].reference_pi_us
                           : 0u;
        if (age > filter->window_us) {
            filter->samples[i] = filter->samples[filter->count - 1u];
            --filter->count;
        } else {
            ++i;
        }
    }
    if (filter->count < filter->capacity) {
        write_index = filter->count++;
    } else {
        /* A full window evicts its oldest sample. */
        write_index = 0u;
        for (i = 1u; i < filter->count; ++i)
            if (filter->samples[i].reference_pi_us < filter->samples[write_index].reference_pi_us)
                write_index = i;
    }
    filter->samples[write_index] = estimate;
    return 0;
}

int hea_clock_filter_min(const struct hea_clock_filter *filter,
                         struct hea_clock_estimate *estimate)
{
    size_t i, best;
    if (filter == NULL || estimate == NULL || filter->samples == NULL || filter->count == 0u)
        return -1;
    best = 0u;
    for (i = 1u; i < filter->count; ++i)
        if (filter->samples[i].delay_us < filter->samples[best].delay_us ||
            (filter->samples[i].delay_us == filter->samples[best].delay_us &&
             filter->samples[i].reference_pi_us < filter->samples[best].reference_pi_us))
            best = i;
    *estimate = filter->samples[best];
    return 0;
}

int hea_clock_fit(const struct hea_clock_filter *filter,
                  uint64_t reference_pi_us, struct hea_clock_fit *fit)
{
    long double mean_x = 0.0L, mean_y = 0.0L;
    long double sxx = 0.0L, sxy = 0.0L;
    long double rms_sum = 0.0L, max_residual = 0.0L;
    long double fitted_drift, centre_offset;
    uint64_t centre;
    uint64_t minimum, maximum;
    size_t i;
    if (filter == NULL || fit == NULL || filter->samples == NULL || filter->count < 2u)
        return -1;
    minimum = filter->samples[0].reference_pi_us;
    maximum = minimum;
    for (i = 0u; i < filter->count; ++i) {
        if (!isfinite(filter->samples[i].offset_us)) return -1;
        if (filter->samples[i].reference_pi_us < minimum)
            minimum = filter->samples[i].reference_pi_us;
        if (filter->samples[i].reference_pi_us > maximum)
            maximum = filter->samples[i].reference_pi_us;
    }
    /* Centre on the data, independently of the requested output reference.
     * This keeps adjacent timestamps distinct even when they are near 2^60. */
    centre = minimum + (maximum - minimum) / 2u;
    for (i = 0u; i < filter->count; ++i) {
        uint64_t timestamp = filter->samples[i].reference_pi_us;
        long double x = timestamp >= centre
                            ? (long double)(timestamp - centre)
                            : -(long double)(centre - timestamp);
        mean_x += x;
        mean_y += (long double)filter->samples[i].offset_us;
    }
    mean_x /= (long double)filter->count;
    mean_y /= (long double)filter->count;
    for (i = 0u; i < filter->count; ++i) {
        uint64_t timestamp = filter->samples[i].reference_pi_us;
        long double x = timestamp >= centre
                            ? (long double)(timestamp - centre)
                            : -(long double)(centre - timestamp);
        long double dx = x - mean_x;
        long double dy = (long double)filter->samples[i].offset_us - mean_y;
        sxx += dx * dx;
        sxy += dx * dy;
    }
    if (!isfinite(sxx) || !isfinite(sxy) || sxx == 0.0L) return -1;
    {
        long double drift = sxy / sxx;
        centre_offset = mean_y - drift * mean_x;
        long double reference_delta = reference_pi_us >= centre
                                          ? (long double)(reference_pi_us - centre)
                                          : -(long double)(centre - reference_pi_us);
        long double offset = centre_offset + drift * reference_delta;
        if (!isfinite(drift) || !isfinite(centre_offset) ||
            !isfinite(reference_delta) || !isfinite(offset)) return -1;
        fitted_drift = drift;
        fit->drift = (double)drift;
        fit->offset_us = (double)offset;
    }
    fit->reference_pi_us = reference_pi_us;
    fit->sample_count = filter->count;
    if (!isfinite(fit->drift) || !isfinite(fit->offset_us)) return -1;
    for (i = 0u; i < filter->count; ++i) {
        uint64_t timestamp = filter->samples[i].reference_pi_us;
        long double x = timestamp >= centre
                            ? (long double)(timestamp - centre)
                            : -(long double)(centre - timestamp);
        long double residual = (long double)filter->samples[i].offset_us -
                               (centre_offset + fitted_drift * x);
        if (!isfinite(residual)) return -1;
        rms_sum += residual * residual;
        if (fabsl(residual) > max_residual) max_residual = fabsl(residual);
    }
    fit->rms_residual_us = (double)sqrtl(rms_sum / (long double)filter->count);
    fit->max_residual_us = (double)max_residual;
    fit->drift_ppm = fit->drift * 1000000.0;
    if (!isfinite(fit->rms_residual_us) || !isfinite(fit->drift_ppm)) return -1;
    return 0;
}

void hea_clock_wrap_init(struct hea_clock_wrap *state, uint32_t raw)
{
    if (state == NULL) return;
    state->last_raw = raw;
    state->last_extended = raw;
    state->initialized = 1;
}

int hea_clock_wrap_extend(struct hea_clock_wrap *state, uint32_t raw,
                          uint64_t *extended)
{
    uint32_t delta;
    uint64_t candidate;
    if (state == NULL || extended == NULL || !state->initialized) return -1;
    delta = raw - state->last_raw;
    if (delta == UINT32_C(0x80000000) || delta > UINT32_C(0x80000000)) return -1;
    candidate = state->last_extended + (uint64_t)delta;
    if (candidate < state->last_extended) return -1;
    *extended = candidate;
    state->last_raw = raw;
    state->last_extended = candidate;
    return 0;
}
