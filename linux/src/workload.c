#include "workload.h"
#include "timing.h"
#include <stdio.h>
#include <inttypes.h>
#include <math.h>

void workload_config_init_default(workload_config_t *config) {
    if (config == NULL) {
        return;
    }
    config->iterations = 100;
    config->warmup_iterations = 10;
    config->intensity = 1000;
    config->interval_ms = 0;
    config->csv_output_path = NULL;
}

bool workload_run_compute_step(uint32_t intensity, double *result_out) {
    if (intensity == 0) {
        intensity = 1;
    }

    /* Deterministic arithmetic workload simulating lightweight edge compute */
    double acc = 1.0;
    const uint32_t inner_loops = intensity * 100U;

    for (uint32_t i = 1; i <= inner_loops; ++i) {
        /* Polynomial calculation with non-trivial math to prevent compiler elimination */
        double x = (double)(i & 0xFF) * 0.01;
        acc += (x * x - 0.5 * x + 0.125) / (acc + 1.0);
    }

    if (result_out != NULL) {
        *result_out = acc;
    }

    return true;
}

workload_error_t workload_write_csv(FILE *stream, const workload_record_t *records, size_t count) {
    if (stream == NULL || records == NULL) {
        return WORKLOAD_ERR_INVALID_ARG;
    }

    if (fprintf(stream, "sequence_id,workload_start_ns,workload_end_ns,latency_ns,valid\n") < 0) {
        return WORKLOAD_ERR_IO;
    }

    for (size_t i = 0; i < count; ++i) {
        int written = fprintf(
            stream,
            "%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%d\n",
            records[i].sequence_id,
            records[i].workload_start_ns,
            records[i].workload_end_ns,
            records[i].latency_ns,
            records[i].valid ? 1 : 0
        );
        if (written < 0) {
            return WORKLOAD_ERR_IO;
        }
    }

    return WORKLOAD_OK;
}

workload_error_t workload_execute(
    const workload_config_t *config,
    workload_record_t *records,
    size_t max_records,
    size_t *actual_records
) {
    if (config == NULL) {
        return WORKLOAD_ERR_INVALID_ARG;
    }
    if (config->iterations == 0) {
        return WORKLOAD_ERR_INVALID_ARG;
    }
    if (records == NULL && config->csv_output_path == NULL) {
        return WORKLOAD_ERR_INVALID_ARG;
    }
    if (records != NULL && max_records < config->iterations) {
        return WORKLOAD_ERR_INVALID_ARG;
    }

    /* 1. Warm-up iterations: executed to warm caches/predictors, strictly excluded from records */
    for (uint32_t w = 0; w < config->warmup_iterations; ++w) {
        double dummy = 0.0;
        if (!workload_run_compute_step(config->intensity, &dummy)) {
            return WORKLOAD_ERR_COMPUTE_FAILED;
        }
    }

    /* 2. Measured iterations */
    uint64_t seq = 1;
    for (uint32_t i = 0; i < config->iterations; ++i) {
        uint64_t start_ns = timing_get_monotonic_ns();
        double compute_result = 0.0;
        bool ok = workload_run_compute_step(config->intensity, &compute_result);
        uint64_t end_ns = timing_get_monotonic_ns();
        uint64_t latency_ns = (end_ns >= start_ns) ? (end_ns - start_ns) : 0;

        if (records != NULL) {
            records[i].sequence_id = seq;
            records[i].workload_start_ns = start_ns;
            records[i].workload_end_ns = end_ns;
            records[i].latency_ns = latency_ns;
            records[i].valid = ok;
        }

        if (config->interval_ms > 0) {
            timing_sleep_ns((uint64_t)config->interval_ms * 1000000ULL);
        }

        seq++;
    }

    if (actual_records != NULL) {
        *actual_records = config->iterations;
    }

    /* 3. CSV file generation if requested */
    if (config->csv_output_path != NULL && records != NULL) {
        FILE *fp = fopen(config->csv_output_path, "w");
        if (fp == NULL) {
            return WORKLOAD_ERR_IO;
        }
        workload_error_t write_err = workload_write_csv(fp, records, config->iterations);
        fclose(fp);
        if (write_err != WORKLOAD_OK) {
            return write_err;
        }
    }

    return WORKLOAD_OK;
}
