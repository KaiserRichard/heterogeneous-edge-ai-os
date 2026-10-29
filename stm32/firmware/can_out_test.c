#include "can_out.h"

#include <stdio.h>
#include <string.h>

static int check_frame(uint8_t state, uint8_t reason, uint16_t seq,
                       uint32_t frame_id, const uint8_t expected[CAN_OUT_FRAME_SIZE])
{
    uint8_t actual[CAN_OUT_FRAME_SIZE];
    can_out_pack(actual, state, reason, seq, frame_id);
    if (memcmp(actual, expected, CAN_OUT_FRAME_SIZE) != 0) {
        fputs("CAN frame packing mismatch\n", stderr);
        return 1;
    }
    return 0;
}

int main(void)
{
    static const uint8_t mixed_endian[CAN_OUT_FRAME_SIZE] = {
        3u, 10u, 0x34u, 0x12u, 0xefu, 0xcdu, 0xabu, 0x89u
    };
    static const uint8_t zeros[CAN_OUT_FRAME_SIZE] = {0};
    static const uint8_t maximums[CAN_OUT_FRAME_SIZE] = {
        0xffu, 0xffu, 0xffu, 0xffu, 0xffu, 0xffu, 0xffu, 0xffu
    };

    if (check_frame(3u, 10u, 0x1234u, 0x89abcdefu, mixed_endian) != 0 ||
        check_frame(0u, 0u, 0u, 0u, zeros) != 0 ||
        check_frame(0xffu, 0xffu, 0xffffu, 0xffffffffu, maximums) != 0)
        return 1;
    puts("CAN frame packing: 3 cases passed");
    return 0;
}
