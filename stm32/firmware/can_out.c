#include "can_out.h"

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define REG32(address) (*(volatile uint32_t *)(uintptr_t)(address))
#if defined(__arm__) || defined(__thumb__)
#define CAN_VECTOR_BARRIER() __asm volatile ("dsb\n\tisb" ::: "memory")
#else
#define CAN_VECTOR_BARRIER() ((void)0)
#endif

#define RCC_BASE 0x40023800u
#define RCC_AHB1ENR (RCC_BASE + 0x30u)
#define RCC_APB1ENR (RCC_BASE + 0x40u)
#define GPIOB_BASE 0x40020400u
#define CAN1_BASE 0x40006400u
#define CAN2_BASE 0x40006800u
#define CAN_FILTER_BASE 0x40006600u
#define TIM2_CNT 0x40000024u

#define CAN_MCR 0x00u
#define CAN_MSR 0x04u
#define CAN_TSR 0x08u
#define CAN_RF0R 0x0cu
#define CAN_IER 0x14u
#define CAN_ESR 0x18u
#define CAN_BTR 0x1cu
#define CAN_TX_MAILBOXES 0x180u
#define CAN_RX_FIFO0 0x1b0u

#define CAN_MCR_INRQ (1u << 0)
#define CAN_MCR_ABOM (1u << 6)
#define CAN_MCR_NART (1u << 4)
#define CAN_MSR_INAK (1u << 0)
#define CAN_RF0R_FMP_MASK 3u
#define CAN_RF0R_FOVR0 (1u << 4)
#define CAN_RF0R_RFOM0 (1u << 5)
#define CAN_IER_FMPIE0 (1u << 1)
#define CAN_IER_FOVIE0 (1u << 3)
#define CAN_ESR_EWGF (1u << 0)
#define CAN_ESR_EPVF (1u << 1)
#define CAN_ESR_BOFF (1u << 2)
#define CAN_ESR_LEC_SHIFT 4u
#define CAN_ESR_LEC_MASK (7u << CAN_ESR_LEC_SHIFT)
#define CAN_ESR_TEC_SHIFT 16u
#define CAN_ESR_REC_SHIFT 24u

#define CAN_FILTER_FMR 0x200u
#define CAN_FILTER_FM1R 0x204u
#define CAN_FILTER_FS1R 0x20cu
#define CAN_FILTER_FFA1R 0x214u
#define CAN_FILTER_FA1R 0x21cu
#define CAN_FILTER_BANK14 14u
#define CAN_FILTER_BANK14_BIT (1u << CAN_FILTER_BANK14)
#define CAN_FILTER_FR1(bank) (0x240u + ((bank) * 8u))
#define CAN_FILTER_FR2(bank) (0x244u + ((bank) * 8u))
#define CAN_FILTER_CAN2_START 14u

#define CAN_TX_MAILBOX_TIR 0x00u
#define CAN_TX_MAILBOX_TDTR 0x04u
#define CAN_TX_MAILBOX_TDLR 0x08u
#define CAN_TX_MAILBOX_TDHR 0x0cu
#define CAN_RX_FIFO_RIR 0x00u
#define CAN_RX_FIFO_RDTR 0x04u
#define CAN_RX_FIFO_RDLR 0x08u
#define CAN_RX_FIFO_RDHR 0x0cu
#define CAN_TIR_TXRQ (1u << 0)
#define CAN_TSR_TME0 (1u << 26)
#define CAN_TSR_RQCP0 (1u << 0)
#define CAN_TSR_TXOK0 (1u << 1)
#define CAN_RX_RIR_IDE (1u << 2)
#define CAN_RX_RIR_RTR (1u << 1)
#define CAN_NVIC_IPR 0xe000e400u
#define CAN_NVIC_ISER 0xe000e100u
#define CAN_SCB_VTOR 0xe000ed08u
#define CAN2_RX0_IRQ 64u
#define VECTOR_WORDS 128u
#define SOURCE_VECTOR_WORDS 113u
#define CAN2_RX0_VECTOR (16u + CAN2_RX0_IRQ)
#define CAN_OUT_PENDING_DEPTH 8u

#define CAN_BIT_TQ_COUNT (1u + CAN_BIT_BS1_TQ + CAN_BIT_BS2_TQ)
#define CAN_BIT_BS1_TQ 11u
#define CAN_BIT_BS2_TQ 2u
#define CAN_BIT_SJW_TQ 1u
#define CAN_INIT_TIMEOUT 1000000u

volatile can_out_stats_t can_out_stats;
#if !defined(CAN_OUT_HOST_TEST)
extern const uint32_t vectors[];
extern void firmware_fault(void);
static uint32_t can_out_vectors[VECTOR_WORDS] __attribute__((aligned(512)));
#endif

static bool can_active;
typedef struct {
    bool active;
    uint8_t state;
    uint8_t reason;
    uint16_t seq;
    uint32_t changed_us;
} pending_state_rx_t;
static volatile pending_state_rx_t pending_state_rx[CAN_OUT_PENDING_DEPTH];
static unsigned pending_write;
static unsigned latest_pending = CAN_OUT_PENDING_DEPTH;
static bool have_last_state;
static uint8_t last_state;
static uint8_t last_reason;
static uint32_t next_periodic_us;
static uint16_t tx_sequence;
static bool can1_was_bus_off;
static bool can2_was_bus_off;
static bool can1_was_warning;
static bool can2_was_warning;
static bool can1_was_passive;
static bool can2_was_passive;

static void increment(volatile uint32_t *counter)
{
    if (*counter != UINT32_MAX) ++*counter;
}

void can_out_pack(uint8_t out[CAN_OUT_FRAME_SIZE], uint8_t state,
                  uint8_t reason, uint16_t seq, uint32_t frame_id)
{
    out[0] = state;
    out[1] = reason;
    out[2] = (uint8_t)seq;
    out[3] = (uint8_t)(seq >> 8);
    out[4] = (uint8_t)frame_id;
    out[5] = (uint8_t)(frame_id >> 8);
    out[6] = (uint8_t)(frame_id >> 16);
    out[7] = (uint8_t)(frame_id >> 24);
}

static void gpio_b_alternate(unsigned pin)
{
    volatile uint32_t *moder = &REG32(GPIOB_BASE);
    volatile uint32_t *pupdr = &REG32(GPIOB_BASE + 0x0cu);
    volatile uint32_t *afr_high = &REG32(GPIOB_BASE + 0x24u);
    unsigned mode_shift = pin * 2u;
    unsigned af_shift = (pin - 8u) * 4u;

    *moder = (*moder & ~(3u << mode_shift)) | (2u << mode_shift);
    *pupdr &= ~(3u << mode_shift); /* transceiver drives RX; no internal pull */
    *afr_high = (*afr_high & ~(15u << af_shift)) | (9u << af_shift);
    REG32(GPIOB_BASE + 0x08u) |= 3u << mode_shift;
}

static bool wait_for_init_state(uint32_t base, bool in_init)
{
    for (uint32_t timeout = 0; timeout < CAN_INIT_TIMEOUT; ++timeout) {
        bool current = (REG32(base + CAN_MSR) & CAN_MSR_INAK) != 0u;
        if (current == in_init) return true;
    }
    return false;
}

static void configure_filter(void)
{
    uint32_t fmr = REG32(CAN_FILTER_BASE + CAN_FILTER_FMR);
    REG32(CAN_FILTER_BASE + CAN_FILTER_FMR) = fmr | 1u; /* FINIT before CANSB */
    fmr &= ~(0x3fu << 8);
    fmr |= (CAN_FILTER_CAN2_START << 8) | 1u; /* CAN2 starts at bank 14; FINIT */
    REG32(CAN_FILTER_BASE + CAN_FILTER_FMR) = fmr;
    REG32(CAN_FILTER_BASE + CAN_FILTER_FA1R) &= ~CAN_FILTER_BANK14_BIT;
    REG32(CAN_FILTER_BASE + CAN_FILTER_FM1R) &= ~CAN_FILTER_BANK14_BIT; /* mask mode */
    REG32(CAN_FILTER_BASE + CAN_FILTER_FS1R) |= CAN_FILTER_BANK14_BIT; /* 32-bit */
    REG32(CAN_FILTER_BASE + CAN_FILTER_FFA1R) &= ~CAN_FILTER_BANK14_BIT; /* FIFO 0 */
    REG32(CAN_FILTER_BASE + CAN_FILTER_FR1(CAN_FILTER_BANK14)) = CAN_OUT_ID << 21;
    REG32(CAN_FILTER_BASE + CAN_FILTER_FR2(CAN_FILTER_BANK14)) =
        (0x7ffu << 21) | CAN_RX_RIR_IDE | CAN_RX_RIR_RTR;
    REG32(CAN_FILTER_BASE + CAN_FILTER_FA1R) |= CAN_FILTER_BANK14_BIT;
    REG32(CAN_FILTER_BASE + CAN_FILTER_FMR) = fmr & ~1u; /* leave filter init */
}

static bool bitrate_btr(uint32_t apb1_hz, uint32_t *btr_out)
{
    const uint32_t divisor = CAN_OUT_BITRATE * CAN_BIT_TQ_COUNT;
    if (apb1_hz == 0u || apb1_hz % divisor != 0u) return false;
    uint32_t prescaler = apb1_hz / divisor;
    if (prescaler == 0u || prescaler > 1024u) return false;

    *btr_out = ((CAN_BIT_SJW_TQ - 1u) << 24) |
               ((CAN_BIT_BS2_TQ - 1u) << 20) |
               ((CAN_BIT_BS1_TQ - 1u) << 16) |
               (prescaler - 1u);
    return true;
}

#if !defined(CAN_OUT_HOST_TEST)
static void install_can2_rx_vector(void)
{
    for (unsigned i = 0; i < SOURCE_VECTOR_WORDS; ++i) can_out_vectors[i] = vectors[i];
    for (unsigned i = SOURCE_VECTOR_WORDS; i < VECTOR_WORDS; ++i)
        can_out_vectors[i] = (uint32_t)(uintptr_t)firmware_fault;
    can_out_vectors[CAN2_RX0_VECTOR] = (uint32_t)(uintptr_t)CAN2_RX0_Handler;
    REG32(CAN_SCB_VTOR) = (uint32_t)(uintptr_t)can_out_vectors;
    CAN_VECTOR_BARRIER();
}
#endif

void can_out_init(uint32_t apb1_hz)
{
    uint32_t btr;
    if (!bitrate_btr(apb1_hz, &btr)) {
        increment(&can_out_stats.init_failures);
        return;
    }

    REG32(RCC_AHB1ENR) |= 1u << 1; /* GPIOB */
    REG32(RCC_APB1ENR) |= (1u << 25) | (1u << 26); /* CAN1 + CAN2 */
    (void)REG32(RCC_APB1ENR);
    gpio_b_alternate(8u);  /* CAN1_RX, AF9 */
    gpio_b_alternate(9u);  /* CAN1_TX, AF9 */
    gpio_b_alternate(12u); /* CAN2_RX, AF9 */
    gpio_b_alternate(13u); /* CAN2_TX, AF9 */

    REG32(CAN1_BASE + CAN_MCR) |= CAN_MCR_INRQ | CAN_MCR_ABOM | CAN_MCR_NART;
    REG32(CAN2_BASE + CAN_MCR) |= CAN_MCR_INRQ | CAN_MCR_ABOM | CAN_MCR_NART;
    if (!wait_for_init_state(CAN1_BASE, true) || !wait_for_init_state(CAN2_BASE, true)) {
        increment(&can_out_stats.init_failures);
        return;
    }

    configure_filter();
    REG32(CAN1_BASE + CAN_BTR) = btr;
    REG32(CAN2_BASE + CAN_BTR) = btr;
    can_out_stats.btr = btr;

    REG32(CAN2_BASE + CAN_IER) = CAN_IER_FMPIE0 | CAN_IER_FOVIE0;
    REG32(CAN1_BASE + CAN_MCR) &= ~CAN_MCR_INRQ;
    REG32(CAN2_BASE + CAN_MCR) &= ~CAN_MCR_INRQ;
    if (!wait_for_init_state(CAN1_BASE, false) || !wait_for_init_state(CAN2_BASE, false)) {
        increment(&can_out_stats.init_failures);
        return;
    }

    can1_was_bus_off = false;
    can2_was_bus_off = false;
    can1_was_warning = false;
    can2_was_warning = false;
    can1_was_passive = false;
    can2_was_passive = false;
    can_active = true;
    can_out_stats.active = 1u;

#if !defined(CAN_OUT_HOST_TEST)
    install_can2_rx_vector();
#endif
    ((volatile uint8_t *)(uintptr_t)CAN_NVIC_IPR)[CAN2_RX0_IRQ] = 6u << 4;
    ((volatile uint32_t *)(uintptr_t)CAN_NVIC_ISER)[CAN2_RX0_IRQ / 32u] =
        1u << (CAN2_RX0_IRQ % 32u);
    CAN_VECTOR_BARRIER();
}

static void sample_errors(uint32_t base, bool can1)
{
    uint32_t esr = REG32(base + CAN_ESR);
    bool bus_off = (esr & CAN_ESR_BOFF) != 0u;
    bool warning = (esr & CAN_ESR_EWGF) != 0u;
    bool passive = (esr & CAN_ESR_EPVF) != 0u;
    bool *was_bus_off = can1 ? &can1_was_bus_off : &can2_was_bus_off;
    bool *was_warning = can1 ? &can1_was_warning : &can2_was_warning;
    bool *was_passive = can1 ? &can1_was_passive : &can2_was_passive;

    if (bus_off && !*was_bus_off) increment(&can_out_stats.bus_off_events);
    if (warning && !*was_warning) increment(&can_out_stats.error_warning_events);
    if (passive && !*was_passive) increment(&can_out_stats.error_passive_events);
    *was_bus_off = bus_off;
    *was_warning = warning;
    *was_passive = passive;
    if (can1) {
        can_out_stats.can1_esr = esr;
        can_out_stats.can1_tec = (uint8_t)(esr >> CAN_ESR_TEC_SHIFT);
        can_out_stats.can1_rec = (uint8_t)(esr >> CAN_ESR_REC_SHIFT);
    } else {
        can_out_stats.can2_esr = esr;
        can_out_stats.can2_tec = (uint8_t)(esr >> CAN_ESR_TEC_SHIFT);
        can_out_stats.can2_rec = (uint8_t)(esr >> CAN_ESR_REC_SHIFT);
    }

    uint32_t lec = (esr & CAN_ESR_LEC_MASK) >> CAN_ESR_LEC_SHIFT;
    if (lec != 0u && lec != 7u) {
        increment(&can_out_stats.error_events);
        REG32(base + CAN_ESR) = 7u << CAN_ESR_LEC_SHIFT; /* clear LEC to no-change */
    }
}

static void collect_tx_results(void)
{
    uint32_t tsr = REG32(CAN1_BASE + CAN_TSR);
    for (unsigned mailbox = 0; mailbox < 3u; ++mailbox) {
        uint32_t rqcp = CAN_TSR_RQCP0 << mailbox;
        if ((tsr & rqcp) == 0u) continue;
        if ((tsr & (CAN_TSR_TXOK0 << mailbox)) != 0u)
            increment(&can_out_stats.tx_completed);
        else
            increment(&can_out_stats.tx_failed);
        REG32(CAN1_BASE + CAN_TSR) = rqcp; /* RQCP is write-one-to-clear */
    }
}

static bool transmit(const uint8_t data[CAN_OUT_FRAME_SIZE])
{
    uint32_t tsr = REG32(CAN1_BASE + CAN_TSR);
    unsigned mailbox;
    for (mailbox = 0; mailbox < 3u; ++mailbox) {
        if ((tsr & (CAN_TSR_TME0 << mailbox)) != 0u) break;
    }
    if (mailbox == 3u) {
        increment(&can_out_stats.tx_mailbox_full);
        return false;
    }

    uint32_t mailbox_base = CAN1_BASE + CAN_TX_MAILBOXES + mailbox * 0x10u;
    uint32_t low = (uint32_t)data[0] | ((uint32_t)data[1] << 8) |
                   ((uint32_t)data[2] << 16) | ((uint32_t)data[3] << 24);
    uint32_t high = (uint32_t)data[4] | ((uint32_t)data[5] << 8) |
                    ((uint32_t)data[6] << 16) | ((uint32_t)data[7] << 24);

    REG32(mailbox_base + CAN_TX_MAILBOX_TDTR) = CAN_OUT_FRAME_SIZE;
    REG32(mailbox_base + CAN_TX_MAILBOX_TDLR) = low;
    REG32(mailbox_base + CAN_TX_MAILBOX_TDHR) = high;
    REG32(mailbox_base + CAN_TX_MAILBOX_TIR) = (CAN_OUT_ID << 21) | CAN_TIR_TXRQ;
    increment(&can_out_stats.tx_queued);
    return true;
}

void can_out_update(uint32_t now_us, uint8_t state, uint8_t reason,
                    uint32_t last_fresh_frame_id)
{
    if (!can_active) return;

    collect_tx_results();
    sample_errors(CAN1_BASE, true);
    sample_errors(CAN2_BASE, false);

    bool changed = !have_last_state || state != last_state || reason != last_reason;
    bool periodic = have_last_state && (int32_t)(now_us - next_periodic_us) >= 0;
    if (!changed && !periodic) return;

    uint8_t data[CAN_OUT_FRAME_SIZE];
    uint16_t seq = tx_sequence++;
    can_out_pack(data, state, reason, seq, last_fresh_frame_id);
    if (changed) {
        increment(&can_out_stats.state_announcements);
        can_out_stats.last_state_change_us = now_us;
        bool found = false;
        for (unsigned n = 0; n < CAN_OUT_PENDING_DEPTH; ++n) {
            unsigned slot = (pending_write + n) % CAN_OUT_PENDING_DEPTH;
            if (pending_state_rx[slot].active) continue;
            pending_state_rx[slot].active = false;
            pending_state_rx[slot].state = state;
            pending_state_rx[slot].reason = reason;
            pending_state_rx[slot].seq = seq;
            pending_state_rx[slot].changed_us = now_us;
            pending_state_rx[slot].active = true;
            pending_write = (slot + 1u) % CAN_OUT_PENDING_DEPTH;
            latest_pending = slot;
            found = true;
            break;
        }
        if (!found) {
            increment(&can_out_stats.state_delivery_missed);
            latest_pending = CAN_OUT_PENDING_DEPTH;
        }
    } else if (periodic && latest_pending < CAN_OUT_PENDING_DEPTH &&
               pending_state_rx[latest_pending].active &&
               pending_state_rx[latest_pending].state == state &&
               pending_state_rx[latest_pending].reason == reason) {
        /* A periodic retry can deliver a dropped transition frame; keep its age. */
        pending_state_rx[latest_pending].seq = seq;
    }
    (void)transmit(data);

    if (!have_last_state) next_periodic_us = now_us + CAN_OUT_PERIOD_US;
    if (periodic) next_periodic_us = now_us + CAN_OUT_PERIOD_US;
    have_last_state = true;
    last_state = state;
    last_reason = reason;
}

void CAN2_RX0_Handler(void)
{
    uint32_t fifo = REG32(CAN2_BASE + CAN_RF0R);
    if ((fifo & CAN_RF0R_FOVR0) != 0u) {
        increment(&can_out_stats.rx_overruns);
        REG32(CAN2_BASE + CAN_RF0R) = CAN_RF0R_FOVR0;
    }

    /* FIFO0 has three hardware entries, so this drain is strictly bounded. */
    for (unsigned count = 0; count < 3u; ++count) {
        if ((REG32(CAN2_BASE + CAN_RF0R) & CAN_RF0R_FMP_MASK) == 0u) break;
        uint32_t rx_base = CAN2_BASE + CAN_RX_FIFO0;
        uint32_t rir = REG32(rx_base + CAN_RX_FIFO_RIR);
        uint32_t rdtr = REG32(rx_base + CAN_RX_FIFO_RDTR);
        uint32_t low = REG32(rx_base + CAN_RX_FIFO_RDLR);
        uint32_t high = REG32(rx_base + CAN_RX_FIFO_RDHR);
        REG32(CAN2_BASE + CAN_RF0R) = CAN_RF0R_RFOM0;

        uint32_t id = (rir >> 21) & 0x7ffu;
        uint8_t dlc = (uint8_t)(rdtr & 15u);
        if (id != CAN_OUT_ID || (rir & (CAN_RX_RIR_IDE | CAN_RX_RIR_RTR)) != 0u ||
            dlc != CAN_OUT_FRAME_SIZE) {
            increment(&can_out_stats.rx_invalid);
            continue;
        }

        can_out_stats.last_rx_id = id;
        can_out_stats.last_rx_us = REG32(TIM2_CNT);
        can_out_stats.last_rx_data[0] = (uint8_t)low;
        can_out_stats.last_rx_data[1] = (uint8_t)(low >> 8);
        can_out_stats.last_rx_data[2] = (uint8_t)(low >> 16);
        can_out_stats.last_rx_data[3] = (uint8_t)(low >> 24);
        can_out_stats.last_rx_data[4] = (uint8_t)high;
        can_out_stats.last_rx_data[5] = (uint8_t)(high >> 8);
        can_out_stats.last_rx_data[6] = (uint8_t)(high >> 16);
        can_out_stats.last_rx_data[7] = (uint8_t)(high >> 24);
        can_out_stats.last_rx_seq = (uint16_t)((uint16_t)can_out_stats.last_rx_data[2] |
                                    ((uint16_t)can_out_stats.last_rx_data[3] << 8));
        increment(&can_out_stats.rx_frames);
        for (unsigned i = 0; i < CAN_OUT_PENDING_DEPTH; ++i) {
            if (!pending_state_rx[i].active ||
                pending_state_rx[i].state != can_out_stats.last_rx_data[0] ||
                pending_state_rx[i].reason != can_out_stats.last_rx_data[1] ||
                pending_state_rx[i].seq != can_out_stats.last_rx_seq) continue;
            uint32_t latency = can_out_stats.last_rx_us - pending_state_rx[i].changed_us;
            unsigned bucket = latency >= 1000u ? 10u : (unsigned)(latency / 100u);
            increment(&can_out_stats.state_latency_bins[bucket]);
            increment(&can_out_stats.state_rx_count);
            can_out_stats.last_state_latency_us = latency;
            if (latency > can_out_stats.max_state_latency_us)
                can_out_stats.max_state_latency_us = latency;
            pending_state_rx[i].active = false;
            break;
        }
    }
}
