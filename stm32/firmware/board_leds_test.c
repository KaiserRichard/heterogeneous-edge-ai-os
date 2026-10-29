/* Host test for the pure state-to-pin mapping table in board_leds.h. */
#define BOARD_LEDS_HOST_TEST
#include "board_leds.h"
#include <assert.h>
#include <stdio.h>

int main(void)
{
    const supervisor_state_t states[] = {
        SUPERVISOR_STATE_INIT,
        SUPERVISOR_STATE_FRESH,
        SUPERVISOR_STATE_HOLD,
        SUPERVISOR_STATE_FAILSAFE
    };
    const uint32_t expected_a_set[] = {0u, BOARD_LED_PA5, 0u, 0u};
    const uint32_t expected_a_reset[] = {BOARD_LED_PA5, 0u, BOARD_LED_PA5, BOARD_LED_PA5};
    const uint32_t expected_b_set[] = {0u, BOARD_LED_PB5, BOARD_LED_PB4, BOARD_LED_PB10};
    const uint32_t expected_b_reset[] = {
        BOARD_LED_PB5 | BOARD_LED_PB4 | BOARD_LED_PB10,
        BOARD_LED_PB4 | BOARD_LED_PB10,
        BOARD_LED_PB5 | BOARD_LED_PB10,
        BOARD_LED_PB5 | BOARD_LED_PB4
    };

    for (unsigned i = 0u; i < sizeof states / sizeof states[0]; ++i) {
        board_led_masks_t masks = board_leds_masks_for_state(states[i]);
        assert(masks.gpioa_set == expected_a_set[i]);
        assert(masks.gpioa_reset == expected_a_reset[i]);
        assert(masks.gpiob_set == expected_b_set[i]);
        assert(masks.gpiob_reset == expected_b_reset[i]);
    }
    puts("PASS: all four supervisor states map to the expected atomic LED pin masks");
    return 0;
}
