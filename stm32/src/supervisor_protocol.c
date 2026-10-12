#include "supervisor_protocol.h"

#include <stddef.h>

supervisor_state_t supervisor_receive_frame(supervisor_t *sv,
                                             const struct hea_frame *frame,
                                             uint64_t generation,
                                             uint64_t received_at_ticks,
                                             uint64_t now_ticks)
{
    supervisor_event_t event = {0};
    event.received_at_ticks = received_at_ticks;
    event.generation = generation;
    if (frame != NULL && hea_version_supported(frame->version)) {
        event.wire_seq = frame->seq;
        switch (frame->type) {
        case HEA_MSG_HEARTBEAT: {
            struct hea_heartbeat heartbeat;
            if (hea_unpack_heartbeat(frame, &heartbeat) == 0) {
                event.kind = SUPERVISOR_EVENT_HEARTBEAT;
                event.session_id = heartbeat.session_id;
                event.has_session_id = frame->version == HEA_PROTO_VERSION;
                event.valid = true;
            }
            break;
        }
        case HEA_MSG_INFERENCE: {
            struct hea_inference result;
            if (hea_unpack_inference(frame, &result) == 0 &&
                result.confidence_pct <= 100u &&
                result.linux_done_ns >= result.linux_input_ns) {
                event.kind = SUPERVISOR_EVENT_RESULT;
                event.input_seq = result.input_seq;
                event.has_age_at_send = frame->version != HEA_PROTO_VERSION_LEGACY;
                event.age_at_send_us = result.age_at_send_us;
                /* Pi-only plausibility: done cannot follow the declared send age.
                 * UINT32_MAX is the sender's saturation value, accepted as stale. */
                uint64_t processing_us = (result.linux_done_ns - result.linux_input_ns) / 1000u;
                uint64_t remainder = (result.linux_done_ns - result.linux_input_ns) % 1000u;
                if (remainder != 0u) ++processing_us;
                event.valid = !event.has_age_at_send || result.age_at_send_us == UINT32_MAX ||
                    processing_us <= result.age_at_send_us;
            }
            break;
        }
        case HEA_MSG_ECHO_REQ: {
            struct hea_echo_req echo;
            if (hea_unpack_echo_req(frame, &echo) == 0) {
                event.kind = SUPERVISOR_EVENT_OTHER;
                event.valid = true;
            }
            break;
        }
        default: break;
        }
    }
    return supervisor_update(sv, &event, now_ticks);
}
