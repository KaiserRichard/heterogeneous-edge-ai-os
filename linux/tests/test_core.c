#include "hea_ipc.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

int main(void)
{
    const uint8_t golden[] = {
        0x78, 0x56, 0x34, 0x12, 8, 7, 6, 5, 4, 3, 2, 1,
        0x18, 0x17, 0x16, 0x15, 0x14, 0x13, 0x12, 0x11, 7, 99
    };
    struct hea_result r = { UINT32_C(0x12345678), UINT64_C(0x0102030405060708),
                           UINT64_C(0x1112131415161718), 7, 99 }, decoded;
    struct hea_input in = { r.frame_id, r.t_input_ns }, out;
    uint8_t b[HEA_RESULT_SIZE + 1u];
    hea_result_pack(&r, b); assert(!memcmp(b, golden, HEA_RESULT_SIZE));
    assert(!hea_result_unpack(&decoded, b, HEA_RESULT_SIZE));
    assert(decoded.frame_id == r.frame_id && decoded.t_input_ns == r.t_input_ns);
    assert(decoded.t_done_ns == r.t_done_ns && decoded.class_id == 7 && decoded.confidence == 99);
    assert(hea_result_unpack(&decoded, b, HEA_RESULT_SIZE - 1u) == -1);
    assert(hea_result_unpack(&decoded, b, HEA_RESULT_SIZE + 1u) == -1);
    b[21] = 101; assert(hea_result_unpack(&decoded, b, HEA_RESULT_SIZE) == -1);
    r.t_done_ns = 0; hea_result_pack(&r, b);
    assert(hea_result_unpack(&decoded, b, HEA_RESULT_SIZE) == -1);
    hea_input_pack(&in, b); assert(!memcmp(b, golden, HEA_INPUT_SIZE));
    assert(!hea_input_unpack(&out, b, HEA_INPUT_SIZE));
    assert(out.frame_id == in.frame_id && out.t_input_ns == in.t_input_ns);
    assert(hea_input_unpack(&out, b, HEA_INPUT_SIZE + 1u) == -1);
    struct hea_queue q;
    hea_queue_init(&q, 0);
    assert(!hea_queue_pop(&q, &decoded));
    for (uint32_t i = 0; i < HEA_QUEUE_CAPACITY; ++i) {
        r.frame_id = i; assert(hea_queue_push(&q, &r));
    }
    assert(!hea_queue_push(&q, &r) && q.dropped == 1);
    for (uint32_t i = 0; i < HEA_QUEUE_CAPACITY; ++i) {
        assert(hea_queue_pop(&q, &decoded) && decoded.frame_id == i);
        r.frame_id = i + HEA_QUEUE_CAPACITY; assert(hea_queue_push(&q, &r));
    }
    for (uint32_t i = 0; i < HEA_QUEUE_CAPACITY; ++i)
        assert(hea_queue_pop(&q, &decoded) && decoded.frame_id == i + HEA_QUEUE_CAPACITY);
    assert(!hea_queue_pop(&q, &decoded));
    hea_queue_init(&q, 1);
    for (uint32_t i = 0; i < 100; ++i) { r.frame_id = i; assert(hea_queue_push(&q, &r)); }
    assert(q.count == 1 && q.overwritten == 99 && q.dropped == 0);
    assert(hea_queue_pop(&q, &decoded) && decoded.frame_id == 99);
    assert(!hea_queue_pop(&q, &decoded));
    puts("PASS: IPC golden packing/validation; FIFO order/full/wrap; latest overwrite");
    return 0;
}
