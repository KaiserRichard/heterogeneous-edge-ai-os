#include "workload.h"
#include "timing.h"
#include "test_common.h"
#include <string.h>

static void test_timing_monotonicity(void) {
    printf("Running: %s...\n", __func__);
    uint64_t t1 = timing_get_monotonic_ns();
    TEST_ASSERT(t1 > 0);

    /* Back-to-back read contract: non-decreasing */
    uint64_t t2 = timing_get_monotonic_ns();
    TEST_ASSERT(t2 >= t1);

    /* Elapsed duration measurement after sleep */
    timing_sleep_ns(5000000ULL); /* 5 ms */
    uint64_t t3 = timing_get_monotonic_ns();

    TEST_ASSERT(t3 > t2);
    uint64_t diff = t3 - t2;
    /* Sleep should be at least ~4 ms */
    TEST_ASSERT(diff >= 4000000ULL);
}

static void test_workload_execution_and_warmup(void) {
    printf("Running: %s...\n", __func__);
    workload_config_t cfg;
    workload_config_init_default(&cfg);
    cfg.iterations = 10;
    cfg.warmup_iterations = 3;
    cfg.intensity = 50;
    cfg.interval_ms = 0;
    cfg.csv_output_path = NULL;

    workload_record_t records[10];
    size_t actual_records = 0;

    workload_error_t err = workload_execute(&cfg, records, 10, &actual_records);
    TEST_ASSERT_EQ(err, WORKLOAD_OK);
    TEST_ASSERT_EQ(actual_records, 10);

    /* Verify sequence IDs start at 1, increase monotonically, and timing is non-decreasing */
    for (size_t i = 0; i < actual_records; ++i) {
        TEST_ASSERT_EQ(records[i].sequence_id, (uint64_t)(i + 1));
        TEST_ASSERT(records[i].workload_start_ns > 0);
        TEST_ASSERT(records[i].workload_end_ns >= records[i].workload_start_ns);
        TEST_ASSERT_EQ(records[i].latency_ns, records[i].workload_end_ns - records[i].workload_start_ns);
        TEST_ASSERT_EQ(records[i].valid, true);

        if (i > 0) {
            TEST_ASSERT(records[i].workload_start_ns >= records[i - 1].workload_start_ns);
        }
    }

    /* Overall workload sequence took measurable elapsed duration */
    TEST_ASSERT(records[actual_records - 1].workload_end_ns > records[0].workload_start_ns);
}

static void test_workload_csv_output(void) {
    printf("Running: %s...\n", __func__);
    const char *csv_path = "test_workload_output.csv";

    workload_config_t cfg;
    workload_config_init_default(&cfg);
    cfg.iterations = 5;
    cfg.warmup_iterations = 2;
    cfg.intensity = 20;
    cfg.csv_output_path = csv_path;

    workload_record_t records[5];
    size_t actual_records = 0;

    workload_error_t err = workload_execute(&cfg, records, 5, &actual_records);
    TEST_ASSERT_EQ(err, WORKLOAD_OK);
    TEST_ASSERT_EQ(actual_records, 5);

    /* Read back CSV and verify content */
    FILE *fp = fopen(csv_path, "r");
    TEST_ASSERT(fp != NULL);

    if (fp != NULL) {
        char line[256];
        /* Check header line */
        TEST_ASSERT(fgets(line, sizeof(line), fp) != NULL);
        TEST_ASSERT(strcmp(line, "sequence_id,workload_start_ns,workload_end_ns,latency_ns,valid\n") == 0);

        /* Check 5 data lines */
        size_t lines_read = 0;
        while (fgets(line, sizeof(line), fp) != NULL) {
            uint64_t seq = 0, start = 0, end = 0, lat = 0;
            int valid = 0;
            int parsed = sscanf(line, "%llu,%llu,%llu,%llu,%d", &seq, &start, &end, &lat, &valid);
            TEST_ASSERT_EQ(parsed, 5);
            TEST_ASSERT_EQ(seq, (uint64_t)(lines_read + 1));
            TEST_ASSERT_EQ(valid, 1);
            lines_read++;
        }
        TEST_ASSERT_EQ(lines_read, 5);
        fclose(fp);
        remove(csv_path);
    }
}

static void test_workload_error_handling(void) {
    printf("Running: %s...\n", __func__);
    workload_record_t records[10];
    size_t actual = 0;

    /* NULL config */
    TEST_ASSERT_EQ(workload_execute(NULL, records, 10, &actual), WORKLOAD_ERR_INVALID_ARG);

    /* Zero iterations */
    workload_config_t cfg;
    workload_config_init_default(&cfg);
    cfg.iterations = 0;
    TEST_ASSERT_EQ(workload_execute(&cfg, records, 10, &actual), WORKLOAD_ERR_INVALID_ARG);

    /* Capacity smaller than iterations */
    cfg.iterations = 10;
    TEST_ASSERT_EQ(workload_execute(&cfg, records, 5, &actual), WORKLOAD_ERR_INVALID_ARG);
}

int main(void) {
    printf("=== Starting Linux Workload Unit Tests ===\n");
    test_timing_monotonicity();
    test_workload_execution_and_warmup();
    test_workload_csv_output();
    test_workload_error_handling();
    TEST_REPORT();
    return (g_test_failures == 0) ? 0 : 1;
}
