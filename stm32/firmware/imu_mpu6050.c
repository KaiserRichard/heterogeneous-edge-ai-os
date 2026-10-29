#include "imu_mpu6050.h"

void imu_mpu6050_convert(const uint8_t bytes[IMU_MPU6050_SAMPLE_BYTES],
                         imu_mpu6050_sample_t *sample)
{
    int16_t raw[7];
    for (unsigned i = 0; i < 7u; ++i)
        raw[i] = (int16_t)((uint16_t)((uint16_t)bytes[i * 2u] << 8) |
                           (uint16_t)bytes[i * 2u + 1u]);
    for (unsigned i = 0; i < 3u; ++i) {
        sample->accel_raw[i] = raw[i];
        sample->accel_g[i] = (float)raw[i] / 16384.0f;
        sample->gyro_raw[i] = raw[i + 4u];
        sample->gyro_dps[i] = (float)raw[i + 4u] / 131.0f;
    }
    sample->temperature_raw = raw[3];
    sample->temperature_c = (float)raw[3] / 340.0f + 36.53f;
}

#ifndef IMU_MPU6050_HOST_TEST
#include "stm32f446xx.h"

#define I2C_SR1 REG32(0x40005414u)
#define I2C_SR2 REG32(0x40005418u)
#define I2C_DR  REG32(0x40005410u)
#define I2C_CR1 REG32(0x40005400u)
#define I2C_CR2 REG32(0x40005404u)
#define I2C_CCR REG32(0x4000541cu)
#define I2C_TRISE REG32(0x40005420u)
#define REG32(a) (*(volatile uint32_t *)(a))
#define I2C_TIMEOUT_CYCLES 420000u /* 5 ms at 84 MHz */

static int wait_sr1(uint32_t mask)
{
    uint32_t start = REG32(0xe0001004u);
    while (!(I2C_SR1 & mask)) {
        if ((uint32_t)(REG32(0xe0001004u) - start) > I2C_TIMEOUT_CYCLES ||
            (I2C_SR1 & ((1u << 8) | (1u << 10)))) return 0;
    }
    return 1;
}

static int start_address(uint8_t address, int read)
{
    I2C_CR1 |= 1u << 8;
    if (!wait_sr1(1u << 0)) return 0;
    I2C_DR = (uint32_t)(address << 1) | (read ? 1u : 0u);
    if (!wait_sr1(1u << 1)) return 0;
    (void)I2C_SR1; (void)I2C_SR2;
    return 1;
}

static void stop(void)
{
    I2C_CR1 |= 1u << 9;
    I2C_CR1 |= 1u << 10; /* ACK for the next transaction */
}

static int read_register(uint8_t reg, uint8_t *data, unsigned length)
{
    if (!start_address(IMU_MPU6050_ADDRESS, 0)) goto fail;
    I2C_DR = reg;
    if (!wait_sr1(1u << 7)) goto fail;
    if (!start_address(IMU_MPU6050_ADDRESS, 1)) goto fail;
    for (unsigned i = 0; i < length; ++i) {
        if (i + 1u == length) {
            I2C_CR1 &= ~(1u << 10);
            I2C_CR1 |= 1u << 9;
        }
        if (!wait_sr1(1u << 6)) goto fail;
        data[i] = (uint8_t)I2C_DR;
    }
    return 1;
fail:
    stop();
    return 0;
}

int imu_mpu6050_init(imu_mpu6050_state_t *state)
{
    uint8_t who = 0;
    RCC->AHB1ENR |= 1u << 1;
    RCC->APB1ENR |= 1u << 21;
    (void)RCC->APB1ENR;
    /* PB6/PB7 AF4, open drain, high speed, external pull-ups on the rig. */
    for (unsigned pin = 6u; pin <= 7u; ++pin) {
        GPIOB->MODER = (GPIOB->MODER & ~(3u << (pin * 2u))) | (2u << (pin * 2u));
        GPIOB->OTYPER |= 1u << pin;
        GPIOB->OSPEEDER |= 3u << (pin * 2u);
        GPIOB->PUPDR &= ~(3u << (pin * 2u));
        GPIOB->AFR[0] = (GPIOB->AFR[0] & ~(15u << (pin * 4u))) | (4u << (pin * 4u));
    }
    I2C_CR1 = 0;
    I2C_CR2 = 42u;
    /* Fm, DUTY=0 (Tlow/Thigh = 2): 42 MHz / (3 * 35) = 400 kHz. */
    I2C_CCR = (1u << 15) | 35u;
    I2C_TRISE = 13u;
    I2C_CR1 = 1u;
    I2C_CR1 |= 1u << 10;
    if (!read_register(0x75u, &who, 1u) || who != IMU_MPU6050_ADDRESS) {
        if (state->i2c_errors != UINT32_MAX) ++state->i2c_errors;
        return 0;
    }
    /* Wake sensor; keep default ±2 g / ±250 dps full-scale ranges. */
    if (!start_address(IMU_MPU6050_ADDRESS, 0)) goto fail;
    I2C_DR = 0x6bu;
    if (!wait_sr1(1u << 7)) goto fail;
    I2C_DR = 0;
    if (!wait_sr1(1u << 7)) goto fail;
    stop();
    return 1;
fail:
    stop();
    if (state->i2c_errors != UINT32_MAX) ++state->i2c_errors;
    return 0;
}

int imu_mpu6050_sample(imu_mpu6050_state_t *state)
{
    uint8_t bytes[IMU_MPU6050_SAMPLE_BYTES];
    if (!read_register(0x3bu, bytes, sizeof bytes)) {
        if (state->i2c_errors != UINT32_MAX) ++state->i2c_errors;
        if (state->sample_errors != UINT32_MAX) ++state->sample_errors;
        return 0;
    }
    uint32_t sample_cycles = REG32(0xe0001004u);
    imu_mpu6050_convert(bytes, &state->sample);
    state->sample_cycles = sample_cycles;
    return 1;
}

void imu_mpu6050_record_jitter(imu_mpu6050_state_t *state, uint32_t error_cycles)
{
    /* 84 MHz: bins 0..6 span [0,70) us; bin 7 is >=70 us. */
    unsigned bin = error_cycles / 840u;
    if (bin >= IMU_MPU6050_HISTOGRAM_BINS) bin = IMU_MPU6050_HISTOGRAM_BINS - 1u;
    if (state->jitter_histogram[bin] != UINT32_MAX) ++state->jitter_histogram[bin];
}
#endif
