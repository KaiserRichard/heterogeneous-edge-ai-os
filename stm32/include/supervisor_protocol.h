#ifndef SUPERVISOR_PROTOCOL_H
#define SUPERVISOR_PROTOCOL_H

#include "hea_proto.h"
#include "supervisor.h"

/* Only pass frames emitted by hea_parser_feed (CRC checked there). The
 * adapter checks version, type, length and result field plausibility.
 * received_at_ticks is the real receipt boundary, now_ticks is evaluation time.
 * Invalid/unknown frames still trigger a timer evaluation. No Pi timestamp
 * is subtracted from MCU time. Version 1/2 age fields are not used by Step 1. */
supervisor_state_t supervisor_receive_frame(supervisor_t *sv,
                                             const struct hea_frame *frame,
                                             uint64_t received_at_ticks,
                                             uint64_t now_ticks);

#endif
