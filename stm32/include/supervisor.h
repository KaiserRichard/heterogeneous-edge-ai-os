#ifndef SUPERVISOR_H
#define SUPERVISOR_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Supervisor state definitions.
 *
 * Models real-time deadline monitoring and safety failsafe logic
 * independently of hardware drivers and RTOS primitives.
 */
typedef enum {
    SUPERVISOR_STATE_INIT = 0,     /* Startup: awaiting first valid perception packet */
    SUPERVISOR_STATE_FRESH,        /* Operating normally: packets arriving within freshness deadline */
    SUPERVISOR_STATE_HOLD,         /* Transient omission: hold last known state within hold tolerance */
    SUPERVISOR_STATE_FAILSAFE      /* Safety threshold exceeded: deadline missed or corrupted stream */
} supervisor_state_t;

/**
 * State transition and diagnostic event reasons.
 */
typedef enum {
    SUPERVISOR_REASON_NONE = 0,
    SUPERVISOR_REASON_FIRST_VALID_DATA,
    SUPERVISOR_REASON_DATA_FRESH,
    SUPERVISOR_REASON_FRESHNESS_DEADLINE_MISSED,
    SUPERVISOR_REASON_FAILSAFE_TIMEOUT,
    SUPERVISOR_REASON_DUPLICATE_SEQUENCE,
    SUPERVISOR_REASON_STALE_SEQUENCE,
    SUPERVISOR_REASON_INVALID_DATA_BURST,
    SUPERVISOR_REASON_RECOVERED
} supervisor_reason_t;

/**
 * Sequence number comparison categories using unsigned modular half-range semantics.
 *
 * Given delta = (current_seq - last_seq) in 32-bit unsigned modular arithmetic:
 * - delta == 0: Duplicate
 * - 0 < delta < 2^31: Strictly newer
 * - delta > 2^31: Older / stale
 * - delta == 2^31: Ambiguous / half-range boundary (not safely orderable)
 */
typedef enum {
    SUPERVISOR_SEQ_DUPLICATE = 0,
    SUPERVISOR_SEQ_NEWER,
    SUPERVISOR_SEQ_OLDER,
    SUPERVISOR_SEQ_AMBIGUOUS
} supervisor_seq_order_t;

/**
 * Configuration parameters for the supervisor state machine.
 * All thresholds are expressed in the local receiver's time tick domain.
 *
 * Architectural Note on Policies:
 * - Primary Architectural Model: Minimal time-based freshness/timeout model.
 *   State is derived from elapsed local receiver time since the last accepted
 *   new valid result.
 * - Provisional Policy (Fault Burst): max_consecutive_invalid enables an optional
 *   fast-path trip to FAILSAFE upon receiving repeated corrupt/invalid packets.
 *   Set to 0 to disable and rely purely on the timeout model.
 * - Provisional Policy (Recovery Hysteresis): recovery_valid_required specifies
 *   how many consecutive fresh valid packets are required before leaving FAILSAFE.
 *   Default is 1 (minimal recovery).
 */
typedef struct {
    uint64_t fresh_timeout_ticks;     /* Max ticks since last valid packet before transitioning to HOLD */
    uint64_t failsafe_timeout_ticks;  /* Max ticks since last valid packet before triggering FAILSAFE */
    uint32_t max_consecutive_invalid; /* Provisional: max consecutive invalid packets before FAILSAFE (0 = disabled) */
    uint32_t recovery_valid_required; /* Provisional: consecutive valid packets to recover (default: 1) */
} supervisor_config_t;

/**
 * Input event for a single evaluation step of the supervisor state machine.
 */
typedef struct {
    bool result_arrived;           /* True if a packet arrived in this cycle */
    uint32_t sequence_id;          /* Sequence ID from packet header (if result_arrived is true) */
    bool is_valid;                 /* True if packet passed validation/checksum checks */
    uint64_t current_time_ticks;   /* Monotonic timestamp in the receiver's local time domain */
} supervisor_input_t;

/**
 * State machine instance data.
 */
typedef struct {
    supervisor_state_t state;
    supervisor_reason_t last_transition_reason;
    supervisor_config_t config;

    /* Internal tracking in receiver's local time domain */
    uint64_t last_valid_time_ticks;
    uint32_t last_sequence_id;
    bool has_received_first_valid;

    uint32_t consecutive_invalid_count;
    uint32_t consecutive_valid_count;
} supervisor_t;

/**
 * @brief Compare two uint32_t sequence IDs using unsigned modular half-range semantics.
 *
 * Avoids implementation-defined unsigned-to-signed integer conversions.
 *
 * @param current_seq Candidate sequence ID from received packet.
 * @param last_seq Sequence ID of the last accepted valid packet.
 * @return Ordering category (DUPLICATE, NEWER, OLDER, or AMBIGUOUS).
 */
supervisor_seq_order_t supervisor_seq_compare(uint32_t current_seq, uint32_t last_seq);

/**
 * @brief Initialize default configuration for the supervisor.
 *
 * Defaults to the minimal freshness/timeout model (max_consecutive_invalid = 0).
 *
 * @param config Pointer to configuration struct.
 */
void supervisor_config_init_default(supervisor_config_t *config);

/**
 * @brief Initialize supervisor instance with given configuration.
 *
 * @param sv Pointer to supervisor struct.
 * @param config Pointer to configuration parameters (if NULL, defaults are used).
 */
void supervisor_init(supervisor_t *sv, const supervisor_config_t *config);

/**
 * @brief Update supervisor state machine for a single cycle.
 *
 * Evaluates state transitions deterministically using the supervisor's
 * local time domain. Never accesses external system clocks or hardware registers.
 *
 * @param sv Pointer to supervisor instance.
 * @param input Pointer to cycle input data.
 * @return Current supervisor state after evaluation.
 */
supervisor_state_t supervisor_update(supervisor_t *sv, const supervisor_input_t *input);

/**
 * @brief Convert supervisor state enum to human-readable string.
 */
const char *supervisor_state_to_str(supervisor_state_t state);

/**
 * @brief Convert supervisor transition reason enum to human-readable string.
 */
const char *supervisor_reason_to_str(supervisor_reason_t reason);

#ifdef __cplusplus
}
#endif

#endif /* SUPERVISOR_H */
