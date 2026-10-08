#include "supervisor_protocol.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static unsigned checks;
#define CHECK(expr) do { ++checks; if (!(expr)) { \
    fprintf(stderr, "%s:%d: %s\n", __FILE__, __LINE__, #expr); exit(1); \
} } while (0)

/* Synthetic ticks, not hardware-calibrated deadlines. */
static const supervisor_config_t config = {50u, 30u, 90u, 20u};

static void init(supervisor_t *sv)
{
    CHECK(supervisor_init(sv, &config, 0u));
}

static supervisor_state_t event(supervisor_t *sv, supervisor_event_kind_t kind,
                                uint16_t wire, uint32_t input, uint64_t now)
{
    supervisor_event_t e = {kind, true, wire, input, now};
    return supervisor_update(sv, &e, now);
}

static void ready(supervisor_t *sv)
{
    init(sv);
    CHECK(event(sv, SUPERVISOR_EVENT_HEARTBEAT, 0u, 0u, 0u) == SUPERVISOR_STATE_INIT);
    CHECK(event(sv, SUPERVISOR_EVENT_RESULT, 1u, 0u, 1u) == SUPERVISOR_STATE_FRESH);
}

static void test_sequence_boundaries(void)
{
    CHECK(supervisor_seq_compare16(7u, 7u) == SUPERVISOR_SEQ_DUPLICATE);
    CHECK(supervisor_seq_compare16(8u, 7u) == SUPERVISOR_SEQ_NEWER);
    CHECK(supervisor_seq_compare16(6u, 7u) == SUPERVISOR_SEQ_OLDER);
    CHECK(supervisor_seq_compare16(32768u, 0u) == SUPERVISOR_SEQ_AMBIGUOUS);
    CHECK(supervisor_seq_compare16(32767u, 0u) == SUPERVISOR_SEQ_NEWER);
    CHECK(supervisor_seq_compare16(32769u, 0u) == SUPERVISOR_SEQ_OLDER);
    CHECK(supervisor_seq_compare(0u, UINT32_MAX) == SUPERVISOR_SEQ_NEWER);
    CHECK(supervisor_seq_compare(UINT32_MAX, 0u) == SUPERVISOR_SEQ_OLDER);
    CHECK(supervisor_seq_compare(UINT32_C(0x80000000), 0u) == SUPERVISOR_SEQ_AMBIGUOUS);
    CHECK(supervisor_seq_compare(UINT32_C(0x7fffffff), 0u) == SUPERVISOR_SEQ_NEWER);
    CHECK(supervisor_seq_compare(UINT32_C(0x80000001), 0u) == SUPERVISOR_SEQ_OLDER);
    CHECK(supervisor_seq_compare(10u, 10u) == SUPERVISOR_SEQ_DUPLICATE);
    for (uint32_t s = 0u; s <= UINT16_MAX; ++s) {
        CHECK(supervisor_seq_compare16((uint16_t)(s + 1u), (uint16_t)s) == SUPERVISOR_SEQ_NEWER);
    }
}

static void test_configuration_and_startup(void)
{
    supervisor_t sv;
    CHECK(!supervisor_init(NULL, &config, 0u));
    CHECK(!supervisor_init(&sv, NULL, 0u));
    CHECK(sv.state == SUPERVISOR_STATE_FAILSAFE);
    CHECK(!supervisor_rearm(&sv, 100u));
    supervisor_config_t invalid = config;
    invalid.result_failsafe_ticks = invalid.result_hold_ticks;
    CHECK(!supervisor_init(&sv, &invalid, 0u));
    invalid = config; invalid.heartbeat_timeout_ticks = 0u;
    CHECK(!supervisor_init(&sv, &invalid, 0u));
    invalid = config; invalid.result_hold_ticks = 0u;
    CHECK(!supervisor_init(&sv, &invalid, 0u));
    invalid = config; invalid.rearm_healthy_ticks = 0u;
    CHECK(!supervisor_init(&sv, &invalid, 0u));
    init(&sv);
    CHECK(supervisor_update(&sv, NULL, 10000u) == SUPERVISOR_STATE_INIT);
    CHECK(!supervisor_rearm(&sv, 10000u));
    CHECK(event(&sv, SUPERVISOR_EVENT_RESULT, 0u, 1u, 10001u) == SUPERVISOR_STATE_INIT);
    CHECK(event(&sv, SUPERVISOR_EVENT_HEARTBEAT, 1u, 0u, 10032u) == SUPERVISOR_STATE_INIT);
    CHECK(event(&sv, SUPERVISOR_EVENT_RESULT, 2u, 2u, 10033u) == SUPERVISOR_STATE_FRESH);
    CHECK(supervisor_update(NULL, NULL, 0u) == SUPERVISOR_STATE_FAILSAFE);
    CHECK(!supervisor_rearm(NULL, 0u));
}

static void test_heartbeat_loss_and_expiry_precedence(void)
{
    supervisor_t sv;
    ready(&sv);
    CHECK(event(&sv, SUPERVISOR_EVENT_RESULT, 2u, 1u, 25u) == SUPERVISOR_STATE_FRESH);
    CHECK(event(&sv, SUPERVISOR_EVENT_RESULT, 3u, 2u, 49u) == SUPERVISOR_STATE_FRESH);
    /* Heartbeat at exact expiry must not hide the previously expired deadline. */
    CHECK(event(&sv, SUPERVISOR_EVENT_HEARTBEAT, 4u, 0u, 50u) == SUPERVISOR_STATE_FAILSAFE);
    CHECK(sv.last_transition_reason == SUPERVISOR_REASON_HEARTBEAT_TIMEOUT);
    CHECK(sv.last_heartbeat_ticks == 50u && sv.last_result_ticks == 49u);
    CHECK(event(&sv, SUPERVISOR_EVENT_RESULT, 5u, 3u, 51u) == SUPERVISOR_STATE_FAILSAFE);
    CHECK(!supervisor_rearm(&sv, 69u));
    CHECK(supervisor_rearm(&sv, 70u));
    CHECK(sv.state == SUPERVISOR_STATE_INIT);
    CHECK(sv.last_transition_reason == SUPERVISOR_REASON_REARM);
    CHECK(!sv.has_heartbeat && !sv.has_result && !sv.healthy_interval);
    /* Rearm preserves anti-replay history; cached traffic cannot arm output. */
    CHECK(event(&sv, SUPERVISOR_EVENT_HEARTBEAT, 4u, 0u, 70u) == SUPERVISOR_STATE_INIT);
    CHECK(!sv.has_heartbeat);
    CHECK(event(&sv, SUPERVISOR_EVENT_HEARTBEAT, 6u, 0u, 71u) == SUPERVISOR_STATE_INIT);
    CHECK(event(&sv, SUPERVISOR_EVENT_RESULT, 7u, 3u, 72u) == SUPERVISOR_STATE_INIT);
    CHECK(!sv.has_result);
    CHECK(event(&sv, SUPERVISOR_EVENT_RESULT, 8u, 4u, 73u) == SUPERVISOR_STATE_FRESH);
}

static void test_result_silence_and_hold_recovery(void)
{
    supervisor_t sv;
    ready(&sv);
    CHECK(supervisor_update(&sv, NULL, 30u) == SUPERVISOR_STATE_FRESH);
    CHECK(supervisor_update(&sv, NULL, 31u) == SUPERVISOR_STATE_HOLD);
    CHECK(sv.last_transition_reason == SUPERVISOR_REASON_RESULT_SILENCE);
    CHECK(event(&sv, SUPERVISOR_EVENT_RESULT, 2u, 1u, 32u) == SUPERVISOR_STATE_FRESH);
    CHECK(event(&sv, SUPERVISOR_EVENT_HEARTBEAT, 3u, 0u, 40u) == SUPERVISOR_STATE_FRESH);
    CHECK(supervisor_update(&sv, NULL, 62u) == SUPERVISOR_STATE_HOLD);
    CHECK(event(&sv, SUPERVISOR_EVENT_HEARTBEAT, 4u, 0u, 80u) == SUPERVISOR_STATE_HOLD);
    CHECK(event(&sv, SUPERVISOR_EVENT_HEARTBEAT, 5u, 0u, 120u) == SUPERVISOR_STATE_HOLD);
    /* Receipt silence at 90 ticks wins over a new result at the same instant. */
    CHECK(event(&sv, SUPERVISOR_EVENT_RESULT, 6u, 2u, 122u) == SUPERVISOR_STATE_FAILSAFE);
    CHECK(sv.last_transition_reason == SUPERVISOR_REASON_RESULT_TIMEOUT);
    CHECK(event(&sv, SUPERVISOR_EVENT_RESULT, 7u, 3u, 123u) == SUPERVISOR_STATE_FAILSAFE);
    CHECK(!supervisor_rearm(&sv, 141u));
    CHECK(supervisor_rearm(&sv, 142u));
}

static void test_loss_while_hold_and_health_gap(void)
{
    supervisor_t sv;
    ready(&sv);
    CHECK(supervisor_update(&sv, NULL, 31u) == SUPERVISOR_STATE_HOLD);
    CHECK(supervisor_update(&sv, NULL, 50u) == SUPERVISOR_STATE_FAILSAFE);
    CHECK(sv.last_transition_reason == SUPERVISOR_REASON_HEARTBEAT_TIMEOUT);
    CHECK(!supervisor_rearm(&sv, 500u));
    CHECK(event(&sv, SUPERVISOR_EVENT_HEARTBEAT, 2u, 0u, 501u) == SUPERVISOR_STATE_FAILSAFE);
    CHECK(!sv.healthy_interval);
    CHECK(event(&sv, SUPERVISOR_EVENT_RESULT, 3u, 1u, 502u) == SUPERVISOR_STATE_FAILSAFE);
    CHECK(sv.healthy_since_ticks == 502u);
    /* Configure a healthy interval longer than one receipt deadline. */
    sv.config.rearm_healthy_ticks = 60u;
    CHECK(event(&sv, SUPERVISOR_EVENT_HEARTBEAT, 4u, 0u, 520u) == SUPERVISOR_STATE_FAILSAFE);
    CHECK(event(&sv, SUPERVISOR_EVENT_RESULT, 5u, 2u, 532u) == SUPERVISOR_STATE_FAILSAFE);
    CHECK(sv.healthy_since_ticks == 532u); /* Exact result expiry reset. */
    CHECK(!supervisor_rearm(&sv, 550u));
    CHECK(event(&sv, SUPERVISOR_EVENT_RESULT, 6u, 3u, 551u) == SUPERVISOR_STATE_FAILSAFE);
    CHECK(event(&sv, SUPERVISOR_EVENT_HEARTBEAT, 7u, 0u, 560u) == SUPERVISOR_STATE_FAILSAFE);
    CHECK(event(&sv, SUPERVISOR_EVENT_RESULT, 8u, 4u, 575u) == SUPERVISOR_STATE_FAILSAFE);
    CHECK(!supervisor_rearm(&sv, 591u));
    CHECK(supervisor_rearm(&sv, 592u));
}

static void test_duplicates_replays_and_invalid_events(void)
{
    supervisor_t sv;
    ready(&sv);
    CHECK(event(&sv, SUPERVISOR_EVENT_HEARTBEAT, 1u, 0u, 5u) == SUPERVISOR_STATE_FRESH);
    CHECK(sv.last_heartbeat_ticks == 0u);
    CHECK(event(&sv, SUPERVISOR_EVENT_RESULT, 0u, 2u, 6u) == SUPERVISOR_STATE_FRESH);
    CHECK(sv.last_result_ticks == 1u);
    CHECK(event(&sv, SUPERVISOR_EVENT_HEARTBEAT, 32769u, 0u, 7u) == SUPERVISOR_STATE_FRESH);
    CHECK(sv.last_heartbeat_ticks == 0u && sv.last_wire_seq == 1u);
    CHECK(event(&sv, SUPERVISOR_EVENT_RESULT, 2u, 0u, 8u) == SUPERVISOR_STATE_FRESH);
    CHECK(sv.last_wire_seq == 2u && sv.last_result_ticks == 1u);
    CHECK(event(&sv, SUPERVISOR_EVENT_RESULT, 3u, UINT32_MAX, 9u) == SUPERVISOR_STATE_FRESH);
    CHECK(sv.last_result_ticks == 1u);
    CHECK(event(&sv, SUPERVISOR_EVENT_RESULT, 4u, UINT32_C(0x80000000), 10u) == SUPERVISOR_STATE_FRESH);
    CHECK(sv.last_result_ticks == 1u && sv.last_input_seq == 0u);
    supervisor_event_t bad = {SUPERVISOR_EVENT_HEARTBEAT, false, 5u, 0u, 20u};
    CHECK(supervisor_update(&sv, &bad, 20u) == SUPERVISOR_STATE_FRESH);
    CHECK(sv.last_heartbeat_ticks == 0u && sv.last_wire_seq == 4u);
    CHECK(event(&sv, SUPERVISOR_EVENT_OTHER, 5u, 0u, 30u) == SUPERVISOR_STATE_FRESH);
    CHECK(sv.last_result_ticks == 1u && sv.last_heartbeat_ticks == 0u);
    CHECK(event(&sv, SUPERVISOR_EVENT_RESULT, 6u, 0u, 31u) == SUPERVISOR_STATE_HOLD);
    CHECK(supervisor_update(&sv, &bad, 50u) == SUPERVISOR_STATE_FAILSAFE);
}

static void test_wire_and_input_wrap(void)
{
    supervisor_t sv;
    init(&sv);
    CHECK(event(&sv, SUPERVISOR_EVENT_HEARTBEAT, 65534u, 0u, 0u) == SUPERVISOR_STATE_INIT);
    CHECK(event(&sv, SUPERVISOR_EVENT_RESULT, 65535u, UINT32_MAX, 1u) == SUPERVISOR_STATE_FRESH);
    CHECK(event(&sv, SUPERVISOR_EVENT_HEARTBEAT, 0u, 0u, 2u) == SUPERVISOR_STATE_FRESH);
    CHECK(event(&sv, SUPERVISOR_EVENT_RESULT, 1u, 0u, 3u) == SUPERVISOR_STATE_FRESH);
    CHECK(sv.last_result_ticks == 3u && sv.last_input_seq == 0u);
    CHECK(event(&sv, SUPERVISOR_EVENT_RESULT, 65535u, 1u, 4u) == SUPERVISOR_STATE_FRESH);
    CHECK(sv.last_result_ticks == 3u);
}

static void test_clock_regression(void)
{
    supervisor_t sv;
    ready(&sv);
    CHECK(supervisor_update(&sv, NULL, 20u) == SUPERVISOR_STATE_FRESH);
    CHECK(event(&sv, SUPERVISOR_EVENT_HEARTBEAT, 2u, 0u, 19u) == SUPERVISOR_STATE_FAILSAFE);
    CHECK(sv.last_transition_reason == SUPERVISOR_REASON_CLOCK_REGRESSION);
    CHECK(sv.last_time_ticks == 20u && sv.last_heartbeat_ticks == 0u);
    CHECK(!sv.healthy_interval);
    CHECK(!supervisor_rearm(&sv, 19u));
    CHECK(supervisor_update(&sv, NULL, 21u) == SUPERVISOR_STATE_FAILSAFE);
    CHECK(!supervisor_rearm(&sv, 22u));
}

/* Exercise the real encoder/parser. Never fake a CRC-valid delivery. */
static size_t feed(supervisor_t *sv, struct hea_parser *parser,
                   const uint8_t *bytes, size_t len, uint64_t now)
{
    size_t decoded = 0u;
    for (size_t i = 0u; i < len; ++i) {
        if (hea_parser_feed(parser, bytes[i]) != 0) {
            ++decoded;
            (void)supervisor_receive_frame(sv, &parser->frame, now, now);
        }
    }
    (void)supervisor_update(sv, NULL, now);
    return decoded;
}

static size_t inference(uint8_t *out, uint16_t wire, uint32_t input,
                        uint64_t sample, uint64_t done, uint8_t confidence)
{
    struct hea_inference m = {sample, done, input, 1u, confidence};
    uint8_t payload[HEA_MAX_PAYLOAD];
    uint8_t len = hea_pack_inference(&m, payload);
    return hea_encode(HEA_MSG_INFERENCE, wire, payload, len, out, HEA_MAX_FRAME);
}

static void test_parser_crc_and_payload_validation(void)
{
    supervisor_t sv;
    struct hea_parser parser;
    uint8_t out[HEA_MAX_FRAME];
    ready(&sv);
    hea_parser_init(&parser);
    size_t len = inference(out, 2u, 1u, 100u, 120u, 90u);
    /* Every payload/CRC single-bit corruption must leave timers untouched. */
    for (size_t byte = HEA_HEADER_LEN; byte < len; ++byte) {
        for (unsigned bit = 0u; bit < 8u; ++bit) {
            out[byte] ^= (uint8_t)(1u << bit);
            CHECK(feed(&sv, &parser, out, len, 2u) == 0u);
            CHECK(sv.last_result_ticks == 1u && sv.last_heartbeat_ticks == 0u);
            out[byte] ^= (uint8_t)(1u << bit);
        }
    }
    CHECK(parser.stats.crc_errors == (len - HEA_HEADER_LEN) * 8u);
    CHECK(feed(&sv, &parser, out, len, 3u) == 1u);
    CHECK(sv.last_result_ticks == 3u);
    /* New wire sequence with duplicate input does not renew receipt silence. */
    len = inference(out, 3u, 1u, 100u, 120u, 90u);
    CHECK(feed(&sv, &parser, out, len, 4u) == 1u);
    CHECK(sv.last_result_ticks == 3u && sv.last_wire_seq == 3u);
    len = inference(out, 4u, 2u, 100u, 120u, 101u);
    CHECK(feed(&sv, &parser, out, len, 5u) == 1u);
    CHECK(sv.last_wire_seq == 3u && sv.last_result_ticks == 3u);
    len = inference(out, 4u, 2u, 120u, 100u, 90u);
    CHECK(feed(&sv, &parser, out, len, 6u) == 1u);
    CHECK(sv.last_wire_seq == 3u);
    len = hea_encode(HEA_MSG_INFERENCE, 4u, NULL, 0u, out, sizeof(out));
    CHECK(feed(&sv, &parser, out, len, 7u) == 1u);
    CHECK(sv.last_wire_seq == 3u);
    len = hea_encode(0x7fu, 4u, NULL, 0u, out, sizeof(out));
    CHECK(feed(&sv, &parser, out, len, 8u) == 1u);
    CHECK(sv.last_wire_seq == 3u);
    CHECK(supervisor_receive_frame(&sv, NULL, 50u, 50u) == SUPERVISOR_STATE_FAILSAFE);
}

static void test_parser_heartbeat_echo_and_no_cross_clock_math(void)
{
    supervisor_t sv;
    struct hea_parser parser;
    uint8_t out[HEA_MAX_FRAME], payload[HEA_MAX_PAYLOAD];
    struct hea_heartbeat hb = {UINT64_MAX};
    struct hea_echo_req echo = {0u};
    init(&sv);
    hea_parser_init(&parser);
    size_t len = hea_encode(HEA_MSG_HEARTBEAT, 0u, payload,
                            hea_pack_heartbeat(&hb, payload), out, sizeof(out));
    CHECK(feed(&sv, &parser, out, len, 0u) == 1u);
    CHECK(sv.has_heartbeat && sv.last_heartbeat_ticks == 0u);
    len = inference(out, 1u, 0u, UINT64_MAX - 1u, UINT64_MAX, 90u);
    CHECK(feed(&sv, &parser, out, len, 1u) == 1u);
    CHECK(sv.state == SUPERVISOR_STATE_FRESH && sv.last_result_ticks == 1u);
    len = hea_encode(HEA_MSG_ECHO_REQ, 2u, payload,
                    hea_pack_echo_req(&echo, payload), out, sizeof(out));
    CHECK(feed(&sv, &parser, out, len, 20u) == 1u);
    CHECK(sv.last_wire_seq == 2u && sv.last_heartbeat_ticks == 0u);
    CHECK(sv.last_result_ticks == 1u);
    CHECK(feed(&sv, &parser, out, len, 50u) == 1u);
    CHECK(sv.state == SUPERVISOR_STATE_FAILSAFE);
    struct hea_frame bad = parser.frame;
    bad.version = 2u;
    CHECK(supervisor_receive_frame(&sv, &bad, 51u, 51u) == SUPERVISOR_STATE_FAILSAFE);
    CHECK(sv.last_wire_seq == 2u);
}

static void test_backlog_epoch_and_nonzero_clock(void)
{
    supervisor_t sv;
    CHECK(supervisor_init(&sv, &config, UINT64_C(1000000000000)));
    uint64_t base = UINT64_C(1000000000000);
    CHECK(event(&sv, SUPERVISOR_EVENT_HEARTBEAT, 100u, 0u, base) == SUPERVISOR_STATE_INIT);
    CHECK(event(&sv, SUPERVISOR_EVENT_RESULT, 101u, 100u, base + 1u) == SUPERVISOR_STATE_FRESH);
    supervisor_event_t delayed = {SUPERVISOR_EVENT_RESULT, true, 102u, 101u, base + 2u};
    CHECK(supervisor_update(&sv, &delayed, base + 35u) == SUPERVISOR_STATE_HOLD);
    CHECK(sv.last_result_ticks == base + 2u); /* Not processing time! */
    delayed.kind = SUPERVISOR_EVENT_HEARTBEAT;
    delayed.wire_seq = 103u;
    delayed.received_at_ticks = base + 40u;
    CHECK(supervisor_update(&sv, &delayed, base + 45u) == SUPERVISOR_STATE_HOLD);
    delayed.kind = SUPERVISOR_EVENT_RESULT;
    delayed.wire_seq = 104u;
    delayed.input_seq = 102u;
    delayed.received_at_ticks = base + 3u;
    CHECK(supervisor_update(&sv, &delayed, base + 93u) == SUPERVISOR_STATE_FAILSAFE);
    CHECK(!sv.healthy_interval); /* Backlog cannot begin healthy rearm. */
    delayed.received_at_ticks = base + 1000u;
    CHECK(supervisor_update(&sv, &delayed, base + 94u) == SUPERVISOR_STATE_FAILSAFE);
    CHECK(sv.last_wire_seq == 104u && sv.last_result_ticks == base + 3u);
    delayed.wire_seq = 105u;
    delayed.input_seq = 103u;
    delayed.received_at_ticks = base - 1u;
    CHECK(supervisor_update(&sv, &delayed, base + 95u) == SUPERVISOR_STATE_FAILSAFE);
    CHECK(sv.last_wire_seq == 104u);
    CHECK(!supervisor_rearm(&sv, base + 200u));
    CHECK(event(&sv, SUPERVISOR_EVENT_HEARTBEAT, 105u, 0u, base + 201u) == SUPERVISOR_STATE_FAILSAFE);
    CHECK(event(&sv, SUPERVISOR_EVENT_RESULT, 106u, 103u, base + 202u) == SUPERVISOR_STATE_FAILSAFE);
    CHECK(supervisor_rearm(&sv, base + 222u));
    delayed.wire_seq = 107u;
    delayed.input_seq = 104u;
    delayed.received_at_ticks = base + 221u;
    CHECK(supervisor_update(&sv, &delayed, base + 223u) == SUPERVISOR_STATE_INIT);
    CHECK(!sv.has_result && sv.last_wire_seq == 106u);
    /* A restarted sender cannot silently reset preserved replay watermarks. */
    CHECK(event(&sv, SUPERVISOR_EVENT_RESULT, 107u, 0u, base + 224u) == SUPERVISOR_STATE_INIT);
    CHECK(!sv.has_result && sv.last_input_seq == 103u);

    /* A newer sequence must not move either same-kind receipt timer backwards. */
    ready(&sv);
    CHECK(event(&sv, SUPERVISOR_EVENT_HEARTBEAT, 2u, 0u, 10u) == SUPERVISOR_STATE_FRESH);
    delayed.kind = SUPERVISOR_EVENT_HEARTBEAT;
    delayed.wire_seq = 3u;
    delayed.received_at_ticks = 9u;
    CHECK(supervisor_update(&sv, &delayed, 11u) == SUPERVISOR_STATE_FRESH);
    CHECK(sv.last_heartbeat_ticks == 10u && sv.last_wire_seq == 2u);
    CHECK(event(&sv, SUPERVISOR_EVENT_RESULT, 3u, 1u, 12u) == SUPERVISOR_STATE_FRESH);
    delayed.kind = SUPERVISOR_EVENT_RESULT;
    delayed.wire_seq = 4u;
    delayed.input_seq = 2u;
    delayed.received_at_ticks = 11u;
    CHECK(supervisor_update(&sv, &delayed, 13u) == SUPERVISOR_STATE_FRESH);
    CHECK(sv.last_result_ticks == 12u && sv.last_input_seq == 1u && sv.last_wire_seq == 3u);
}

static void test_malformed_heartbeat_and_crc_storm(void)
{
    supervisor_t sv;
    struct hea_parser parser;
    uint8_t out[HEA_MAX_FRAME], payload[HEA_MAX_PAYLOAD];
    struct hea_heartbeat hb = {0u};
    ready(&sv);
    hea_parser_init(&parser);
    size_t len = hea_encode(HEA_MSG_HEARTBEAT, 2u, NULL, 0u, out, sizeof(out));
    CHECK(feed(&sv, &parser, out, len, 10u) == 1u);
    CHECK(sv.last_wire_seq == 1u && sv.last_heartbeat_ticks == 0u);
    len = hea_encode(HEA_MSG_HEARTBEAT, 2u, payload,
                     hea_pack_heartbeat(&hb, payload), out, sizeof(out));
    out[len - 1u] ^= 1u;
    for (uint64_t t = 11u; t <= 60u; ++t) {
        CHECK(feed(&sv, &parser, out, len, t) == 0u);
        CHECK(sv.last_heartbeat_ticks == 0u && sv.last_result_ticks == 1u);
        CHECK(!sv.healthy_interval || t < 31u);
    }
    CHECK(sv.state == SUPERVISOR_STATE_FAILSAFE);
    CHECK(!supervisor_rearm(&sv, 60u));
}

int main(void)
{
    test_sequence_boundaries();
    test_configuration_and_startup();
    test_heartbeat_loss_and_expiry_precedence();
    test_result_silence_and_hold_recovery();
    test_loss_while_hold_and_health_gap();
    test_duplicates_replays_and_invalid_events();
    test_wire_and_input_wrap();
    test_clock_regression();
    test_parser_crc_and_payload_validation();
    test_parser_heartbeat_echo_and_no_cross_clock_math();
    test_backlog_epoch_and_nonzero_clock();
    test_malformed_heartbeat_and_crc_storm();
    printf("12 supervisor scenarios passed (%u checks, including exhaustive 16-bit increment wrap).\n", checks);
    return 0;
}
