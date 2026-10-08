#ifndef SUPERVISOR_H
#define SUPERVISOR_H

#include <stdbool.h>
#include <stdint.h>

/* Step 1: MCU-local receipt silence, not source Age of Information. */
typedef enum {
    SUPERVISOR_STATE_INIT = 0,
    SUPERVISOR_STATE_FRESH,
    SUPERVISOR_STATE_HOLD,
    SUPERVISOR_STATE_FAILSAFE
} supervisor_state_t;

typedef enum {
    SUPERVISOR_REASON_NONE = 0,
    SUPERVISOR_REASON_READY,
    SUPERVISOR_REASON_RESULT_SILENCE,
    SUPERVISOR_REASON_HEARTBEAT_TIMEOUT,
    SUPERVISOR_REASON_RESULT_TIMEOUT,
    SUPERVISOR_REASON_REARM,
    SUPERVISOR_REASON_CLOCK_REGRESSION,
    SUPERVISOR_REASON_INVALID_CONFIG
} supervisor_reason_t;

typedef enum {
    SUPERVISOR_SEQ_DUPLICATE = 0,
    SUPERVISOR_SEQ_NEWER,
    SUPERVISOR_SEQ_OLDER,
    SUPERVISOR_SEQ_AMBIGUOUS
} supervisor_seq_order_t;

typedef enum {
    SUPERVISOR_EVENT_NONE = 0,
    SUPERVISOR_EVENT_HEARTBEAT,
    SUPERVISOR_EVENT_RESULT,
    SUPERVISOR_EVENT_OTHER /* Valid Pi ECHO_REQ; advances wire sequence only. */
} supervisor_event_kind_t;

typedef struct {
    uint64_t heartbeat_timeout_ticks;
    uint64_t result_hold_ticks;
    uint64_t result_failsafe_ticks;
    uint64_t rearm_healthy_ticks;
} supervisor_config_t;

typedef struct {
    supervisor_event_kind_t kind;
    bool valid;
    uint16_t wire_seq; /* One shared per-Pi counter, across message types. */
    uint32_t input_seq; /* Used only for RESULT; independent input counter. */
    uint64_t received_at_ticks; /* Actual MCU receipt boundary, not queue dispatch. */
} supervisor_event_t;

typedef struct {
    supervisor_state_t state;
    supervisor_reason_t last_transition_reason;
    supervisor_config_t config;
    uint64_t last_time_ticks;
    uint64_t epoch_start_ticks;
    uint64_t last_heartbeat_ticks;
    uint64_t last_result_ticks;
    uint64_t healthy_since_ticks;
    uint16_t last_wire_seq;
    uint32_t last_input_seq;
    bool configured;
    bool has_wire_seq;
    bool has_input_seq;
    bool has_heartbeat;
    bool has_result;
    bool healthy_interval;
} supervisor_t;

supervisor_seq_order_t supervisor_seq_compare16(uint16_t current, uint16_t last);
supervisor_seq_order_t supervisor_seq_compare(uint32_t current, uint32_t last);

/* No default thresholds. Invalid config leaves an unrearmable FAILSAFE. */
bool supervisor_init(supervisor_t *sv, const supervisor_config_t *config,
                     uint64_t now_ticks);

/* Single-owner API. Call even without traffic. Expiry precedes event handling.
 * Times must be nondecreasing, extended MCU-local ticks in one unit; no wrap.
 * NONE/NULL means a timer evaluation. Invalid events never renew timers.
 * An event must carry receipt time <= now and within this init/rearm epoch. */
supervisor_state_t supervisor_update(supervisor_t *sv,
                                     const supervisor_event_t *event,
                                     uint64_t now_ticks);

/* Local explicit request, not a wire command. Only succeeds from FAILSAFE
 * after uninterrupted healthy observation; clears receipt/health history,
 * preserves sequence high-water marks, and returns to safe INIT.
 * Owner must atomically invalidate queued pre-rearm events: receipt ticks
 * equal to the new epoch cannot distinguish events within the same tick. */
bool supervisor_rearm(supervisor_t *sv, uint64_t now_ticks);

/* Only FRESH permits new simulated output; HOLD policy is a port decision.
 * INIT and FAILSAFE must select the local safe output. */
const char *supervisor_state_to_str(supervisor_state_t state);

#endif
