/* Compile-only port: UNVERIFIED ON HARDWARE. Register bits follow RM0390. */
#include "stm32f446xx.h"
#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"
#include "stream_buffer.h"
#include "supervisor_protocol.h"
#include "rx_dma_cursor.h"

#define REG32(a) (*(volatile uint32_t *)(a))
#define FRAME_DEPTH 8u
#define RX_RECORDS 256u
#define APP_STACK 512u
#ifndef UART_BAUD
#define UART_BAUD 921600u
#endif
#define SYSCLK_HZ 84000000u
#define PCLK1_HZ (SYSCLK_HZ / 2u)
#define PCLK2_HZ SYSCLK_HZ
#define UART_BRR ((PCLK2_HZ + UART_BAUD / 2u) / UART_BAUD)
_Static_assert(configTICK_RATE_HZ == 1000, "RX poll requires a 1 ms tick");
_Static_assert(UART_BRR >= 16u && UART_BRR <= 65535u, "USART1 baud out of range");

/* Per-byte ISR timestamp keeps final-CRC-byte receipt independent of RX backlog.
 * Stream entries are fixed size; ISR only writes when an entire record fits. */
typedef struct { uint32_t raw_us; uint8_t byte; uint8_t error; uint8_t pad[2]; } rx_record_t;
typedef struct { struct hea_frame frame; uint64_t receipt, generation; } frame_event_t;
static supervisor_t supervisor;
static uint64_t extended_us;
static struct hea_parser parser;
#if !RX_DMA
static StreamBufferHandle_t rx_stream;
static StaticStreamBuffer_t rx_control;
static uint8_t rx_storage[RX_RECORDS * sizeof(rx_record_t) + 1u];
#else
/* DMA2 Stream2, channel 4; byte-wide, direct-mode circular receive. */
#define DMA_RX_SIZE 2048u
#define DMA2_LISR REG32(0x40026400u)
#define DMA2_LIFCR REG32(0x40026408u)
#define DMA_RX_CR REG32(0x40026440u)
#define DMA_RX_NDTR REG32(0x40026444u)
#define DMA_RX_PAR REG32(0x40026448u)
#define DMA_RX_M0AR REG32(0x4002644cu)
#define DMA_RX_FCR REG32(0x40026454u)
#define DMA_RX_FLAGS (0x3du << 16)
#define DMA_RX_ERRORS ((1u << 16) | (1u << 18) | (1u << 19))
static volatile uint8_t dma_rx[DMA_RX_SIZE];
static TaskHandle_t rx_handle;
static volatile uint32_t rx_error_epoch;
#endif
static QueueHandle_t frames, echoes, captures;
static StaticQueue_t frame_control, echo_control, capture_control;
static uint8_t frame_storage[FRAME_DEPTH * sizeof(frame_event_t)];
static uint8_t echo_storage[FRAME_DEPTH * sizeof(struct hea_echo_resp)];
static uint8_t capture_storage[8u * sizeof(uint32_t)];
static StaticTask_t task_controls[3], idle_control;
static StackType_t stacks[3][APP_STACK], idle_stack[configMINIMAL_STACK_SIZE];
static volatile uint32_t rx_dropped, uart_errors, capture_lost;
static volatile uint32_t uart_ore, uart_fe, uart_ne, uart_pe;
extern volatile uint32_t max_irq_masked_cycles;
void hea_irq_timing_reset(void);
static uint32_t queue_dropped;
static uint16_t missed_heartbeats;
static supervisor_state_t published_state;
static uint16_t tx_seq;
static TaskHandle_t status_handle;
static uint8_t clock_fallback;

static void increment(volatile uint32_t *counter)
{
    if (*counter != UINT32_MAX) ++*counter;
}

#if RX_DMA
static void dma_drop(void)
{
    taskENTER_CRITICAL(); /* rx_dropped also has a USART ISR writer */
    increment(&rx_dropped);
    taskEXIT_CRITICAL();
}
#endif

static void output(supervisor_state_t state)
{
    /* Two-wire code: PA5/PB5 = 00 safe INIT/FAILSAFE, 11 FRESH, 01 HOLD.
     * HOLD explicitly inhibits new output on PA5, PB5 denotes grace state. */
    GPIOA->BSRR = state == SUPERVISOR_STATE_FRESH ? (1u << 5) : (1u << 21);
    GPIOB->BSRR = (state == SUPERVISOR_STATE_FRESH || state == SUPERVISOR_STATE_HOLD)
                    ? (1u << 5) : (1u << 21);
}

void firmware_fault(void)
{
    __asm volatile ("cpsid i" ::: "memory");
    RCC->AHB1ENR |= 3u;
    (void)RCC->AHB1ENR;
    GPIOA->BSRR = 1u << 21;
    GPIOB->BSRR = 1u << 21;
    GPIOA->MODER = (GPIOA->MODER & ~(3u << 10)) | (1u << 10);
    GPIOB->MODER = (GPIOB->MODER & ~(3u << 10)) | (1u << 10);
    for (;;) __asm volatile ("wfi");
}
void vApplicationStackOverflowHook(TaskHandle_t task, char *name)
{
    (void)task; (void)name; firmware_fault();
}
void vApplicationMallocFailedHook(void) { firmware_fault(); }
void vApplicationGetIdleTaskMemory(StaticTask_t **tcb, StackType_t **stack, uint32_t *size)
{
    *tcb = &idle_control; *stack = idle_stack; *size = configMINIMAL_STACK_SIZE;
}

static void alternate(GPIO_RegDef_t *gpio, unsigned pin, unsigned af)
{
    gpio->MODER = (gpio->MODER & ~(3u << (pin * 2u))) | (2u << (pin * 2u));
    gpio->AFR[pin / 8u] = (gpio->AFR[pin / 8u] & ~(15u << ((pin % 8u) * 4u))) |
                         (af << ((pin % 8u) * 4u));
    gpio->OSPEEDER |= 3u << (pin * 2u);
}
static void irq_enable(unsigned irq)
{
    ((volatile uint8_t *)0xe000e400u)[irq] = 6u << 4; /* numerically >= 5 */
    ((volatile uint32_t *)0xe000e280u)[irq / 32u] = 1u << (irq % 32u);
    ((volatile uint32_t *)0xe000e100u)[irq / 32u] = 1u << (irq % 32u);
}
static void board_init(void)
{
    RCC->AHB1ENR |= 3u;
    (void)RCC->AHB1ENR;
    output(SUPERVISOR_STATE_INIT);
    GPIOA->MODER = (GPIOA->MODER & ~(3u << 10)) | (1u << 10);
    GPIOB->MODER = (GPIOB->MODER & ~(3u << 10)) | (1u << 10);
    /* HSE bypass 8 MHz: M=8; HSI 16 MHz: M=16. N=336/P=4 in both.
     * APB1 /2 = 42 MHz, timer clock doubles to 84 MHz; APB2 /1. */
    RCC->CR |= 1u;
    while (!(RCC->CR & 2u)) { }
    RCC->CFGR = 0;
    while (RCC->CFGR & 12u) { }
    RCC->CR &= ~(1u << 24);
    while (RCC->CR & (1u << 25)) { }
    RCC->APB1ENR |= 1u << 28;
    PWR->CR |= 3u << 14; /* voltage scale 1 */
    REG32(FLASHINTR_BASEADDR) = 2u | (7u << 8); /* 2 WS at 3.3 V, caches/prefetch */
    uint32_t pll_source = 16u;
#if CLOCK_HSE
    /* SysTick at reset HSI/8 (2 MHz): bounded 100 ms startup timeout.
     * FreeRTOS configures SysTick afresh when the scheduler starts. */
    RCC->CR &= ~(1u << 16);
    RCC->CR |= 1u << 18; /* HSEBYP: ST-LINK MCO on PH0/OSC_IN */
    REG32(0xe000e014u) = 200000u - 1u;
    REG32(0xe000e018u) = 0;
    REG32(0xe000e010u) = 1u; /* enable, no interrupt, HCLK/8 */
    RCC->CR |= 1u << 16;
    while (!(RCC->CR & (1u << 17)) && !(REG32(0xe000e010u) & (1u << 16))) { }
    REG32(0xe000e010u) = 0;
    REG32(0xe000e018u) = 0;
    if (RCC->CR & (1u << 17)) pll_source = 8u | (1u << 22);
    else {
        clock_fallback = 1;
        RCC->CR &= ~(1u << 16);
    }
#endif
    RCC->PLLCFGR = pll_source | (336u << 6) | (1u << 16) | (7u << 24);
    RCC->CFGR = 4u << 10;
    RCC->CR |= 1u << 24;
    while (!(RCC->CR & (1u << 25))) { }
    RCC->CFGR |= 2u;
    while ((RCC->CFGR & 12u) != 8u) { }
    REG32(0xe000ed08u) = FLASH_BASEADDR; /* VTOR */
    REG32(0xe000ed0cu) = 0x05fa0000u | (3u << 8); /* four preemption bits */
    REG32(0xe000edfcu) |= 1u << 24; /* DEMCR.TRCENA */
    REG32(0xe0001004u) = 0; /* DWT.CYCCNT */
    REG32(0xe0001000u) |= 1u; /* DWT.CTRL.CYCCNTENA */
    RCC->APB1ENR |= 1u; /* TIM2 */
    RCC->APB2ENR |= 1u << 4; /* USART1 */
    (void)RCC->APB2ENR;
    alternate(GPIOA, 0, 1);
    GPIOA->PUPDR = (GPIOA->PUPDR & ~3u) | 2u; /* sync idle low */
    TIM2->PSC = SYSCLK_HZ / 1000000u - 1u;
    TIM2->ARR = UINT32_MAX;
    TIM2->CCMR1 = 1u; /* CC1 mapped directly to TI1, no filter */
    TIM2->CCER = 1u; /* rising edge */
    TIM2->EGR = 1u;
    TIM2->SR = 0;
    TIM2->DIER = 2u;
    TIM2->CR1 = 1u;
    alternate(GPIOA, 9, 7);
    alternate(GPIOA, 10, 7);
    GPIOA->PUPDR = (GPIOA->PUPDR & ~(3u << 20)) | (1u << 20);
    USART1->BRR = UART_BRR;
    USART1->CR1 = (1u << 13) | (1u << 3) | (1u << 2); /* 8N1 */
#if DEBUG_VCP
    RCC->APB1ENR |= 1u << 17;
    (void)RCC->APB1ENR;
    alternate(GPIOA, 2, 7); alternate(GPIOA, 3, 7);
    USART2->BRR = (PCLK1_HZ + 57600u) / 115200u;
    USART2->CR1 = (1u << 13) | (1u << 3) | (1u << 2);
    const char *s = "HEA 84MHz UNVERIFIED ON HARDWARE\r\n";
    while (*s) {
        while (!(USART2->SR & (1u << 7))) { }
        USART2->DR = (uint8_t)*s++;
    }
#endif
}
/* Call only inside a task critical section. A 1 kHz owner samples even idle. */
static uint64_t now_locked(void)
{
    uint64_t next;
    if (!supervisor_extend_mcu_us(extended_us, TIM2->CNT, &next)) firmware_fault();
    extended_us = next;
    return next;
}
static void uart_error_count(uint32_t sr)
{
    if (!(sr & 15u)) return;
    increment(&uart_errors); /* error-bearing SR samples, not sum of flags */
    if (sr & (1u << 3)) increment(&uart_ore);
    if (sr & (1u << 1)) increment(&uart_fe);
    if (sr & (1u << 2)) increment(&uart_ne);
    if (sr & 1u) increment(&uart_pe);
}
void USART1_Handler(void)
{
#if RX_DMA
    BaseType_t wake = pdFALSE;
    uint32_t sr = USART1->SR;
    if (sr & ((1u << 4) | 15u)) {
        /* RM0390: SR then DR clears IDLE and PE/FE/NE/ORE. DMA continues.
         * If RXNE is still pending, conservatively mark a possible stolen byte
         * as a discontinuity rather than delivering a corrupt partial frame. */
        uint32_t pending = USART1->SR;
        (void)USART1->DR;
        uart_error_count(sr | pending);
        if ((sr | pending) & 15u || pending & (1u << 5)) {
            ++rx_error_epoch;
            increment(&rx_dropped);
        }
        vTaskNotifyGiveFromISR(rx_handle, &wake);
    }
    portYIELD_FROM_ISR(wake);
#else
    static uint8_t gap;
    BaseType_t wake = pdFALSE;
    uint32_t sr = USART1->SR;
    if (sr & ((1u << 5) | 15u)) {
        rx_record_t record = { .raw_us = TIM2->CNT, .byte = (uint8_t)USART1->DR,
                               .error = (sr & 15u) != 0u };
        uart_error_count(sr);
        record.error |= gap;
        if (xStreamBufferSpacesAvailable(rx_stream) >= sizeof record) {
            if (xStreamBufferSendFromISR(rx_stream, &record, sizeof record, &wake) != sizeof record)
                firmware_fault();
            gap = 0;
        } else {
            increment(&rx_dropped);
            gap = 1;
        }
    }
    portYIELD_FROM_ISR(wake);
#endif
}
void TIM2_Handler(void)
{
    BaseType_t wake = pdFALSE;
    uint32_t sr = TIM2->SR;
    if (sr & 2u) {
        uint32_t capture = TIM2->CCR1; /* SR read then CCR1 clears CC1IF */
        if (xQueueSendFromISR(captures, &capture, &wake) != pdPASS) increment(&capture_lost);
    }
    if (sr & (1u << 9)) {
        TIM2->SR = ~(1u << 9); /* write-zero-to-clear only overcapture */
        increment(&capture_lost);
    }
    portYIELD_FROM_ISR(wake);
}
static void rx_task(void *argument)
{
    (void)argument;
#if RX_DMA
    unsigned consumed = 0;
    uint32_t epoch = rx_error_epoch;
    uint32_t sampled_at = TIM2->CNT;
#endif
    for (;;) {
        rx_record_t record;
#if RX_DMA
        (void)ulTaskNotifyTake(pdTRUE, 1); /* IDLE wakeup or 1 ms poll */
        uint32_t sampled = TIM2->CNT;
        unsigned produced = rx_dma_position(DMA_RX_SIZE, DMA_RX_NDTR);
        __asm volatile ("dmb" ::: "memory");
        uint32_t errors = DMA2_LISR & DMA_RX_ERRORS;
        /* Do not infer empty from equal indices after a possible whole lap.
         * At the configured baud, this elapsed time can fill the entire ring.
         * Discard conservatively, even if the line may actually have been idle. */
        bool late = rx_dma_lap_possible(sampled, sampled_at, DMA_RX_SIZE,
                    (PCLK2_HZ + UART_BRR - 1u) / UART_BRR);
        uint32_t drain_started = sampled_at;
        sampled_at = sampled;
        if (errors) firmware_fault(); /* DMA bus/config failure: safe outputs */
        DMA2_LIFCR = DMA_RX_FLAGS;
        if (late || epoch != rx_error_epoch) {
            if (late) dma_drop();
            epoch = rx_error_epoch;
            consumed = produced;
            parser.state = HEA_P_SOF0;
            continue;
        }
        /* One snapshot is bounded to <one ring. New bytes wait for next drain. */
        while (consumed != produced) {
            record.byte = dma_rx[consumed];
            record.raw_us = TIM2->CNT; /* time RX task sees this byte */
            consumed = (consumed + 1u) % DMA_RX_SIZE;
            if (rx_dma_lap_possible(record.raw_us, drain_started, DMA_RX_SIZE,
                (PCLK2_HZ + UART_BRR - 1u) / UART_BRR)) {
                dma_drop();
                parser.state = HEA_P_SOF0;
                consumed = produced;
                break;
            }
            if (epoch != rx_error_epoch) {
                parser.state = HEA_P_SOF0;
                break;
            }
#else
        size_t n = xStreamBufferReceive(rx_stream, &record, sizeof record, portMAX_DELAY);
        configASSERT(n == sizeof record);
        if (record.error) {
            /* Preserve statistics, discard partial framing after byte loss. */
            parser.state = HEA_P_SOF0;
            continue;
        }
#endif
        if (!hea_parser_feed(&parser, record.byte)) continue;
        frame_event_t event = { .frame = parser.frame };
        taskENTER_CRITICAL();
#if RX_DMA
        if (epoch != rx_error_epoch) {
            taskEXIT_CRITICAL();
            parser.state = HEA_P_SOF0;
            continue;
        }
#endif
        uint64_t now = now_locked();
        uint32_t age = (uint32_t)now - record.raw_us;
        if (age >= 0x80000000u || now < age) firmware_fault();
        event.receipt = now - age; /* reconstruct from recent extended sample */
        event.generation = supervisor.generation;
        taskEXIT_CRITICAL();
        if (xQueueSend(frames, &event, 0) != pdPASS) {
            increment(&queue_dropped);
            continue;
        }
        struct hea_echo_req request;
        if (hea_unpack_echo_req(&event.frame, &request) == 0) {
            struct hea_echo_resp response = {request.linux_t1_ns, record.raw_us, 0};
            if (xQueueSend(echoes, &response, 0) != pdPASS) increment(&queue_dropped);
        }
#if RX_DMA
        }
#endif
    }
}
static uint64_t now_task(void)
{
    taskENTER_CRITICAL();
    uint64_t now = now_locked();
    taskEXIT_CRITICAL();
    return now;
}
static void supervisor_task(void *argument)
{
    (void)argument;
    TickType_t release = xTaskGetTickCount();
    hea_irq_timing_reset(); /* exclude pre-scheduler BASEPRI ownership */
    /* Enable only after scheduler starts and every IPC object exists. */
    (void)USART1->SR; (void)USART1->DR;
#if RX_DMA
    RCC->AHB1ENR |= 1u << 22; /* DMA2 clock */
    (void)RCC->AHB1ENR;
    DMA_RX_CR = 0;
    while (DMA_RX_CR & 1u) { }
    DMA2_LIFCR = DMA_RX_FLAGS;
    DMA_RX_PAR = (uint32_t)&USART1->DR;
    DMA_RX_M0AR = (uint32_t)dma_rx;
    DMA_RX_NDTR = DMA_RX_SIZE;
    DMA_RX_FCR = 0; /* direct mode; byte memory writes precede NDTR decrement */
    DMA_RX_CR = (4u << 25) | (2u << 16) | (1u << 10) | (1u << 8) | 1u;
    USART1->CR3 |= (1u << 6) | 1u; /* DMAR, EIE */
    USART1->CR1 |= (1u << 4) | (1u << 8); /* IDLEIE, PEIE; no RXNEIE */
#else
    USART1->CR3 |= 1u; /* EIE */
    USART1->CR1 |= (1u << 5) | (1u << 8); /* RXNEIE, PEIE */
#endif
    irq_enable(37);
    irq_enable(28);
    for (;;) {
        /* Sole highest-priority owner: no ISR accesses the supervisor.
         * Lower-priority readers suspend scheduling when taking snapshots. */
        bool events_pending = supervisor.transition_count != 0u;
        supervisor_state_t previous = supervisor.state;
        supervisor_update(&supervisor, NULL, now_task());
        /* Bounded batch prevents traffic from extending one release forever. */
        for (unsigned i = 0; i < FRAME_DEPTH; ++i) {
            frame_event_t event;
            if (xQueueReceive(frames, &event, 0) != pdPASS) break;
            supervisor_receive_frame(&supervisor, &event.frame, event.generation,
                                     event.receipt, now_task());
        }
        if (previous != SUPERVISOR_STATE_FAILSAFE && supervisor.state == SUPERVISOR_STATE_FAILSAFE &&
            supervisor.last_transition_reason == SUPERVISOR_REASON_HEARTBEAT_TIMEOUT &&
            missed_heartbeats != UINT16_MAX) ++missed_heartbeats;
        published_state = supervisor.state;
        output(published_state);
        if (!events_pending && supervisor.transition_count != 0u) xTaskNotifyGive(status_handle);
#if BRINGUP_BLINK
        /* Diagnostic image only: PB5 stays safe; PA5 toggles at 1 Hz. */
        GPIOB->BSRR = 1u << 21;
        GPIOA->BSRR = (release % 1000u < 500u) ? (1u << 5) : (1u << 21);
#endif
        vTaskDelayUntil(&release, 1);
    }
}
static void send_frame(uint8_t type, const uint8_t *payload, uint8_t length)
{
    uint8_t bytes[HEA_MAX_FRAME];
    size_t n = hea_encode(type, tx_seq++, payload, length, bytes, sizeof bytes);
    for (size_t i = 0; i < n; ++i) {
        uint32_t start = TIM2->CNT;
        while (!(USART1->SR & (1u << 7))) {
            if ((uint32_t)(TIM2->CNT - start) > 10000u) firmware_fault();
        }
        USART1->DR = bytes[i];
    }
}
static void status_task(void *argument)
{
    (void)argument;
    TickType_t release = xTaskGetTickCount();
    struct hea_mcu_status_extended status = {0};
    for (;;) {
        uint32_t capture;
        for (unsigned i = 0; i < 8u && xQueueReceive(captures, &capture, 0) == pdPASS; ++i) {
            status.last_capture_us = capture;
            increment(&status.capture_count);
        }
        uint8_t payload[HEA_MAX_PAYLOAD];
        /* Drain events every tick, independent of 10 Hz status; never TX in ISR.
         * Bounded batch leaves time for echoes/status under sustained transitions. */
        for (unsigned i = 0; i < SUPERVISOR_TRANSITION_DEPTH; ++i) {
            struct hea_state_event event;
            vTaskSuspendAll(); /* Serialize with sole owner; IRQs stay enabled. */
            bool available = supervisor_pop_transition(&supervisor, &event);
            (void)xTaskResumeAll();
            if (!available) break;
            uint8_t length = hea_pack_state_event(&event, payload);
            send_frame(HEA_MSG_STATE_EVENT, payload, length);
        }
        /* Sole TX owner: at most one echo per iteration, bounded status delay. */
        struct hea_echo_resp echo;
        if (xQueueReceive(echoes, &echo, 0) == pdPASS) {
            /* Wait for prior status/echo wire completion before sampling T3. */
            uint32_t start = TIM2->CNT;
            while (!(USART1->SR & (1u << 6))) {
                if ((uint32_t)(TIM2->CNT - start) > 10000u) firmware_fault();
            }
            echo.mcu_tx_us = TIM2->CNT;
            uint8_t length = hea_pack_echo_resp(&echo, payload);
            send_frame(HEA_MSG_ECHO_RESP, payload, length);
        }
        if ((TickType_t)(xTaskGetTickCount() - release) >= pdMS_TO_TICKS(100)) {
            release += pdMS_TO_TICKS(100);
            vTaskSuspendAll();
            status.base.mcu_us = TIM2->CNT;
            status.base.state = (uint8_t)published_state;
            status.base.missed_heartbeats = missed_heartbeats;
            status.base.rx_crc_errors = parser.stats.crc_errors > UINT16_MAX ? UINT16_MAX :
                                        (uint16_t)parser.stats.crc_errors;
            status.rx_dropped = rx_dropped;
            status.queue_dropped = queue_dropped; status.capture_lost = capture_lost;
            status.clock_fallback = clock_fallback;
            status.state_event_lost = supervisor.transition_lost;
            (void)xTaskResumeAll();
            /* ISR-owned counters: coherent short snapshot, no supervisor work. */
            taskENTER_CRITICAL();
            status.uart_errors = uart_errors;
            status.uart_ore = uart_ore; status.uart_fe = uart_fe;
            status.uart_ne = uart_ne; status.uart_pe = uart_pe;
            status.max_irq_masked_cycles = max_irq_masked_cycles;
            taskEXIT_CRITICAL();
            uint8_t length = hea_pack_mcu_status_extended(&status, payload);
            send_frame(HEA_MSG_MCU_STATUS, payload, length);
        }
        (void)ulTaskNotifyTake(pdTRUE, 1); /* event wakeup, otherwise one-tick polling */
    }
}
int main(void)
{
    board_init();
    extended_us = TIM2->CNT;
    /* PROVISIONAL educational thresholds, in us; calibrate on the rig. */
    const supervisor_config_t config = {100000, 200000, 500000, 1000000, 5000};
    configASSERT(supervisor_init(&supervisor, &config, extended_us));
    hea_parser_init(&parser);
#if !RX_DMA
    rx_stream = xStreamBufferCreateStatic(sizeof rx_storage, sizeof(rx_record_t), rx_storage, &rx_control);
    configASSERT(rx_stream);
#endif
    frames = xQueueCreateStatic(FRAME_DEPTH, sizeof(frame_event_t), frame_storage, &frame_control);
    echoes = xQueueCreateStatic(FRAME_DEPTH, sizeof(struct hea_echo_resp), echo_storage, &echo_control);
    captures = xQueueCreateStatic(8, sizeof(uint32_t), capture_storage, &capture_control);
    configASSERT(frames && echoes && captures);
    configASSERT(xTaskCreateStatic(supervisor_task, "supervisor", APP_STACK, NULL, 3, stacks[0], &task_controls[0]));
#if RX_DMA
    rx_handle = xTaskCreateStatic(rx_task, "rx", APP_STACK, NULL, 2, stacks[1], &task_controls[1]);
    configASSERT(rx_handle);
#else
    configASSERT(xTaskCreateStatic(rx_task, "rx", APP_STACK, NULL, 2, stacks[1], &task_controls[1]));
#endif
    status_handle = xTaskCreateStatic(status_task, "status_tx", APP_STACK, NULL, 1, stacks[2], &task_controls[2]);
    configASSERT(status_handle);
    vTaskStartScheduler();
    firmware_fault();
}
