#include "supervisor_protocol.h"

#include <stddef.h>

supervisor_state_t supervisor_receive_frame(supervisor_t *sv,
                                             const struct hea_frame *frame,
                                             uint64_t received_at_ticks,
                                             uint64_t now_ticks)
{
    supervisor_event_t event = {SUPERVISOR_EVENT_NONE, false, 0u, 0u, received_at_ticks};
    if (frame != NULL && hea_version_supported(frame->version)) {
        event.wire_seq = frame->seq;
        switch (frame->type) {
        case HEA_MSG_HEARTBEAT: {
            struct hea_heartbeat heartbeat;
            if (hea_unpack_heartbeat(frame, &heartbeat) == 0) {
                event.kind = SUPERVISOR_EVENT_HEARTBEAT;
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
                event.valid = true;
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
