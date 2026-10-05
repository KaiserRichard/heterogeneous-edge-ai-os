#include "supervisor.h"

supervisor_seq_order_t supervisor_seq_compare(uint32_t current_seq, uint32_t last_seq) {
    uint32_t delta = current_seq - last_seq;
    if (delta == 0U) {
        return SUPERVISOR_SEQ_DUPLICATE;
    }
    if (delta < 0x80000000U) {
        return SUPERVISOR_SEQ_NEWER;
    }
    if (delta == 0x80000000U) {
        return SUPERVISOR_SEQ_AMBIGUOUS;
    }
    return SUPERVISOR_SEQ_OLDER;
}

void supervisor_config_init_default(supervisor_config_t *config) {
    if (config == NULL) {
        return;
    }
    config->fresh_timeout_ticks = 100;     /* e.g., 100 ms or ticks */
    config->failsafe_timeout_ticks = 300;  /* e.g., 300 ms or ticks */
    config->max_consecutive_invalid = 0;   /* Minimal model: 0 disables fast-trip, relying purely on timeouts */
    config->recovery_valid_required = 1;   /* Minimal model: 1 fresh valid packet recovers */
}

void supervisor_init(supervisor_t *sv, const supervisor_config_t *config) {
    if (sv == NULL) {
        return;
    }

    if (config != NULL) {
        sv->config = *config;
    } else {
        supervisor_config_init_default(&sv->config);
    }

    if (sv->config.failsafe_timeout_ticks < sv->config.fresh_timeout_ticks) {
        sv->config.failsafe_timeout_ticks = sv->config.fresh_timeout_ticks;
    }
    if (sv->config.recovery_valid_required == 0) {
        sv->config.recovery_valid_required = 1;
    }

    sv->state = SUPERVISOR_STATE_INIT;
    sv->last_transition_reason = SUPERVISOR_REASON_NONE;
    sv->last_valid_time_ticks = 0;
    sv->last_sequence_id = 0;
    sv->has_received_first_valid = false;
    sv->consecutive_invalid_count = 0;
    sv->consecutive_valid_count = 0;
}

supervisor_state_t supervisor_update(supervisor_t *sv, const supervisor_input_t *input) {
    if (sv == NULL || input == NULL) {
        return SUPERVISOR_STATE_FAILSAFE;
    }

    uint64_t elapsed_ticks = 0;
    if (sv->has_received_first_valid && input->current_time_ticks >= sv->last_valid_time_ticks) {
        elapsed_ticks = input->current_time_ticks - sv->last_valid_time_ticks;
    }

    switch (sv->state) {
        case SUPERVISOR_STATE_INIT: {
            if (input->result_arrived) {
                if (input->is_valid) {
                    /* First valid result transitions INIT -> FRESH */
                    sv->has_received_first_valid = true;
                    sv->last_valid_time_ticks = input->current_time_ticks;
                    sv->last_sequence_id = input->sequence_id;
                    sv->consecutive_invalid_count = 0;
                    sv->consecutive_valid_count = 1;
                    sv->state = SUPERVISOR_STATE_FRESH;
                    sv->last_transition_reason = SUPERVISOR_REASON_FIRST_VALID_DATA;
                } else {
                    sv->consecutive_invalid_count++;
                    if (sv->config.max_consecutive_invalid > 0 &&
                        sv->consecutive_invalid_count >= sv->config.max_consecutive_invalid) {
                        sv->state = SUPERVISOR_STATE_FAILSAFE;
                        sv->last_transition_reason = SUPERVISOR_REASON_INVALID_DATA_BURST;
                    }
                }
            }
            break;
        }

        case SUPERVISOR_STATE_FRESH: {
            if (input->result_arrived) {
                if (input->is_valid) {
                    supervisor_seq_order_t order = supervisor_seq_compare(input->sequence_id, sv->last_sequence_id);
                    if (order == SUPERVISOR_SEQ_NEWER) {
                        /* Genuinely fresh subsequent result within deadline */
                        sv->last_sequence_id = input->sequence_id;
                        sv->last_valid_time_ticks = input->current_time_ticks;
                        sv->consecutive_invalid_count = 0;
                        sv->consecutive_valid_count++;
                        sv->last_transition_reason = SUPERVISOR_REASON_DATA_FRESH;
                    } else {
                        /* Non-advancing sequence (duplicate, older, or ambiguous): DO NOT refresh timestamp */
                        sv->last_transition_reason = (order == SUPERVISOR_SEQ_DUPLICATE) ?
                            SUPERVISOR_REASON_DUPLICATE_SEQUENCE : SUPERVISOR_REASON_STALE_SEQUENCE;

                        /* State is derived from elapsed local receiver time since last accepted valid result */
                        if (elapsed_ticks >= sv->config.failsafe_timeout_ticks) {
                            sv->state = SUPERVISOR_STATE_FAILSAFE;
                            sv->last_transition_reason = SUPERVISOR_REASON_FAILSAFE_TIMEOUT;
                        } else if (elapsed_ticks >= sv->config.fresh_timeout_ticks) {
                            sv->state = SUPERVISOR_STATE_HOLD;
                            sv->last_transition_reason = SUPERVISOR_REASON_FRESHNESS_DEADLINE_MISSED;
                        }
                    }
                } else {
                    /* Invalid result arrived */
                    sv->consecutive_invalid_count++;
                    sv->consecutive_valid_count = 0;
                    if (sv->config.max_consecutive_invalid > 0 &&
                        sv->consecutive_invalid_count >= sv->config.max_consecutive_invalid) {
                        sv->state = SUPERVISOR_STATE_FAILSAFE;
                        sv->last_transition_reason = SUPERVISOR_REASON_INVALID_DATA_BURST;
                    } else if (elapsed_ticks >= sv->config.failsafe_timeout_ticks) {
                        sv->state = SUPERVISOR_STATE_FAILSAFE;
                        sv->last_transition_reason = SUPERVISOR_REASON_FAILSAFE_TIMEOUT;
                    } else if (elapsed_ticks >= sv->config.fresh_timeout_ticks) {
                        sv->state = SUPERVISOR_STATE_HOLD;
                        sv->last_transition_reason = SUPERVISOR_REASON_FRESHNESS_DEADLINE_MISSED;
                    }
                }
            } else {
                /* No result arrived in this cycle: evaluate elapsed time */
                if (elapsed_ticks >= sv->config.failsafe_timeout_ticks) {
                    sv->state = SUPERVISOR_STATE_FAILSAFE;
                    sv->last_transition_reason = SUPERVISOR_REASON_FAILSAFE_TIMEOUT;
                } else if (elapsed_ticks >= sv->config.fresh_timeout_ticks) {
                    sv->state = SUPERVISOR_STATE_HOLD;
                    sv->last_transition_reason = SUPERVISOR_REASON_FRESHNESS_DEADLINE_MISSED;
                }
            }
            break;
        }

        case SUPERVISOR_STATE_HOLD: {
            if (input->result_arrived) {
                if (input->is_valid) {
                    supervisor_seq_order_t order = supervisor_seq_compare(input->sequence_id, sv->last_sequence_id);
                    if (order == SUPERVISOR_SEQ_NEWER) {
                        /* Recovery from transient delay back to FRESH */
                        sv->last_sequence_id = input->sequence_id;
                        sv->last_valid_time_ticks = input->current_time_ticks;
                        sv->consecutive_invalid_count = 0;
                        sv->consecutive_valid_count = 1;
                        sv->state = SUPERVISOR_STATE_FRESH;
                        sv->last_transition_reason = SUPERVISOR_REASON_DATA_FRESH;
                    } else {
                        /* Non-advancing sequence received while in HOLD */
                        sv->last_transition_reason = (order == SUPERVISOR_SEQ_DUPLICATE) ?
                            SUPERVISOR_REASON_DUPLICATE_SEQUENCE : SUPERVISOR_REASON_STALE_SEQUENCE;
                        if (elapsed_ticks >= sv->config.failsafe_timeout_ticks) {
                            sv->state = SUPERVISOR_STATE_FAILSAFE;
                            sv->last_transition_reason = SUPERVISOR_REASON_FAILSAFE_TIMEOUT;
                        }
                    }
                } else {
                    sv->consecutive_invalid_count++;
                    sv->consecutive_valid_count = 0;
                    if (sv->config.max_consecutive_invalid > 0 &&
                        sv->consecutive_invalid_count >= sv->config.max_consecutive_invalid) {
                        sv->state = SUPERVISOR_STATE_FAILSAFE;
                        sv->last_transition_reason = SUPERVISOR_REASON_INVALID_DATA_BURST;
                    } else if (elapsed_ticks >= sv->config.failsafe_timeout_ticks) {
                        sv->state = SUPERVISOR_STATE_FAILSAFE;
                        sv->last_transition_reason = SUPERVISOR_REASON_FAILSAFE_TIMEOUT;
                    }
                }
            } else {
                /* In HOLD and deadline exceeded -> transition to FAILSAFE */
                if (elapsed_ticks >= sv->config.failsafe_timeout_ticks) {
                    sv->state = SUPERVISOR_STATE_FAILSAFE;
                    sv->last_transition_reason = SUPERVISOR_REASON_FAILSAFE_TIMEOUT;
                }
            }
            break;
        }

        case SUPERVISOR_STATE_FAILSAFE: {
            if (input->result_arrived) {
                if (input->is_valid) {
                    supervisor_seq_order_t order = supervisor_seq_compare(input->sequence_id, sv->last_sequence_id);
                    if (order == SUPERVISOR_SEQ_NEWER) {
                        sv->consecutive_valid_count++;
                        sv->last_sequence_id = input->sequence_id;
                        sv->last_valid_time_ticks = input->current_time_ticks;
                        sv->consecutive_invalid_count = 0;

                        if (sv->consecutive_valid_count >= sv->config.recovery_valid_required) {
                            sv->state = SUPERVISOR_STATE_FRESH;
                            sv->last_transition_reason = SUPERVISOR_REASON_RECOVERED;
                        }
                    } else {
                        sv->consecutive_valid_count = 0;
                        sv->last_transition_reason = (order == SUPERVISOR_SEQ_DUPLICATE) ?
                            SUPERVISOR_REASON_DUPLICATE_SEQUENCE : SUPERVISOR_REASON_STALE_SEQUENCE;
                    }
                } else {
                    sv->consecutive_valid_count = 0;
                    sv->consecutive_invalid_count++;
                }
            }
            break;
        }

        default:
            sv->state = SUPERVISOR_STATE_FAILSAFE;
            break;
    }

    return sv->state;
}

const char *supervisor_state_to_str(supervisor_state_t state) {
    switch (state) {
        case SUPERVISOR_STATE_INIT:     return "INIT";
        case SUPERVISOR_STATE_FRESH:    return "FRESH";
        case SUPERVISOR_STATE_HOLD:     return "HOLD";
        case SUPERVISOR_STATE_FAILSAFE: return "FAILSAFE";
        default:                        return "UNKNOWN";
    }
}

const char *supervisor_reason_to_str(supervisor_reason_t reason) {
    switch (reason) {
        case SUPERVISOR_REASON_NONE:                      return "NONE";
        case SUPERVISOR_REASON_FIRST_VALID_DATA:          return "FIRST_VALID_DATA";
        case SUPERVISOR_REASON_DATA_FRESH:                return "DATA_FRESH";
        case SUPERVISOR_REASON_FRESHNESS_DEADLINE_MISSED: return "FRESHNESS_DEADLINE_MISSED";
        case SUPERVISOR_REASON_FAILSAFE_TIMEOUT:          return "FAILSAFE_TIMEOUT";
        case SUPERVISOR_REASON_DUPLICATE_SEQUENCE:        return "DUPLICATE_SEQUENCE";
        case SUPERVISOR_REASON_STALE_SEQUENCE:            return "STALE_SEQUENCE";
        case SUPERVISOR_REASON_INVALID_DATA_BURST:        return "INVALID_DATA_BURST";
        case SUPERVISOR_REASON_RECOVERED:                 return "RECOVERED";
        default:                                          return "UNKNOWN";
    }
}
