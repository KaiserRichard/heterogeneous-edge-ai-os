#include "supervisor.h"

#include <stddef.h>
#include <string.h>

static uint64_t saturating_add(uint64_t a, uint64_t b)
{
    return UINT64_MAX - a < b ? UINT64_MAX : a + b;
}

bool supervisor_extend_mcu_us(uint64_t previous, uint32_t raw, uint64_t *out)
{
    uint32_t delta = raw - (uint32_t)previous;
    if (out == NULL || delta >= UINT32_C(0x80000000) ||
        UINT64_MAX - previous < delta) return false;
    *out = previous + delta;
    return true;
}

static uint64_t result_age(const supervisor_t *sv, uint64_t now)
{
    uint64_t elapsed = now - sv->last_result_ticks;
    if (sv->receipt_silence_fallback) return elapsed;
    return saturating_add(saturating_add(elapsed, sv->last_age_at_send_us),
                          sv->config.transit_bound_us);
}

supervisor_seq_order_t supervisor_seq_compare16(uint16_t current, uint16_t last)
{
    uint16_t delta = (uint16_t)(current - last);
    if (delta == 0u) return SUPERVISOR_SEQ_DUPLICATE;
    if (delta < UINT16_C(0x8000)) return SUPERVISOR_SEQ_NEWER;
    if (delta == UINT16_C(0x8000)) return SUPERVISOR_SEQ_AMBIGUOUS;
    return SUPERVISOR_SEQ_OLDER;
}

supervisor_seq_order_t supervisor_seq_compare(uint32_t current, uint32_t last)
{
    uint32_t delta = current - last;
    if (delta == 0u) return SUPERVISOR_SEQ_DUPLICATE;
    if (delta < UINT32_C(0x80000000)) return SUPERVISOR_SEQ_NEWER;
    if (delta == UINT32_C(0x80000000)) return SUPERVISOR_SEQ_AMBIGUOUS;
    return SUPERVISOR_SEQ_OLDER;
}

static void transition(supervisor_t *sv, supervisor_state_t state,
                       supervisor_reason_t reason)
{
    if (sv->state != state) {
        sv->state = state;
        sv->last_transition_reason = reason;
    }
}

bool supervisor_init(supervisor_t *sv, const supervisor_config_t *config,
                     uint64_t now_ticks)
{
    if (sv == NULL) return false;
    memset(sv, 0, sizeof(*sv));
    sv->state = SUPERVISOR_STATE_FAILSAFE;
    sv->last_transition_reason = SUPERVISOR_REASON_INVALID_CONFIG;
    sv->last_time_ticks = now_ticks;
    sv->epoch_start_ticks = now_ticks;
    if (config == NULL || config->heartbeat_timeout_ticks == 0u ||
        config->result_hold_ticks == 0u ||
        config->result_failsafe_ticks <= config->result_hold_ticks ||
        config->rearm_healthy_ticks == 0u) return false;
    sv->config = *config;
    sv->configured = true;
    sv->state = SUPERVISOR_STATE_INIT;
    sv->last_transition_reason = SUPERVISOR_REASON_NONE;
    return true;
}

static bool healthy(const supervisor_t *sv, uint64_t now)
{
    return sv->has_heartbeat && sv->has_result &&
        now - sv->last_heartbeat_ticks < sv->config.heartbeat_timeout_ticks &&
        result_age(sv, now) < sv->config.result_hold_ticks;
}

static void evaluate(supervisor_t *sv, uint64_t now)
{
    bool hb_ok = sv->has_heartbeat &&
        now - sv->last_heartbeat_ticks < sv->config.heartbeat_timeout_ticks;
    if (!healthy(sv, now)) sv->healthy_interval = false;
    /* INIT source-age expiry must latch before replacement traffic is accepted. */
    if (sv->state == SUPERVISOR_STATE_INIT && sv->has_result &&
        !sv->receipt_silence_fallback &&
        result_age(sv, now) >= sv->config.result_failsafe_ticks)
        transition(sv, SUPERVISOR_STATE_FAILSAFE, SUPERVISOR_REASON_SOURCE_AGE_TIMEOUT);
    if (sv->state == SUPERVISOR_STATE_FRESH ||
        sv->state == SUPERVISOR_STATE_HOLD) {
        if (!hb_ok) {
            transition(sv, SUPERVISOR_STATE_FAILSAFE,
                       SUPERVISOR_REASON_HEARTBEAT_TIMEOUT);
        } else if (result_age(sv, now) >= sv->config.result_failsafe_ticks) {
            transition(sv, SUPERVISOR_STATE_FAILSAFE,
                       sv->receipt_silence_fallback ? SUPERVISOR_REASON_RESULT_TIMEOUT :
                       SUPERVISOR_REASON_SOURCE_AGE_TIMEOUT);
        } else if (result_age(sv, now) >= sv->config.result_hold_ticks) {
            transition(sv, SUPERVISOR_STATE_HOLD,
                       sv->receipt_silence_fallback ? SUPERVISOR_REASON_RESULT_SILENCE :
                       SUPERVISOR_REASON_SOURCE_AGE_HOLD);
        }
    }
}

static void accept(supervisor_t *sv, const supervisor_event_t *event, uint64_t now)
{
    if (event != NULL && event->generation != sv->generation) {
        if (sv->rejected_generation_events != UINT64_MAX)
            ++sv->rejected_generation_events;
        return;
    }
    if (event == NULL || !event->valid ||
        event->kind < SUPERVISOR_EVENT_HEARTBEAT ||
        event->kind > SUPERVISOR_EVENT_OTHER ||
        event->received_at_ticks > now ||
        event->received_at_ticks < sv->epoch_start_ticks) return;
    if (event->kind == SUPERVISOR_EVENT_RESULT && event->has_age_at_send &&
        event->age_at_send_us > UINT32_MAX) return;
    if ((event->kind == SUPERVISOR_EVENT_HEARTBEAT && sv->has_heartbeat &&
         event->received_at_ticks < sv->last_heartbeat_ticks) ||
        (event->kind == SUPERVISOR_EVENT_RESULT && sv->has_result &&
         event->received_at_ticks < sv->last_result_ticks)) return;
    if (event->kind == SUPERVISOR_EVENT_HEARTBEAT) {
        /* Once a session is known, a legacy heartbeat cannot downgrade it. */
        if (sv->has_session_id && !event->has_session_id) return;
        if (event->has_session_id && (!sv->has_session_id ||
            event->session_id != sv->session_id)) {
            if (sv->generation == UINT64_MAX) return;
            ++sv->generation;
            sv->has_session_id = true;
            sv->session_id = event->session_id;
            sv->has_wire_seq = false;
            sv->has_input_seq = false;
            sv->has_heartbeat = false;
            sv->has_result = false;
            sv->source_age_estimate_us = 0u;
            sv->receipt_silence_fallback = false;
            sv->healthy_interval = false;
            sv->epoch_start_ticks = event->received_at_ticks;
            if (sv->state != SUPERVISOR_STATE_FAILSAFE)
                transition(sv, SUPERVISOR_STATE_INIT, SUPERVISOR_REASON_SESSION_CHANGE);
        }
    }
    if (sv->has_wire_seq && supervisor_seq_compare16(event->wire_seq,
        sv->last_wire_seq) != SUPERVISOR_SEQ_NEWER) return;

    /* A valid new wire frame advances the sender watermark even if its
     * RESULT repeats an old input. It never refreshes either health timer. */
    sv->has_wire_seq = true;
    sv->last_wire_seq = event->wire_seq;
    if (event->kind == SUPERVISOR_EVENT_HEARTBEAT) {
        sv->has_heartbeat = true;
        sv->last_heartbeat_ticks = event->received_at_ticks;
    } else if (event->kind == SUPERVISOR_EVENT_RESULT) {
        if (sv->has_input_seq && supervisor_seq_compare(event->input_seq,
            sv->last_input_seq) != SUPERVISOR_SEQ_NEWER) return;
        sv->has_input_seq = true;
        sv->last_input_seq = event->input_seq;
        sv->has_result = true;
        sv->last_result_ticks = event->received_at_ticks;
        sv->last_age_at_send_us = (uint32_t)event->age_at_send_us;
        sv->receipt_silence_fallback = !event->has_age_at_send;
    }
}

supervisor_state_t supervisor_update(supervisor_t *sv,
                                     const supervisor_event_t *event,
                                     uint64_t now_ticks)
{
    if (sv == NULL) return SUPERVISOR_STATE_FAILSAFE;
    if (!sv->configured) return sv->state;
    if (now_ticks < sv->last_time_ticks) {
        sv->state = SUPERVISOR_STATE_FAILSAFE;
        sv->last_transition_reason = SUPERVISOR_REASON_CLOCK_REGRESSION;
        sv->healthy_interval = false;
        return sv->state;
    }
    sv->last_time_ticks = now_ticks;
    evaluate(sv, now_ticks);
    accept(sv, event, now_ticks);
    if (sv->has_result) sv->source_age_estimate_us = result_age(sv, now_ticks);
    evaluate(sv, now_ticks);
    if (healthy(sv, now_ticks)) {
        if (!sv->healthy_interval) {
            sv->healthy_since_ticks = now_ticks;
            sv->healthy_interval = true;
        }
        if (sv->state == SUPERVISOR_STATE_INIT ||
            sv->state == SUPERVISOR_STATE_HOLD) {
            transition(sv, SUPERVISOR_STATE_FRESH, SUPERVISOR_REASON_READY);
        }
    }
    return sv->state;
}

bool supervisor_rearm(supervisor_t *sv, uint64_t now_ticks)
{
    if (sv == NULL || !sv->configured || now_ticks < sv->last_time_ticks) {
        (void)supervisor_update(sv, NULL, now_ticks);
        return false;
    }
    (void)supervisor_update(sv, NULL, now_ticks);
    if (sv->generation == UINT64_MAX ||
        sv->state != SUPERVISOR_STATE_FAILSAFE || !sv->healthy_interval ||
        now_ticks - sv->healthy_since_ticks < sv->config.rearm_healthy_ticks) {
        return false;
    }
    transition(sv, SUPERVISOR_STATE_INIT, SUPERVISOR_REASON_REARM);
    ++sv->generation;
    sv->epoch_start_ticks = now_ticks;
    sv->has_heartbeat = false;
    sv->has_result = false;
    sv->source_age_estimate_us = 0u;
    sv->receipt_silence_fallback = false;
    sv->healthy_interval = false;
    return true;
}

const char *supervisor_state_to_str(supervisor_state_t state)
{
    switch (state) {
    case SUPERVISOR_STATE_INIT: return "INIT";
    case SUPERVISOR_STATE_FRESH: return "FRESH";
    case SUPERVISOR_STATE_HOLD: return "HOLD";
    case SUPERVISOR_STATE_FAILSAFE: return "FAILSAFE";
    }
    return "UNKNOWN";
}
