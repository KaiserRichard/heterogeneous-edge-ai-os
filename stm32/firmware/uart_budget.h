#ifndef HEA_UART_BUDGET_H
#define HEA_UART_BUDGET_H
#include "hea_proto.h"

/* 8N1: ten bits per byte, round UP for the largest legal wire frame.
 * Shared with the bridge's runtime baud calculation. The 5 ms margin covers
 * 2 ms to submit a partial write and 3 ms for RX polling, delivery and clock
 * quantization. Thus 921600 uses 5793 us (stricter than the former 5000 us),
 * and 9600 uses 81042 us. These are conservative software budgets, requiring
 * measurement of the actual UART/adapter delay on the rig.
 * Firmware and bridge must use the same baud. If this shared configuration
 * changes, rebuild Linux with `make -C linux clean all` as its lightweight
 * Makefile does not generate transitive header dependencies. */
#define HEA_UART_SERIAL_US(baud) \
    ((HEA_MAX_FRAME * UINT64_C(10000000) + (baud) - 1u) / (baud))
#define HEA_UART_WRITE_US UINT64_C(2000)
#define HEA_UART_RX_MARGIN_US UINT64_C(3000)
#define HEA_UART_ASSEMBLY_US(baud) (HEA_UART_SERIAL_US(baud) + HEA_UART_WRITE_US)
#define HEA_UART_TRANSIT_US(baud) (HEA_UART_ASSEMBLY_US(baud) + HEA_UART_RX_MARGIN_US)

/* Expire from the first SOF byte, never from the last byte: trickle traffic
 * cannot keep an old frame alive. Expiration is checked on the next byte;
 * an idle partial frame never emits an event. Keep statistics returning to SOF.
 * uint32 subtraction handles TIM2 wrap; budget is below half a timer wrap. */
static inline int hea_uart_feed(struct hea_parser *p, uint8_t byte,
                                uint32_t now, uint32_t *started, uint32_t bound)
{
    if (p->state != HEA_P_SOF0 && (uint32_t)(now - *started) >= bound)
        p->state = HEA_P_SOF0;
    if (p->state == HEA_P_SOF0 || (p->state == HEA_P_SOF1 && byte == HEA_SOF0))
        *started = now;
    return hea_parser_feed(p, byte);
}
#endif
