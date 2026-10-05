#ifndef TIMING_H
#define TIMING_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Retrieve current monotonic timestamp in nanoseconds.
 *
 * Uses CLOCK_MONOTONIC on POSIX-compliant systems (macOS and Linux).
 * Guaranteed to be non-decreasing (monotonic) and unaffected by system
 * wall-clock adjustments, making it suitable for elapsed duration measurement.
 *
 * Note on resolution contract: Consecutive back-to-back calls without delay
 * may return identical timestamps if called within the minimum granularity of
 * the underlying hardware clock.
 *
 * @return Current timestamp in nanoseconds (non-decreasing).
 */
uint64_t timing_get_monotonic_ns(void);

/**
 * @brief High-resolution sleep for the specified duration in nanoseconds.
 *
 * Uses nanosleep on POSIX-compliant systems.
 *
 * @param ns Duration to sleep in nanoseconds.
 */
void timing_sleep_ns(uint64_t ns);

#ifdef __cplusplus
}
#endif

#endif /* TIMING_H */
