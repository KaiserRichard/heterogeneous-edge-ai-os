#ifndef IMU_MPU6050_H
#define IMU_MPU6050_H

#include <stdint.h>

#define IMU_MPU6050_ADDRESS 0x68u
#define IMU_MPU6050_SAMPLE_BYTES 14u
#define IMU_MPU6050_HISTOGRAM_BINS 8u

typedef struct {
    int16_t accel_raw[3];
    int16_t temperature_raw;
    int16_t gyro_raw[3];
    float accel_g[3];
    float temperature_c;
    float gyro_dps[3];
} imu_mpu6050_sample_t;

/* Pure parser/converter. Accelerometer ±2 g, gyro ±250 degree/s defaults. */
void imu_mpu6050_convert(const uint8_t bytes[IMU_MPU6050_SAMPLE_BYTES],
                         imu_mpu6050_sample_t *sample);

#ifndef IMU_MPU6050_HOST_TEST
typedef struct {
    imu_mpu6050_sample_t sample;
    uint32_t sample_cycles;
    uint32_t i2c_errors;
    uint32_t sample_errors;
    uint32_t missed_periods;
    uint32_t jitter_histogram[IMU_MPU6050_HISTOGRAM_BINS];
} imu_mpu6050_state_t;

/* Public latest-value and diagnostics, written by the low-priority IMU task. */
extern imu_mpu6050_state_t imu_state;

/* Initialize I2C1 PB6/PB7, 400 kHz, then verify WHO_AM_I. */
int imu_mpu6050_init(imu_mpu6050_state_t *state);
/* One bounded register read; updates latest sample and CYCCNT timestamp. */
int imu_mpu6050_sample(imu_mpu6050_state_t *state);
/* Record absolute release-period error in 8 bins, each 10 us wide. */
void imu_mpu6050_record_jitter(imu_mpu6050_state_t *state, uint32_t error_cycles);
#endif

#endif
