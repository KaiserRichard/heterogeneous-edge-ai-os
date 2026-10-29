#ifndef HEA_CAN_OUT_H
#define HEA_CAN_OUT_H

#include <stdint.h>

#define CAN_OUT_ID 0x120u
#define CAN_OUT_FRAME_SIZE 8u
#define CAN_OUT_BITRATE 500000u
#define CAN_OUT_PERIOD_US 100000u

/* Live counters are debugger-visible even when no serial console is enabled. */
typedef struct {
    uint32_t init_failures;
    uint32_t tx_queued;
    uint32_t tx_completed;
    uint32_t tx_failed;
    uint32_t tx_mailbox_full;
    uint32_t rx_frames;
    uint32_t rx_invalid;
    uint32_t rx_overruns;
    uint32_t error_events;
    uint32_t bus_off_events;
    uint32_t error_warning_events;
    uint32_t error_passive_events;
    uint32_t state_announcements;
    uint32_t state_rx_count;
    uint32_t state_delivery_missed;
    uint32_t last_state_change_us;
    uint32_t last_state_latency_us;
    uint32_t max_state_latency_us;
    uint32_t state_latency_bins[11]; /* 0-99 ... 900-999 us, then >=1000 us */
    uint32_t last_rx_us;
    uint32_t last_rx_id;
    uint32_t can1_esr;
    uint32_t can2_esr;
    uint32_t btr;
    uint16_t last_rx_seq;
    uint8_t can1_tec;
    uint8_t can1_rec;
    uint8_t can2_tec;
    uint8_t can2_rec;
    uint8_t last_rx_data[CAN_OUT_FRAME_SIZE];
    uint8_t active;
} can_out_stats_t;

extern volatile can_out_stats_t can_out_stats;

/* Payload byte layout: state, reason, seq LE16, frame_id LE32. */
void can_out_pack(uint8_t out[CAN_OUT_FRAME_SIZE], uint8_t state,
                  uint8_t reason, uint16_t seq, uint32_t frame_id);

/* Configure bxCAN1/2 for 500 kbit/s and CAN2 filter bank 14. */
void can_out_init(uint32_t apb1_hz);

/* Bounded, nonblocking supervisor-side service; now_us is TIM2's 1 MHz count. */
void can_out_update(uint32_t now_us, uint8_t state, uint8_t reason,
                    uint32_t last_fresh_frame_id);

/* Installed in the optional RAM vector table for bxCAN2 FIFO0. */
void CAN2_RX0_Handler(void);

#endif
