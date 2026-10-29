#ifndef BOARD_LEDS_H
#define BOARD_LEDS_H

#include <stdint.h>
#include "supervisor.h"

#define BOARD_LED_PA5 (1u << 5)
#define BOARD_LED_PB5 (1u << 5)
#define BOARD_LED_PB4 (1u << 4)
#define BOARD_LED_PB10 (1u << 10)
#define BOARD_LED_PC7 (1u << 7)

typedef struct {
    uint32_t gpioa_set;
    uint32_t gpioa_reset;
    uint32_t gpiob_set;
    uint32_t gpiob_reset;
} board_led_masks_t;

/* Pure mapping so the state table can be checked on the host without CMSIS. */
static inline board_led_masks_t board_leds_masks_for_state(supervisor_state_t state)
{
    const board_led_masks_t all_off = {
        .gpioa_set = 0u,
        .gpioa_reset = BOARD_LED_PA5,
        .gpiob_set = 0u,
        .gpiob_reset = BOARD_LED_PB5 | BOARD_LED_PB4 | BOARD_LED_PB10
    };

    switch (state) {
    case SUPERVISOR_STATE_FRESH:
        return (board_led_masks_t){
            .gpioa_set = BOARD_LED_PA5,
            .gpioa_reset = 0u,
            .gpiob_set = BOARD_LED_PB5,
            .gpiob_reset = BOARD_LED_PB4 | BOARD_LED_PB10
        };
    case SUPERVISOR_STATE_HOLD:
        return (board_led_masks_t){
            .gpioa_set = 0u,
            .gpioa_reset = BOARD_LED_PA5,
            .gpiob_set = BOARD_LED_PB4,
            .gpiob_reset = BOARD_LED_PB5 | BOARD_LED_PB10
        };
    case SUPERVISOR_STATE_FAILSAFE:
        return (board_led_masks_t){
            .gpioa_set = 0u,
            .gpioa_reset = BOARD_LED_PA5,
            .gpiob_set = BOARD_LED_PB10,
            .gpiob_reset = BOARD_LED_PB5 | BOARD_LED_PB4
        };
    case SUPERVISOR_STATE_INIT:
    default:
        return all_off;
    }
}

/* Call from task context after GPIOA/B/C clocks and output modes are enabled. */
#ifndef BOARD_LEDS_HOST_TEST
static inline void board_leds_output(supervisor_state_t state)
{
    board_led_masks_t masks = board_leds_masks_for_state(state);
    GPIOA->BSRR = masks.gpioa_set | (masks.gpioa_reset << 16);
    GPIOB->BSRR = masks.gpiob_set | (masks.gpiob_reset << 16);
}

/* Link activity is task-owned. It is intentionally not driven by an ISR. */
static inline void board_leds_toggle_activity(void)
{
    static uint8_t on;
    GPIOC->BSRR = on ? (BOARD_LED_PC7 << 16) : BOARD_LED_PC7;
    on = (uint8_t)!on;
}
#endif

#endif
