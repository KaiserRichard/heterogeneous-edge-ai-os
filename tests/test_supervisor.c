#include "supervisor.h"
#include "test_common.h"

static void test_supervisor_sequence_wrap_around(void) {
    printf("Running: %s...\n", __func__);

    /* 1. Direct unit tests of sequence comparison */
    /* 0xFFFFFFFE -> 0xFFFFFFFF (delta = 1) */
    TEST_ASSERT_EQ(supervisor_seq_compare(0xFFFFFFFFU, 0xFFFFFFFEU), SUPERVISOR_SEQ_NEWER);

    /* 0xFFFFFFFF -> 0x00000000 (delta = 1 with unsigned 32-bit overflow) */
    TEST_ASSERT_EQ(supervisor_seq_compare(0x00000000U, 0xFFFFFFFFU), SUPERVISOR_SEQ_NEWER);

    /* 0x00000000 <- 0xFFFFFFFF (current = 0xFFFFFFFF, last = 0x00000000; delta = 0xFFFFFFFF > 2^31) */
    TEST_ASSERT_EQ(supervisor_seq_compare(0xFFFFFFFFU, 0x00000000U), SUPERVISOR_SEQ_OLDER);

    /* Duplicate sequence (delta == 0) */
    TEST_ASSERT_EQ(supervisor_seq_compare(10U, 10U), SUPERVISOR_SEQ_DUPLICATE);
    TEST_ASSERT_EQ(supervisor_seq_compare(0xFFFFFFFFU, 0xFFFFFFFFU), SUPERVISOR_SEQ_DUPLICATE);

    /* Boundary: delta == 2^31 - 1 (newer) */
    TEST_ASSERT_EQ(supervisor_seq_compare(0x7FFFFFFFU, 0x00000000U), SUPERVISOR_SEQ_NEWER);

    /* Boundary: delta == 2^31 (ambiguous / half-range boundary) */
    TEST_ASSERT_EQ(supervisor_seq_compare(0x80000000U, 0x00000000U), SUPERVISOR_SEQ_AMBIGUOUS);

    /* Boundary: delta == 2^31 + 1 (older) */
    TEST_ASSERT_EQ(supervisor_seq_compare(0x80000001U, 0x00000000U), SUPERVISOR_SEQ_OLDER);

    /* 2. State machine handling of sequence wrap-around */
    supervisor_t sv;
    supervisor_init(&sv, NULL);

    supervisor_input_t input = {
        .result_arrived = true,
        .sequence_id = 0xFFFFFFFFU,
        .is_valid = true,
        .current_time_ticks = 100
    };
    supervisor_update(&sv, &input);
    TEST_ASSERT_EQ(sv.state, SUPERVISOR_STATE_FRESH);
    TEST_ASSERT_EQ(sv.last_sequence_id, 0xFFFFFFFFU);
    TEST_ASSERT_EQ(sv.last_valid_time_ticks, 100);

    /* Next packet arrives at seq = 0x00000000 (wrapped around) */
    input.sequence_id = 0x00000000U;
    input.current_time_ticks = 120;
    supervisor_state_t st = supervisor_update(&sv, &input);
    TEST_ASSERT_EQ(st, SUPERVISOR_STATE_FRESH);
    TEST_ASSERT_EQ(sv.last_transition_reason, SUPERVISOR_REASON_DATA_FRESH);
    TEST_ASSERT_EQ(sv.last_sequence_id, 0x00000000U);
    TEST_ASSERT_EQ(sv.last_valid_time_ticks, 120);

    /* Ambiguous packet at exactly 2^31 delta: not accepted as newer, timestamp not updated */
    input.sequence_id = 0x80000000U;
    input.current_time_ticks = 140;
    st = supervisor_update(&sv, &input);
    TEST_ASSERT_EQ(st, SUPERVISOR_STATE_FRESH);
    TEST_ASSERT_EQ(sv.last_transition_reason, SUPERVISOR_REASON_STALE_SEQUENCE);
    TEST_ASSERT_EQ(sv.last_sequence_id, 0x00000000U);
    TEST_ASSERT_EQ(sv.last_valid_time_ticks, 120);
}

static void test_supervisor_startup_no_result(void) {
    printf("Running: %s...\n", __func__);
    supervisor_t sv;
    supervisor_init(&sv, NULL);

    TEST_ASSERT_EQ(sv.state, SUPERVISOR_STATE_INIT);
    TEST_ASSERT_EQ(sv.has_received_first_valid, false);

    supervisor_input_t input = {
        .result_arrived = false,
        .sequence_id = 0,
        .is_valid = false,
        .current_time_ticks = 0
    };

    /* Cycle multiple times with no input */
    for (uint64_t t = 10; t <= 500; t += 50) {
        input.current_time_ticks = t;
        supervisor_state_t st = supervisor_update(&sv, &input);
        TEST_ASSERT_EQ(st, SUPERVISOR_STATE_INIT);
    }
}

static void test_supervisor_first_fresh_result(void) {
    printf("Running: %s...\n", __func__);
    supervisor_t sv;
    supervisor_init(&sv, NULL);

    supervisor_input_t input = {
        .result_arrived = true,
        .sequence_id = 100,
        .is_valid = true,
        .current_time_ticks = 1000
    };

    supervisor_state_t st = supervisor_update(&sv, &input);
    TEST_ASSERT_EQ(st, SUPERVISOR_STATE_FRESH);
    TEST_ASSERT_EQ(sv.last_transition_reason, SUPERVISOR_REASON_FIRST_VALID_DATA);
    TEST_ASSERT_EQ(sv.last_sequence_id, 100);
    TEST_ASSERT_EQ(sv.last_valid_time_ticks, 1000);
    TEST_ASSERT_EQ(sv.has_received_first_valid, true);
}

static void test_supervisor_repeated_fresh_results(void) {
    printf("Running: %s...\n", __func__);
    supervisor_t sv;
    supervisor_init(&sv, NULL);

    supervisor_input_t input = {
        .result_arrived = true,
        .sequence_id = 1,
        .is_valid = true,
        .current_time_ticks = 100
    };
    supervisor_update(&sv, &input);
    TEST_ASSERT_EQ(sv.state, SUPERVISOR_STATE_FRESH);

    /* Subsequent timely packets */
    for (uint32_t seq = 2; seq <= 10; ++seq) {
        input.sequence_id = seq;
        input.current_time_ticks += 20; /* Within fresh_timeout_ticks (100) */
        supervisor_state_t st = supervisor_update(&sv, &input);
        TEST_ASSERT_EQ(st, SUPERVISOR_STATE_FRESH);
        TEST_ASSERT_EQ(sv.last_transition_reason, SUPERVISOR_REASON_DATA_FRESH);
        TEST_ASSERT_EQ(sv.last_sequence_id, seq);
    }
}

static void test_supervisor_duplicate_and_older_sequence(void) {
    printf("Running: %s...\n", __func__);
    supervisor_config_t cfg;
    supervisor_config_init_default(&cfg);
    cfg.fresh_timeout_ticks = 100;
    cfg.failsafe_timeout_ticks = 300;

    supervisor_t sv;
    supervisor_init(&sv, &cfg);

    /* Send initial valid packet at t=100 with seq=50 */
    supervisor_input_t input = {
        .result_arrived = true,
        .sequence_id = 50,
        .is_valid = true,
        .current_time_ticks = 100
    };
    supervisor_update(&sv, &input);
    TEST_ASSERT_EQ(sv.state, SUPERVISOR_STATE_FRESH);

    /* 1. Duplicate packet at t=130 (age = 30 < 100): does not force HOLD, remains FRESH */
    input.sequence_id = 50;
    input.current_time_ticks = 130;
    supervisor_state_t st = supervisor_update(&sv, &input);
    TEST_ASSERT_EQ(st, SUPERVISOR_STATE_FRESH);
    TEST_ASSERT_EQ(sv.last_transition_reason, SUPERVISOR_REASON_DUPLICATE_SEQUENCE);
    /* last_valid_time_ticks must NOT advance */
    TEST_ASSERT_EQ(sv.last_valid_time_ticks, 100);

    /* 2. Older packet (seq=40) at t=150 (age = 50 < 100): does not force HOLD, remains FRESH */
    input.sequence_id = 40;
    input.current_time_ticks = 150;
    st = supervisor_update(&sv, &input);
    TEST_ASSERT_EQ(st, SUPERVISOR_STATE_FRESH);
    TEST_ASSERT_EQ(sv.last_transition_reason, SUPERVISOR_REASON_STALE_SEQUENCE);
    /* last_valid_time_ticks must NOT advance */
    TEST_ASSERT_EQ(sv.last_valid_time_ticks, 100);

    /* 3. At t=210 (elapsed 110 >= fresh_timeout 100), duplicate/older arrives: degrades to HOLD */
    input.sequence_id = 50;
    input.current_time_ticks = 210;
    st = supervisor_update(&sv, &input);
    TEST_ASSERT_EQ(st, SUPERVISOR_STATE_HOLD);
    TEST_ASSERT_EQ(sv.last_transition_reason, SUPERVISOR_REASON_FRESHNESS_DEADLINE_MISSED);
}

static void test_supervisor_temporary_missing_result(void) {
    printf("Running: %s...\n", __func__);
    supervisor_config_t cfg;
    supervisor_config_init_default(&cfg);
    cfg.fresh_timeout_ticks = 100;
    cfg.failsafe_timeout_ticks = 300;

    supervisor_t sv;
    supervisor_init(&sv, &cfg);

    /* First packet at t=100 */
    supervisor_input_t input = {
        .result_arrived = true,
        .sequence_id = 1,
        .is_valid = true,
        .current_time_ticks = 100
    };
    supervisor_update(&sv, &input);
    TEST_ASSERT_EQ(sv.state, SUPERVISOR_STATE_FRESH);

    /* Cycle at t=150 with no packet (elapsed 50 < 100): stays FRESH */
    input.result_arrived = false;
    input.current_time_ticks = 150;
    supervisor_state_t st = supervisor_update(&sv, &input);
    TEST_ASSERT_EQ(st, SUPERVISOR_STATE_FRESH);

    /* Cycle at t=205 with no packet (elapsed 105 >= 100): transitions to HOLD */
    input.current_time_ticks = 205;
    st = supervisor_update(&sv, &input);
    TEST_ASSERT_EQ(st, SUPERVISOR_STATE_HOLD);
    TEST_ASSERT_EQ(sv.last_transition_reason, SUPERVISOR_REASON_FRESHNESS_DEADLINE_MISSED);

    /* New packet arrives at t=240 before failsafe timeout (elapsed 140 < 300) */
    input.result_arrived = true;
    input.sequence_id = 2;
    input.is_valid = true;
    input.current_time_ticks = 240;
    st = supervisor_update(&sv, &input);
    TEST_ASSERT_EQ(st, SUPERVISOR_STATE_FRESH);
    TEST_ASSERT_EQ(sv.last_transition_reason, SUPERVISOR_REASON_DATA_FRESH);
    TEST_ASSERT_EQ(sv.last_sequence_id, 2);
    TEST_ASSERT_EQ(sv.last_valid_time_ticks, 240);
}

static void test_supervisor_timeout_to_failsafe(void) {
    printf("Running: %s...\n", __func__);
    supervisor_config_t cfg;
    supervisor_config_init_default(&cfg);
    cfg.fresh_timeout_ticks = 100;
    cfg.failsafe_timeout_ticks = 300;

    supervisor_t sv;
    supervisor_init(&sv, &cfg);

    /* Initial packet at t=100 */
    supervisor_input_t input = {
        .result_arrived = true,
        .sequence_id = 1,
        .is_valid = true,
        .current_time_ticks = 100
    };
    supervisor_update(&sv, &input);
    TEST_ASSERT_EQ(sv.state, SUPERVISOR_STATE_FRESH);

    /* Advance time without packets to exceed fresh timeout */
    input.result_arrived = false;
    input.current_time_ticks = 210;
    supervisor_state_t st = supervisor_update(&sv, &input);
    TEST_ASSERT_EQ(st, SUPERVISOR_STATE_HOLD);

    /* Advance time past failsafe timeout (t=405, elapsed 305 >= 300) */
    input.current_time_ticks = 405;
    st = supervisor_update(&sv, &input);
    TEST_ASSERT_EQ(st, SUPERVISOR_STATE_FAILSAFE);
    TEST_ASSERT_EQ(sv.last_transition_reason, SUPERVISOR_REASON_FAILSAFE_TIMEOUT);

    /* Further idle cycles remain in FAILSAFE */
    input.current_time_ticks = 500;
    st = supervisor_update(&sv, &input);
    TEST_ASSERT_EQ(st, SUPERVISOR_STATE_FAILSAFE);
}

static void test_supervisor_recovery(void) {
    printf("Running: %s...\n", __func__);
    supervisor_config_t cfg;
    supervisor_config_init_default(&cfg);
    cfg.fresh_timeout_ticks = 100;
    cfg.failsafe_timeout_ticks = 300;
    cfg.recovery_valid_required = 1;

    supervisor_t sv;
    supervisor_init(&sv, &cfg);

    /* Force supervisor into FAILSAFE via timeout */
    supervisor_input_t input = {
        .result_arrived = true,
        .sequence_id = 10,
        .is_valid = true,
        .current_time_ticks = 100
    };
    supervisor_update(&sv, &input);

    input.result_arrived = false;
    input.current_time_ticks = 450;
    supervisor_state_t st = supervisor_update(&sv, &input);
    TEST_ASSERT_EQ(st, SUPERVISOR_STATE_FAILSAFE);

    /* Recover with fresh valid packet */
    input.result_arrived = true;
    input.sequence_id = 11;
    input.is_valid = true;
    input.current_time_ticks = 500;
    st = supervisor_update(&sv, &input);
    TEST_ASSERT_EQ(st, SUPERVISOR_STATE_FRESH);
    TEST_ASSERT_EQ(sv.last_transition_reason, SUPERVISOR_REASON_RECOVERED);
    TEST_ASSERT_EQ(sv.last_sequence_id, 11);
    TEST_ASSERT_EQ(sv.last_valid_time_ticks, 500);
}

static void test_supervisor_invalid_input_timeout_model(void) {
    printf("Running: %s...\n", __func__);
    supervisor_config_t cfg;
    supervisor_config_init_default(&cfg);
    /* Default max_consecutive_invalid == 0 (pure minimal freshness/timeout model) */
    TEST_ASSERT_EQ(cfg.max_consecutive_invalid, 0);
    cfg.fresh_timeout_ticks = 100;
    cfg.failsafe_timeout_ticks = 300;

    supervisor_t sv;
    supervisor_init(&sv, &cfg);

    /* First valid packet at t=100 */
    supervisor_input_t input = {
        .result_arrived = true,
        .sequence_id = 1,
        .is_valid = true,
        .current_time_ticks = 100
    };
    supervisor_update(&sv, &input);
    TEST_ASSERT_EQ(sv.state, SUPERVISOR_STATE_FRESH);

    /* Multiple invalid packets arrive within freshness window (t < 200) */
    for (uint64_t t = 120; t <= 180; t += 20) {
        input.sequence_id++;
        input.is_valid = false;
        input.current_time_ticks = t;
        supervisor_state_t st = supervisor_update(&sv, &input);
        /* In minimal timeout model, does not trip immediately; remains FRESH because elapsed < 100 */
        TEST_ASSERT_EQ(st, SUPERVISOR_STATE_FRESH);
        TEST_ASSERT_EQ(sv.last_valid_time_ticks, 100);
    }

    /* Invalid packet arrives at t=210 (elapsed 110 >= 100): degrades to HOLD */
    input.current_time_ticks = 210;
    input.is_valid = false;
    supervisor_state_t st = supervisor_update(&sv, &input);
    TEST_ASSERT_EQ(st, SUPERVISOR_STATE_HOLD);
    TEST_ASSERT_EQ(sv.last_transition_reason, SUPERVISOR_REASON_FRESHNESS_DEADLINE_MISSED);

    /* Invalid packet arrives at t=405 (elapsed 305 >= 300): degrades to FAILSAFE */
    input.current_time_ticks = 405;
    st = supervisor_update(&sv, &input);
    TEST_ASSERT_EQ(st, SUPERVISOR_STATE_FAILSAFE);
    TEST_ASSERT_EQ(sv.last_transition_reason, SUPERVISOR_REASON_FAILSAFE_TIMEOUT);
}

static void test_supervisor_invalid_input_burst_policy(void) {
    printf("Running: %s...\n", __func__);
    supervisor_config_t cfg;
    supervisor_config_init_default(&cfg);
    /* Enable provisional fast-trip fault burst policy */
    cfg.max_consecutive_invalid = 3;

    supervisor_t sv;
    supervisor_init(&sv, &cfg);

    /* First valid packet */
    supervisor_input_t input = {
        .result_arrived = true,
        .sequence_id = 1,
        .is_valid = true,
        .current_time_ticks = 100
    };
    supervisor_update(&sv, &input);
    TEST_ASSERT_EQ(sv.state, SUPERVISOR_STATE_FRESH);

    /* 1st invalid packet */
    input.sequence_id = 2;
    input.is_valid = false;
    input.current_time_ticks = 120;
    supervisor_state_t st = supervisor_update(&sv, &input);
    TEST_ASSERT_EQ(st, SUPERVISOR_STATE_FRESH);
    TEST_ASSERT_EQ(sv.consecutive_invalid_count, 1);

    /* 2nd invalid packet */
    input.sequence_id = 3;
    input.current_time_ticks = 140;
    st = supervisor_update(&sv, &input);
    TEST_ASSERT_EQ(st, SUPERVISOR_STATE_FRESH);
    TEST_ASSERT_EQ(sv.consecutive_invalid_count, 2);

    /* 3rd invalid packet triggers immediate FAILSAFE under provisional policy */
    input.sequence_id = 4;
    input.current_time_ticks = 160;
    st = supervisor_update(&sv, &input);
    TEST_ASSERT_EQ(st, SUPERVISOR_STATE_FAILSAFE);
    TEST_ASSERT_EQ(sv.last_transition_reason, SUPERVISOR_REASON_INVALID_DATA_BURST);
    TEST_ASSERT_EQ(sv.consecutive_invalid_count, 3);
}

int main(void) {
    printf("=== Starting Supervisor Unit Tests ===\n");
    test_supervisor_sequence_wrap_around();
    test_supervisor_startup_no_result();
    test_supervisor_first_fresh_result();
    test_supervisor_repeated_fresh_results();
    test_supervisor_duplicate_and_older_sequence();
    test_supervisor_temporary_missing_result();
    test_supervisor_timeout_to_failsafe();
    test_supervisor_recovery();
    test_supervisor_invalid_input_timeout_model();
    test_supervisor_invalid_input_burst_policy();
    TEST_REPORT();
    return (g_test_failures == 0) ? 0 : 1;
}
