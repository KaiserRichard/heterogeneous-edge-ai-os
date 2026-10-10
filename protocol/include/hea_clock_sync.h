/* Portable clock offset, delay, drift and timer-wrap helpers. */
#ifndef HEA_CLOCK_SYNC_H
#define HEA_CLOCK_SYNC_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

struct hea_clock_sample {
    uint64_t t1_pi_us;
    uint64_t t2_mcu_us;
    uint64_t t3_mcu_us;
    uint64_t t4_pi_us;
};

struct hea_clock_estimate {
    double offset_us;
    uint64_t delay_us;
    uint64_t reference_pi_us;
};

struct hea_clock_fit {
    double offset_us;
    double drift;
    double drift_ppm;
    double rms_residual_us;
    double max_residual_us;
    uint64_t reference_pi_us;
    size_t sample_count;
};

struct hea_clock_filter {
    struct hea_clock_estimate *samples;
    size_t capacity;
    size_t count;
    uint64_t window_us;
};

struct hea_clock_wrap {
    uint32_t last_raw;
    uint64_t last_extended;
    int initialized;
};

/* Return 0 on success; -1 rejects invalid ordering, overflow or bad output. */
int hea_clock_sample(const struct hea_clock_sample *sample,
                     struct hea_clock_estimate *estimate);

/* The minimum-delay sample wins; ties retain the oldest reference time. */
int hea_clock_filter_init(struct hea_clock_filter *filter,
                          struct hea_clock_estimate *storage,
                          size_t capacity, uint64_t window_us);
int hea_clock_filter_add(struct hea_clock_filter *filter,
                         const struct hea_clock_sample *sample);
int hea_clock_filter_min(const struct hea_clock_filter *filter,
                         struct hea_clock_estimate *estimate);

/* Fit offset(t) = offset_us + drift * (t - reference_pi_us). */
int hea_clock_fit(const struct hea_clock_filter *filter,
                  uint64_t reference_pi_us, struct hea_clock_fit *fit);

/* Initialize at any raw-timer epoch; no wall-clock alignment is inferred. */
void hea_clock_wrap_init(struct hea_clock_wrap *state, uint32_t raw);
/* Forward gaps must be strictly less than 2^31 microseconds. */
int hea_clock_wrap_extend(struct hea_clock_wrap *state, uint32_t raw,
                          uint64_t *extended);

#ifdef __cplusplus
}
#endif

#endif /* HEA_CLOCK_SYNC_H */
