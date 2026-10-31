#ifndef HEA_IPC_H
#define HEA_IPC_H

#include <stddef.h>
#include <stdint.h>

/* Datagram ABI: explicit little-endian bytes, never a native struct. */
#define HEA_INPUT_SIZE 12u
#define HEA_RESULT_SIZE 22u
struct hea_input { uint32_t frame_id; uint64_t t_input_ns; };
struct hea_result {
    uint32_t frame_id;
    uint64_t t_input_ns, t_done_ns;
    uint8_t class_id, confidence; /* confidence is an integer percentage 0..100 */
};
void hea_input_pack(const struct hea_input *m, uint8_t *b);
int hea_input_unpack(struct hea_input *m, const uint8_t *b, size_t n);
void hea_result_pack(const struct hea_result *m, uint8_t *b);
int hea_result_unpack(struct hea_result *m, const uint8_t *b, size_t n);

#define HEA_QUEUE_CAPACITY 256u
struct hea_queue {
    struct hea_result items[HEA_QUEUE_CAPACITY];
    size_t head, count;
    int latest;
    uint64_t overwritten, dropped;
};
void hea_queue_init(struct hea_queue *q, int latest);
int hea_queue_push(struct hea_queue *q, const struct hea_result *r);
int hea_queue_pop(struct hea_queue *q, struct hea_result *r);
#endif
