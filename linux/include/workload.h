#ifndef WORKLOAD_H
#define WORKLOAD_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    WORKLOAD_OK = 0,
    WORKLOAD_ERR_INVALID_ARG = -1,
    WORKLOAD_ERR_IO = -2,
    WORKLOAD_ERR_COMPUTE_FAILED = -3
} workload_error_t;

typedef struct {
    uint32_t iterations;         /* Number of measured iterations to execute and record */
    uint32_t warmup_iterations;  /* Warm-up iterations (executed, but excluded from measurements) */
    uint32_t intensity;          /* Synthetic computation complexity factor (e.g. inner loop size) */
    uint32_t interval_ms;        /* Pacing interval between iterations in ms (0 = back-to-back) */
    const char *csv_output_path; /* File path to write CSV output, or NULL to skip file output */
} workload_config_t;

typedef struct {
    uint64_t sequence_id;
    uint64_t workload_start_ns;
    uint64_t workload_end_ns;
    uint64_t latency_ns;
    bool valid;
} workload_record_t;

/**
 * @brief Initialize workload configuration with default parameters.
 *
 * @param config Pointer to configuration struct.
 */
void workload_config_init_default(workload_config_t *config);

/**
 * @brief Execute a single synthetic compute step.
 *
 * Simulates a realistic CPU-bound inference calculation using a deterministic
 * floating-point and integer math loop, without external ML dependencies.
 *
 * @param intensity Scale factor controlling compute loop iterations.
 * @param result_out Optional pointer to store computed checksum/result.
 * @return true if computation succeeded, false otherwise.
 */
bool workload_run_compute_step(uint32_t intensity, double *result_out);

/**
 * @brief Run the workload lifecycle (warmup + measured iterations).
 *
 * Executes warmup iterations first without recording them.
 * Then executes the requested number of iterations, measuring per-iteration
 * start/end monotonic timestamps, sequence IDs, and validity.
 *
 * @param config Workload execution configuration.
 * @param records Buffer to store recorded measurement entries.
 * @param max_records Capacity of the records buffer.
 * @param actual_records Pointer to store the number of recorded entries.
 * @return WORKLOAD_OK on success, negative error code on failure.
 */
workload_error_t workload_execute(
    const workload_config_t *config,
    workload_record_t *records,
    size_t max_records,
    size_t *actual_records
);

/**
 * @brief Write measured records to a CSV stream.
 *
 * Format: sequence_id,workload_start_ns,workload_end_ns,latency_ns,valid
 *
 * @param stream Output file stream.
 * @param records Array of workload records.
 * @param count Number of records to write.
 * @return WORKLOAD_OK on success, negative error code on failure.
 */
workload_error_t workload_write_csv(FILE *stream, const workload_record_t *records, size_t count);

#ifdef __cplusplus
}
#endif

#endif /* WORKLOAD_H */
