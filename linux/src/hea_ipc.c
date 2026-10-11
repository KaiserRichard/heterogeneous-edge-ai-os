#include "hea_ipc.h"
#include <string.h>

static void put(uint8_t *b, uint64_t v, size_t n)
{
    for (size_t i = 0; i < n; ++i) b[i] = (uint8_t)(v >> (8u * i));
}
static uint64_t get(const uint8_t *b, size_t n)
{
    uint64_t v = 0;
    for (size_t i = 0; i < n; ++i) v |= (uint64_t)b[i] << (8u * i);
    return v;
}
void hea_input_pack(const struct hea_input *m, uint8_t *b)
{
    put(b, m->frame_id, 4); put(b + 4, m->t_input_ns, 8);
}
int hea_input_unpack(struct hea_input *m, const uint8_t *b, size_t n)
{
    if (n != HEA_INPUT_SIZE) return -1;
    m->frame_id = (uint32_t)get(b, 4); m->t_input_ns = get(b + 4, 8);
    return 0;
}
void hea_result_pack(const struct hea_result *m, uint8_t *b)
{
    put(b, m->frame_id, 4); put(b + 4, m->t_input_ns, 8);
    put(b + 12, m->t_done_ns, 8); b[20] = m->class_id; b[21] = m->confidence;
}
int hea_result_unpack(struct hea_result *m, const uint8_t *b, size_t n)
{
    if (n != HEA_RESULT_SIZE || b[21] > 100u) return -1;
    m->frame_id = (uint32_t)get(b, 4); m->t_input_ns = get(b + 4, 8);
    m->t_done_ns = get(b + 12, 8); m->class_id = b[20]; m->confidence = b[21];
    return m->t_done_ns < m->t_input_ns ? -1 : 0;
}
void hea_queue_init(struct hea_queue *q, int latest)
{
    memset(q, 0, sizeof(*q)); q->latest = latest;
}
int hea_queue_push(struct hea_queue *q, const struct hea_result *r)
{
    if (q->latest && q->count != 0u) {
        q->items[q->head] = *r; ++q->overwritten; return 1;
    }
    if (q->count == HEA_QUEUE_CAPACITY) { ++q->dropped; return 0; }
    q->items[(q->head + q->count) % HEA_QUEUE_CAPACITY] = *r;
    ++q->count; return 1;
}
int hea_queue_pop(struct hea_queue *q, struct hea_result *r)
{
    if (q->count == 0u) return 0;
    *r = q->items[q->head]; q->head = (q->head + 1u) % HEA_QUEUE_CAPACITY;
    --q->count; return 1;
}
