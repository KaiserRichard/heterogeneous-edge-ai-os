#include "workload.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <inttypes.h>

static void print_usage(const char *prog_name) {
    printf("Usage: %s [options]\n", prog_name);
    printf("Options:\n");
    printf("  -n <iterations>  Number of measured iterations (default: 50)\n");
    printf("  -w <warmup>      Number of warm-up iterations (default: 5)\n");
    printf("  -i <intensity>   Workload compute intensity factor (default: 500)\n");
    printf("  -p <ms>          Sleep interval between iterations in ms (default: 0)\n");
    printf("  -o <path>        CSV output file path (optional)\n");
    printf("  -s               Print CSV output directly to stdout\n");
    printf("  -h               Show this help message\n");
}

int main(int argc, char **argv) {
    workload_config_t config;
    workload_config_init_default(&config);
    config.iterations = 50;
    config.warmup_iterations = 5;
    config.intensity = 500;
    config.interval_ms = 0;

    bool print_stdout_csv = false;

    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "-n") == 0 && i + 1 < argc) {
            config.iterations = (uint32_t)strtoul(argv[++i], NULL, 10);
        } else if (strcmp(argv[i], "-w") == 0 && i + 1 < argc) {
            config.warmup_iterations = (uint32_t)strtoul(argv[++i], NULL, 10);
        } else if (strcmp(argv[i], "-i") == 0 && i + 1 < argc) {
            config.intensity = (uint32_t)strtoul(argv[++i], NULL, 10);
        } else if (strcmp(argv[i], "-p") == 0 && i + 1 < argc) {
            config.interval_ms = (uint32_t)strtoul(argv[++i], NULL, 10);
        } else if (strcmp(argv[i], "-o") == 0 && i + 1 < argc) {
            config.csv_output_path = argv[++i];
        } else if (strcmp(argv[i], "-s") == 0) {
            print_stdout_csv = true;
        } else if (strcmp(argv[i], "-h") == 0 || strcmp(argv[i], "--help") == 0) {
            print_usage(argv[0]);
            return 0;
        } else {
            fprintf(stderr, "Unknown or incomplete option: %s\n", argv[i]);
            print_usage(argv[0]);
            return 1;
        }
    }

    if (config.iterations == 0) {
        fprintf(stderr, "Error: iterations must be greater than 0\n");
        return 1;
    }

    workload_record_t *records = (workload_record_t *)calloc(config.iterations, sizeof(workload_record_t));
    if (records == NULL) {
        fprintf(stderr, "Error: failed to allocate memory for %u records\n", config.iterations);
        return 1;
    }

    size_t actual_records = 0;
    workload_error_t err = workload_execute(&config, records, config.iterations, &actual_records);
    if (err != WORKLOAD_OK) {
        fprintf(stderr, "Error: workload execution failed with code %d\n", err);
        free(records);
        return 1;
    }

    if (print_stdout_csv) {
        workload_write_csv(stdout, records, actual_records);
    } else {
        /* Print brief execution summary to stderr/stdout */
        uint64_t total_latency_ns = 0;
        uint64_t min_latency_ns = UINT64_MAX;
        uint64_t max_latency_ns = 0;

        for (size_t i = 0; i < actual_records; ++i) {
            total_latency_ns += records[i].latency_ns;
            if (records[i].latency_ns < min_latency_ns) {
                min_latency_ns = records[i].latency_ns;
            }
            if (records[i].latency_ns > max_latency_ns) {
                max_latency_ns = records[i].latency_ns;
            }
        }

        double avg_ms = (actual_records > 0) ? ((double)total_latency_ns / (double)actual_records) / 1e6 : 0.0;
        double min_ms = (actual_records > 0) ? (double)min_latency_ns / 1e6 : 0.0;
        double max_ms = (actual_records > 0) ? (double)max_latency_ns / 1e6 : 0.0;

        printf("Workload execution complete:\n");
        printf("  Warmup iterations: %u (excluded from stats)\n", config.warmup_iterations);
        printf("  Measured iterations: %zu\n", actual_records);
        printf("  Latency (min/avg/max): %.3f / %.3f / %.3f ms\n", min_ms, avg_ms, max_ms);
        if (config.csv_output_path != NULL) {
            printf("  Wrote CSV output to: %s\n", config.csv_output_path);
        }
    }

    free(records);
    return 0;
}
