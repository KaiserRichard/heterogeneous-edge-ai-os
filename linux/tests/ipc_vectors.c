/* Portable byte vectors emitted by the production C packers. */
#include "hea_ipc.h"
#include <stdio.h>

int main(void)
{
    const struct hea_input input = {UINT32_C(0x01020304), UINT64_C(0x1112131415161718)};
    const struct hea_result result = {UINT32_C(0x01020304),
        UINT64_C(0x1112131415161718), UINT64_C(0x2122232425262728), 231, 50};
    uint8_t bytes[HEA_RESULT_SIZE];
    hea_input_pack(&input, bytes);
    if (fwrite(bytes, 1, HEA_INPUT_SIZE, stdout) != HEA_INPUT_SIZE) return 1;
    hea_result_pack(&result, bytes);
    return fwrite(bytes, 1, HEA_RESULT_SIZE, stdout) != HEA_RESULT_SIZE;
}
