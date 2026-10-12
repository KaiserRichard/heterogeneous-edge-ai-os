#include "rx_dma_cursor.h"
#include "hea_proto.h"
#include "../firmware/uart_budget.h"
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
    assert(HEA_UART_TRANSIT_US(921600) == 5793);
    assert(HEA_UART_TRANSIT_US(9600) == 81042);
    /* Expired prefixes cannot be completed by delayed suffixes. A quiet gap
     * followed by SOF accepts the next frame at every possible split, even
     * across TIM2 wrap. Also test a normal slow-baud serialized frame. */
    for (size_t split = 1; split < n; ++split) {
        struct hea_parser p; hea_parser_init(&p);
        uint32_t start = 0, origin = UINT32_MAX - 100u;
        for (size_t i = 0; i < split; ++i)
            assert(!hea_uart_feed(&p, wire[i], origin + (uint32_t)i, &start, 2793));
        for (size_t i = split; i < n; ++i)
            assert(!hea_uart_feed(&p, wire[i], origin + 40000u + (uint32_t)i, &start, 2793));
        unsigned ready = 0;
        for (size_t i = 0; i < n; ++i)
            ready += (unsigned)hea_uart_feed(&p, wire[i], origin + 80000u + (uint32_t)i, &start, 2793);
        assert(ready == 1 && p.frame.seq == 7);
    }
    struct hea_parser slow; hea_parser_init(&slow);
    uint32_t start = 0;
    for (size_t i = 0; i < n; ++i)
        assert(hea_uart_feed(&slow, wire[i], (uint32_t)(i * 1042u), &start,
                             (uint32_t)HEA_UART_ASSEMBLY_US(9600)) == (i + 1u == n));
    puts("PASS: baud-derived transit budget; expired frame suffix rejected, SOF resync and slow-baud assembly");
    puts("PASS: DMA cursor reload, fragmented frames at every ring wrap, unseen-lap/time-wrap guard");
    return 0;
}
