#include "hea_proto.h"

#include <string.h>

int hea_version_supported(uint8_t version)
{
    return version == HEA_PROTO_VERSION_LEGACY ||
        version == HEA_PROTO_VERSION_AGE || version == HEA_PROTO_VERSION;
}

int hea_age_at_send_us(uint64_t input_ns, uint64_t send_ns, uint32_t *age_us)
{
    if (age_us == NULL || send_ns < input_ns) return -1;
    uint64_t elapsed = send_ns - input_ns;
    uint64_t us = elapsed / UINT64_C(1000) + (elapsed % UINT64_C(1000) != 0u ? 1u : 0u);
    *age_us = us > UINT32_MAX ? UINT32_MAX : (uint32_t)us;
    return 0;
}

uint16_t hea_crc16_update(uint16_t crc, uint8_t byte)
{
    uint32_t c = (uint32_t)crc ^ ((uint32_t)byte << 8);
    for (int i = 0; i < 8; i++)
        c = (c & 0x8000u) ? ((c << 1) ^ 0x1021u) : (c << 1);
    return (uint16_t)(c & 0xFFFFu);
}

uint16_t hea_crc16(const uint8_t *data, size_t len)
{
    uint16_t crc = 0xFFFFu;
    for (size_t i = 0; i < len; i++)
        crc = hea_crc16_update(crc, data[i]);
    return crc;
}

size_t hea_encode(uint8_t type, uint16_t seq, const uint8_t *payload, uint8_t len,
                  uint8_t *out, size_t out_cap)
{
    size_t total = HEA_HEADER_LEN + (size_t)len + HEA_CRC_LEN;
    if (len > HEA_MAX_PAYLOAD || out_cap < total)
        return 0;

    out[0] = HEA_SOF0;
    out[1] = HEA_SOF1;
    out[2] = HEA_PROTO_VERSION;
    out[3] = type;
    out[4] = (uint8_t)(seq & 0xFFu);
    out[5] = (uint8_t)(seq >> 8);
    out[6] = len;
    if (len)
        memcpy(&out[HEA_HEADER_LEN], payload, len);

    uint16_t crc = hea_crc16(&out[2], HEA_HEADER_LEN - 2 + (size_t)len);
    out[HEA_HEADER_LEN + len] = (uint8_t)(crc & 0xFFu);
    out[HEA_HEADER_LEN + len + 1] = (uint8_t)(crc >> 8);
    return total;
}

void hea_parser_init(struct hea_parser *p)
{
    memset(p, 0, sizeof(*p));
    p->state = HEA_P_SOF0;
}

/*
 * On any error the parser returns to SOF hunting at the next byte. Bytes of a
 * rejected frame are not rescanned, so a valid frame that starts inside a
 * corrupted one is lost; the bound is one maximum-size frame.
 */
int hea_parser_feed(struct hea_parser *p, uint8_t b)
{
    switch (p->state) {
    case HEA_P_SOF0:
        if (b == HEA_SOF0)
            p->state = HEA_P_SOF1;
        else
            p->stats.bytes_dropped++;
        return 0;

    case HEA_P_SOF1:
        if (b == HEA_SOF1) {
            p->state = HEA_P_HEADER;
            p->idx = 0;
            p->crc = 0xFFFFu;
        } else if (b != HEA_SOF0) { /* A5 A5 5A: stay synced on the second A5 */
            p->state = HEA_P_SOF0;
            p->stats.bytes_dropped += 2;
        } else {
            p->stats.bytes_dropped++;
        }
        return 0;

    case HEA_P_HEADER:
        p->hdr[p->idx++] = b;
        p->crc = hea_crc16_update(p->crc, b);
        if (p->idx < sizeof(p->hdr))
            return 0;
        p->frame.version = p->hdr[0];
        p->frame.type = p->hdr[1];
        p->frame.seq = (uint16_t)(p->hdr[2] | (p->hdr[3] << 8));
        p->frame.len = p->hdr[4];
        if (p->frame.len > HEA_MAX_PAYLOAD) {
            p->stats.len_errors++;
            p->state = HEA_P_SOF0;
            return 0;
        }
        p->idx = 0;
        p->state = p->frame.len ? HEA_P_PAYLOAD : HEA_P_CRC;
        return 0;

    case HEA_P_PAYLOAD:
        p->frame.payload[p->idx++] = b;
        p->crc = hea_crc16_update(p->crc, b);
        if (p->idx == p->frame.len) {
            p->idx = 0;
            p->state = HEA_P_CRC;
        }
        return 0;

    case HEA_P_CRC:
        p->crc_rx[p->idx++] = b;
        if (p->idx < HEA_CRC_LEN)
            return 0;
        p->state = HEA_P_SOF0;
        if ((uint16_t)(p->crc_rx[0] | (p->crc_rx[1] << 8)) != p->crc) {
            p->stats.crc_errors++;
            return 0;
        }
        if (!hea_version_supported(p->frame.version)) {
            p->stats.version_errors++;
            return 0;
        }
        p->stats.frames_ok++;
        return 1;
    }
    p->state = HEA_P_SOF0;
    return 0;
}

/* ---- little-endian helpers ---- */

static void put_u16(uint8_t *b, uint16_t v)
{
    b[0] = (uint8_t)v;
    b[1] = (uint8_t)(v >> 8);
}

static void put_u32(uint8_t *b, uint32_t v)
{
    for (int i = 0; i < 4; i++)
        b[i] = (uint8_t)(v >> (8 * i));
}

static void put_u64(uint8_t *b, uint64_t v)
{
    for (int i = 0; i < 8; i++)
        b[i] = (uint8_t)(v >> (8 * i));
}

static uint16_t get_u16(const uint8_t *b) { return (uint16_t)(b[0] | (b[1] << 8)); }

static uint32_t get_u32(const uint8_t *b)
{
    uint32_t v = 0;
    for (int i = 3; i >= 0; i--)
        v = (v << 8) | b[i];
    return v;
}

static uint64_t get_u64(const uint8_t *b)
{
    uint64_t v = 0;
    for (int i = 7; i >= 0; i--)
        v = (v << 8) | b[i];
    return v;
}

static int check(const struct hea_frame *f, uint8_t type, uint8_t len)
{
    return (hea_version_supported(f->version) && f->type == type && f->len == len) ? 0 : -1;
}

/* ---- payloads ---- */

uint8_t hea_pack_heartbeat(const struct hea_heartbeat *m, uint8_t *b)
{
    put_u64(b, m->linux_send_ns);
    put_u64(&b[8], m->session_id);
    return 16;
}

int hea_unpack_heartbeat(const struct hea_frame *f, struct hea_heartbeat *m)
{
    uint8_t expected = f->version == HEA_PROTO_VERSION ? 16u : 8u;
    if (check(f, HEA_MSG_HEARTBEAT, expected))
        return -1;
    m->linux_send_ns = get_u64(f->payload);
    m->session_id = f->version == HEA_PROTO_VERSION ? get_u64(&f->payload[8]) : 0u;
    return 0;
}

uint8_t hea_pack_inference(const struct hea_inference *m, uint8_t *b)
{
    put_u64(&b[0], m->linux_input_ns);
    put_u64(&b[8], m->linux_done_ns);
    put_u32(&b[16], m->input_seq);
    b[20] = m->class_id;
    b[21] = m->confidence_pct;
    put_u32(&b[22], m->age_at_send_us);
    return 26;
}

int hea_unpack_inference(const struct hea_frame *f, struct hea_inference *m)
{
    uint8_t expected = f->version == HEA_PROTO_VERSION_LEGACY ? 22u : 26u;
    if (check(f, HEA_MSG_INFERENCE, expected))
        return -1;
    m->linux_input_ns = get_u64(&f->payload[0]);
    m->linux_done_ns = get_u64(&f->payload[8]);
    m->input_seq = get_u32(&f->payload[16]);
    m->class_id = f->payload[20];
    m->confidence_pct = f->payload[21];
    /* Zero here means absent: callers must check frame.version for presence. */
    m->age_at_send_us = f->version == HEA_PROTO_VERSION_LEGACY ? 0u : get_u32(&f->payload[22]);
    return 0;
}

uint8_t hea_pack_echo_req(const struct hea_echo_req *m, uint8_t *b)
{
    put_u64(b, m->linux_t1_ns);
    return 8;
}

int hea_unpack_echo_req(const struct hea_frame *f, struct hea_echo_req *m)
{
    if (check(f, HEA_MSG_ECHO_REQ, 8))
        return -1;
    m->linux_t1_ns = get_u64(f->payload);
    return 0;
}

uint8_t hea_pack_echo_resp(const struct hea_echo_resp *m, uint8_t *b)
{
    put_u64(&b[0], m->linux_t1_ns);
    put_u32(&b[8], m->mcu_rx_us);
    put_u32(&b[12], m->mcu_tx_us);
    return 16;
}

int hea_unpack_echo_resp(const struct hea_frame *f, struct hea_echo_resp *m)
{
    if (check(f, HEA_MSG_ECHO_RESP, 16))
        return -1;
    m->linux_t1_ns = get_u64(&f->payload[0]);
    m->mcu_rx_us = get_u32(&f->payload[8]);
    m->mcu_tx_us = get_u32(&f->payload[12]);
    return 0;
}

uint8_t hea_pack_mcu_status(const struct hea_mcu_status *m, uint8_t *b)
{
    put_u32(&b[0], m->mcu_us);
    b[4] = m->state;
    put_u16(&b[5], m->missed_heartbeats);
    put_u16(&b[7], m->rx_crc_errors);
    return 9;
}

int hea_unpack_mcu_status(const struct hea_frame *f, struct hea_mcu_status *m)
{
    if (check(f, HEA_MSG_MCU_STATUS, 9))
        return -1;
    m->mcu_us = get_u32(&f->payload[0]);
    m->state = f->payload[4];
    m->missed_heartbeats = get_u16(&f->payload[5]);
    m->rx_crc_errors = get_u16(&f->payload[7]);
    return 0;
}
