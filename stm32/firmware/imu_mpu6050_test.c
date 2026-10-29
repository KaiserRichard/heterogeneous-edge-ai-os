#include "imu_mpu6050.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>

int main(void)
{
    const uint8_t bytes[IMU_MPU6050_SAMPLE_BYTES] = {
        0x40,0x00, 0xc0,0x00, 0x20,0x00, 0x00,0x00,
        0x20,0x00, 0xe0,0x00, 0x00,0x83
    };
    imu_mpu6050_sample_t sample;
    imu_mpu6050_convert(bytes, &sample);
    assert(sample.accel_raw[0] == 16384 && sample.accel_raw[1] == -16384);
    assert(sample.accel_raw[2] == 8192 && sample.temperature_raw == 0);
    assert(sample.gyro_raw[0] == 8192 && sample.gyro_raw[1] == -8192);
    assert(sample.gyro_raw[2] == 131);
    assert(fabsf(sample.accel_g[0] - 1.0f) < 0.0001f);
    assert(fabsf(sample.accel_g[1] + 1.0f) < 0.0001f);
    assert(fabsf(sample.temperature_c - 36.53f) < 0.001f);
    assert(fabsf(sample.gyro_dps[2] - 1.0f) < 0.0001f);
    puts("PASS: MPU6050 big-endian raw values and scaled units");
    return 0;
}
