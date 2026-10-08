/* Host unit tests for hea_proto. Build and run: make -C protocol test */
#include "hea_proto.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int failures;
#define CHECK(c)                                                              \
    do {                                                                      \
        if (!(c)) {                                                           \
            fprintf(stderr, "%s:%d: CHECK failed: %s\n", __FILE__, __LINE__, #c); \
            failures++;                                                       \
        }                                                                     \
    } while (0)

static int feed_all(struct hea_parser *p, const uint8_t *b, size_t n, struct hea_frame *last)
{
    int got = 0;
    for (size_t i = 0; i < n; i++)
        if (hea_parser_feed(p, b[i])) {
            got++;
            if (last)
                *last = p->frame;
        }
    return got;
}

static size_t make_inference(uint16_t seq, uint8_t *out)
{
    struct hea_inference m = {0x1122334455667788ull, 0x99AABBCCDDEEFF00ull, 0xDEADBEEFu, 7, 93};
    uint8_t pl[HEA_MAX_PAYLOAD];
    uint8_t len = hea_pack_inference(&m, pl);
    return hea_encode(HEA_MSG_INFERENCE, seq, pl, len, out, HEA_MAX_FRAME);
}

static void test_crc_known_vector(void)
{
    /* CRC-16/CCITT-FALSE check value for "123456789" is 0x29B1. */
    const uint8_t vector[] = {0x31u, 0x32u, 0x33u, 0x34u, 0x35u, 0x36u, 0x37u, 0x38u, 0x39u};
    CHECK(hea_crc16(vector, sizeof vector) == 0x29B1u);
}

static void test_roundtrip_all_types(void)
{
    uint8_t pl[HEA_MAX_PAYLOAD], buf[HEA_MAX_FRAME];
    struct hea_parser p;
    struct hea_frame f;
    hea_parser_init(&p);

    struct hea_heartbeat hb = {123456789012345ull}, hb2;
    size_t n = hea_encode(HEA_MSG_HEARTBEAT, 1, pl, hea_pack_heartbeat(&hb, pl), buf, sizeof buf);
    CHECK(feed_all(&p, buf, n, &f) == 1);
    CHECK(hea_unpack_heartbeat(&f, &hb2) == 0 && hb2.linux_send_ns == hb.linux_send_ns);
    CHECK(f.seq == 1);

    struct hea_inference in2;
    n = make_inference(0xBEEF, buf);
    CHECK(feed_all(&p, buf, n, &f) == 1);
    CHECK(hea_unpack_inference(&f, &in2) == 0);
    CHECK(in2.linux_input_ns == 0x1122334455667788ull && in2.linux_done_ns == 0x99AABBCCDDEEFF00ull);
    CHECK(in2.input_seq == 0xDEADBEEFu && in2.class_id == 7 && in2.confidence_pct == 93);
    CHECK(f.seq == 0xBEEF);

    struct hea_echo_req rq = {42}, rq2;
    n = hea_encode(HEA_MSG_ECHO_REQ, 3, pl, hea_pack_echo_req(&rq, pl), buf, sizeof buf);
    CHECK(feed_all(&p, buf, n, &f) == 1 && hea_unpack_echo_req(&f, &rq2) == 0 && rq2.linux_t1_ns == 42);

    struct hea_echo_resp rs = {43, 0xFFFFFFF0u, 0x00000010u}, rs2;
    n = hea_encode(HEA_MSG_ECHO_RESP, 4, pl, hea_pack_echo_resp(&rs, pl), buf, sizeof buf);
    CHECK(feed_all(&p, buf, n, &f) == 1 && hea_unpack_echo_resp(&f, &rs2) == 0);
    CHECK(rs2.linux_t1_ns == 43 && rs2.mcu_rx_us == 0xFFFFFFF0u && rs2.mcu_tx_us == 0x10u);

    struct hea_mcu_status st = {1000, HEA_MCU_FAILSAFE, 513, 65535}, st2;
    n = hea_encode(HEA_MSG_MCU_STATUS, 5, pl, hea_pack_mcu_status(&st, pl), buf, sizeof buf);
    CHECK(feed_all(&p, buf, n, &f) == 1 && hea_unpack_mcu_status(&f, &st2) == 0);
    CHECK(st2.mcu_us == 1000 && st2.state == HEA_MCU_FAILSAFE && st2.missed_heartbeats == 513 &&
          st2.rx_crc_errors == 65535);

    /* Wrong type is rejected by the unpacker. */
    CHECK(hea_unpack_heartbeat(&f, &hb2) != 0);
    CHECK(p.stats.frames_ok == 5 && p.stats.crc_errors == 0);
}

static void test_empty_payload_and_limits(void)
{
    uint8_t buf[HEA_MAX_FRAME + 4], big[HEA_MAX_PAYLOAD + 1] = {0};
    struct hea_parser p;
    hea_parser_init(&p);
    size_t n = hea_encode(0x10, 9, NULL, 0, buf, sizeof buf);
    CHECK(n == HEA_HEADER_LEN + HEA_CRC_LEN);
    CHECK(feed_all(&p, buf, n, NULL) == 1 && p.frame.len == 0);

    CHECK(hea_encode(0x10, 0, big, HEA_MAX_PAYLOAD, buf, sizeof buf) == HEA_MAX_FRAME);
    CHECK(hea_encode(0x10, 0, big, HEA_MAX_PAYLOAD + 1, buf, sizeof buf) == 0);
    CHECK(hea_encode(0x10, 0, big, 4, buf, 5) == 0);

    /* A header that declares an oversize payload is rejected without reading it. */
    uint8_t bad[] = {HEA_SOF0, HEA_SOF1, 1, 0x10, 0, 0, HEA_MAX_PAYLOAD + 1};
    CHECK(feed_all(&p, bad, sizeof bad, NULL) == 0 && p.stats.len_errors == 1);
    n = make_inference(1, buf);
    CHECK(feed_all(&p, buf, n, NULL) == 1);
}

static void test_resync_after_garbage(void)
{
    uint8_t stream[256], frame[HEA_MAX_FRAME];
    size_t fl = make_inference(77, frame), k = 0;
    const uint8_t junk[] = {0x00, 0xA5, 0x00, 0xA5, 0xA5, 0xFF, 0x5A, 0x13};
    memcpy(stream, junk, sizeof junk);
    k += sizeof junk;
    stream[k++] = HEA_SOF0; /* extra A5 right before a real SOF */
    memcpy(&stream[k], frame, fl);
    k += fl;
    memcpy(&stream[k], frame, fl); /* back-to-back frames */
    k += fl;

    struct hea_parser p;
    hea_parser_init(&p);
    struct hea_frame f;
    CHECK(feed_all(&p, stream, k, &f) == 2);
    CHECK(f.seq == 77);
}

static void test_bad_version_rejected(void)
{
    uint8_t buf[HEA_MAX_FRAME];
    size_t n = make_inference(1, buf);
    buf[2] = 2;
    uint16_t crc = hea_crc16(&buf[2], n - 4); /* re-sign so only the version is wrong */
    buf[n - 2] = (uint8_t)crc;
    buf[n - 1] = (uint8_t)(crc >> 8);
    struct hea_parser p;
    hea_parser_init(&p);
    CHECK(feed_all(&p, buf, n, NULL) == 0 && p.stats.version_errors == 1);
}

static void test_every_single_bit_flip_detected(void)
{
    uint8_t ref[HEA_MAX_FRAME], buf[HEA_MAX_FRAME];
    size_t n = make_inference(5, ref);
    int accepted = 0;
    /* Flip each bit after the SOF: CRC-16 detects every single-bit error. */
    for (size_t i = 2; i < n; i++)
        for (int bit = 0; bit < 8; bit++) {
            memcpy(buf, ref, n);
            buf[i] ^= (uint8_t)(1u << bit);
            struct hea_parser p;
            hea_parser_init(&p);
            accepted += feed_all(&p, buf, n, NULL);
        }
    CHECK(accepted == 0);
}

/* Fixed unsigned operations: libc rand() is not portable across platforms. */
static uint32_t noise_next(uint32_t *state)
{
    uint32_t x = *state;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    *state = x;
    return x;
}

static void test_false_sync_consumes_two_frames(void)
{
    /* Captured glibc rand() losses at seed 12345, sequences 13355/13356.
     * The noise SOF takes A5 5A 01 02 2B from the first real frame as its
     * header: fake len=0x2B (43), which consumes two 31-byte frames. */
    const uint8_t first_noise[] = {0xBBu, 0xFDu, 0xA5u, 0x5Au};
    const uint8_t second_noise[] = {0x9Cu, 0xB4u, 0xB1u, 0xD4u};
    uint8_t frame[HEA_MAX_FRAME];
    struct hea_parser p;
    hea_parser_init(&p);
    CHECK(feed_all(&p, first_noise, sizeof first_noise, NULL) == 0);
    size_t n = make_inference(13355u, frame);
    CHECK(feed_all(&p, frame, n, NULL) == 0);
    CHECK(p.state == HEA_P_PAYLOAD && p.frame.len == 43u && p.idx == 26u);
    CHECK(feed_all(&p, second_noise, sizeof second_noise, NULL) == 0);
    n = make_inference(13356u, frame);
    CHECK(feed_all(&p, frame, n, NULL) == 0);
    CHECK(p.stats.crc_errors == 1u && p.state == HEA_P_SOF0);
    n = make_inference(13357u, frame);
    CHECK(feed_all(&p, frame, n, NULL) == 1);
    CHECK(p.frame.seq == 13357u);
}

static void test_random_noise_recovers(void)
{
    /* Interleave valid frames with random noise; every frame not overlapped
       by a false sync must decode, and no corrupted frame may be accepted. */
    uint32_t rng = UINT32_C(12345);
    uint32_t fingerprint = UINT32_C(2166136261);
    uint8_t frame[HEA_MAX_FRAME];
    struct hea_parser p;
    hea_parser_init(&p);
    int sent = 0, got = 0, wrong = 0;
    for (int r = 0; r < 20000; r++) {
        uint32_t noise = noise_next(&rng) % 12u;
        fingerprint = (fingerprint ^ noise) * UINT32_C(16777619);
        for (uint32_t j = 0u; j < noise; j++) {
            uint8_t byte = (uint8_t)noise_next(&rng);
            fingerprint = (fingerprint ^ byte) * UINT32_C(16777619);
            if (hea_parser_feed(&p, byte))
                wrong++; /* a noise-only frame would need a 1/65536 CRC collision */
        }
        size_t n = make_inference((uint16_t)r, frame);
        sent++;
        for (size_t i = 0; i < n; i++)
            if (hea_parser_feed(&p, frame[i])) {
                if (p.frame.seq == (uint16_t)r && p.frame.type == HEA_MSG_INFERENCE)
                    got++;
                else
                    wrong++;
            }
    }
    printf("  noise test: %d/%d frames decoded (%.2f%%), %d false accepts, crc_err=%u len_err=%u\n",
           got, sent, 100.0 * got / sent, wrong, p.stats.crc_errors, p.stats.len_errors);
    printf("  noise PRNG: xorshift32 seed=12345 fingerprint=%08x\n", (unsigned)fingerprint);
    CHECK(wrong == 0);
    CHECK(got == sent);
    CHECK(fingerprint == UINT32_C(0x8C9204CD));
    CHECK(p.stats.crc_errors == 0u && p.stats.len_errors == 1u);
}

int main(void)
{
    test_crc_known_vector();
    test_roundtrip_all_types();
    test_empty_payload_and_limits();
    test_resync_after_garbage();
    test_bad_version_rejected();
    test_every_single_bit_flip_detected();
    test_false_sync_consumes_two_frames();
    test_random_noise_recovers();
    if (failures) {
        fprintf(stderr, "FAILED: %d check(s)\n", failures);
        return 1;
    }
    printf("all protocol tests passed\n");
    return 0;
}
