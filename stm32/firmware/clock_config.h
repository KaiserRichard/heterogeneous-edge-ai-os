#ifndef HEA_CLOCK_CONFIG_H
#define HEA_CLOCK_CONFIG_H
/* Both HSE (8 MHz / M=8) and HSI (16 MHz / M=16): N=336, P=4.
 * AHB /1; APB1 /2 with timer x2; APB2 /1. One nominal clock contract. */
#define HEA_SYSCLK_HZ 84000000UL
#define HEA_TIM2_HZ HEA_SYSCLK_HZ
#define HEA_TICK_HZ 1000
#endif
