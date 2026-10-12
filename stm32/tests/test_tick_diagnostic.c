#include "tick_diagnostic.h"
#include <assert.h>
#include <stdio.h>

int main(void)
{
    tick_diagnostic_t d;
    tick_diagnostic_init(&d, 0, 0);
    assert(d.ppm == INT32_MIN && d.window_ms == 0);
    assert(!tick_diagnostic_sample(&d, 999, 999999));
    assert(tick_diagnostic_sample(&d, 1000, 1000000));
    assert(d.ppm == 0 && d.window_ms == 1000);
    assert(!tick_diagnostic_sample(&d, 10999, 10999999));
    assert(tick_diagnostic_sample(&d, 11180, 11000000));
    assert(d.ppm == 18000 && d.window_ms == 10000);
    assert(tick_diagnostic_sample(&d, 21000, 21000000));
    assert(d.ppm == -18000);
    tick_diagnostic_init(&d, UINT32_MAX - 499u, UINT32_MAX - 499999u);
    assert(tick_diagnostic_sample(&d, 500, 500000));
    assert(d.ppm == 0);
    /* Quantization: one extra tick in a 10 s window is 100 ppm. */
    assert(tick_diagnostic_sample(&d, 10501, 10500000));
    assert(d.ppm == 100);
    assert(!tick_diagnostic_sample(&d, 1, 1));
    assert(d.ppm == INT32_MIN && d.window_ms == 0);
    puts("PASS: tick ratio startup, 10 s cadence, sign, quantization, wraps and invalid gaps");
    return 0;
}
