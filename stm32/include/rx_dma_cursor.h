#ifndef RX_DMA_CURSOR_H
#define RX_DMA_CURSOR_H
#include <stdbool.h>
#include <stdint.h>

/* NDTR can read either zero at reload or size just after reload. Both denote
 * index zero. Callers must discard if a whole lap could have gone unseen. */
static inline unsigned rx_dma_position(unsigned size, unsigned ndtr)
{
    return (size - ndtr) % size;
}
static inline bool rx_dma_lap_possible(uint32_t now, uint32_t previous,
                                      unsigned size, uint32_t baud)
{
    return (uint32_t)(now - previous) >= (uint64_t)size * 10u * 1000000u / baud;
}
#endif
