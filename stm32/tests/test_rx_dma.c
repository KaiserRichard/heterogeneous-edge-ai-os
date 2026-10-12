#include "rx_dma_cursor.h"
#include "hea_proto.h"
#include <assert.h>
#include <stdio.h>

int main(void)
{
    enum { SIZE = 128 };
    uint8_t ring[SIZE], wire[HEA_MAX_FRAME], payload[HEA_MAX_PAYLOAD];
    struct hea_heartbeat hb = {123456, 42};
    uint8_t len = hea_pack_heartbeat(&hb, payload);
    size_t n = hea_encode(HEA_MSG_HEARTBEAT, 7, payload, len, wire, sizeof wire);
    assert(n < SIZE);
    /* Fragment each frame at every byte, cross every possible physical wrap.
     * DMA notifications may coalesce: producer index, not wake count, owns data. */
    for (unsigned origin = 0; origin < SIZE; ++origin) {
        for (size_t split = 0; split <= n; ++split) {
            struct hea_parser parser;
            hea_parser_init(&parser);
            unsigned read = origin, write = origin, frames = 0;
            for (size_t i = 0; i < n; ++i) {
                ring[write] = wire[i]; write = (write + 1u) % SIZE;
                if (i + 1u != split && i + 1u != n) continue;
                unsigned end = rx_dma_position(SIZE, SIZE - write);
                while (read != end) {
                    if (hea_parser_feed(&parser, ring[read])) ++frames;
                    read = (read + 1u) % SIZE;
                }
            }
            assert(frames == 1 && parser.frame.seq == 7);
        }
    }
    assert(rx_dma_position(SIZE, 0) == 0);
    assert(rx_dma_position(SIZE, SIZE) == 0);
    /* Equal producer/consumer can mean full, not empty. Time guard must reject
     * a possible unseen lap, including across the 32-bit TIM2 wrap. */
    assert(!rx_dma_lap_possible(999, 0, 2048, 923077));
    assert(!rx_dma_lap_possible(22185, 0, 2048, 923077));
    assert(rx_dma_lap_possible(22186, 0, 2048, 923077));
    assert(!rx_dma_lap_possible(499, UINT32_MAX - 499u, 2048, 923077));
    assert(rx_dma_lap_possible(23000, UINT32_MAX - 499u, 2048, 923077));
    puts("PASS: DMA cursor reload, fragmented frames at every ring wrap, unseen-lap/time-wrap guard");
    return 0;
}
