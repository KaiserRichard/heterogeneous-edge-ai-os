#ifndef TICK_DIAGNOSTIC_H
#define TICK_DIAGNOSTIC_H

#include <stdbool.h>
#include <stdint.h>

/* 1 kHz SysTick vs free-running TIM2. Positive ppm means ticks run fast.
 * First measurement covers startup's first second, then nonoverlapping 10 s
 * windows. Unsigned deltas tolerate either counter wrapping. Single owner. */
typedef struct {
    uint32_t ticks, us;
    bool measured;
    int32_t ppm; /* INT32_MIN until the startup window completes. */
    uint16_t window_ms;
} tick_diagnostic_t;

static inline void tick_diagnostic_init(tick_diagnostic_t *d, uint32_t ticks, uint32_t us)
{
    *d = (tick_diagnostic_t){ticks, us, false, INT32_MIN, 0};
}

static inline bool tick_diagnostic_sample(tick_diagnostic_t *d, uint32_t ticks, uint32_t us)
{
    uint32_t elapsed = us - d->us;
    if (elapsed < (d->measured ? 10000000u : 1000000u)) return false;
    /* A stalled sampler cannot claim a valid short-window measurement. */
    if (elapsed >= 0x80000000u || elapsed > 65535000u) {
        tick_diagnostic_init(d, ticks, us);
        return false;
    }
    int64_t error = (int64_t)(uint32_t)(ticks - d->ticks) * 1000 - elapsed;
    int64_t scaled = error * 1000000;
    int64_t ppm = (scaled + (scaled < 0 ? -(int64_t)(elapsed / 2u) : elapsed / 2u)) / elapsed;
    d->ppm = ppm > INT32_MAX ? INT32_MAX : ppm <= INT32_MIN ? INT32_MIN + 1 : (int32_t)ppm;
    d->window_ms = (uint16_t)(elapsed / 1000u);
    d->ticks = ticks;
    d->us = us;
    d->measured = true;
    return true;
}
#endif
