#define _POSIX_C_SOURCE 200809L

#include "timing.h"
#include <time.h>
#include <errno.h>

#define NS_PER_SEC 1000000000ULL

uint64_t timing_get_monotonic_ns(void) {
    struct timespec ts;
    if (clock_gettime(CLOCK_MONOTONIC, &ts) != 0) {
        return 0;
    }
    return ((uint64_t)ts.tv_sec * NS_PER_SEC) + (uint64_t)ts.tv_nsec;
}

void timing_sleep_ns(uint64_t ns) {
    if (ns == 0) {
        return;
    }

    struct timespec req;
    struct timespec rem;
    req.tv_sec = (time_t)(ns / NS_PER_SEC);
    req.tv_nsec = (long)(ns % NS_PER_SEC);

    while (nanosleep(&req, &rem) == -1 && errno == EINTR) {
        req = rem;
    }
}
