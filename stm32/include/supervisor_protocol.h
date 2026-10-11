#ifndef SUPERVISOR_PROTOCOL_H
#define SUPERVISOR_PROTOCOL_H

#include "hea_proto.h"
#include "supervisor.h"

/* Only pass frames emitted by hea_parser_feed (CRC checked there). The
 * adapter checks version, type, length and result field plausibility.
 * generation and received_at_ticks must be captured at the real receipt boundary,
 * not read/restamped at queue dispatch; now_ticks is evaluation time.
 * Invalid/unknown frames still trigger a timer evaluation. No Pi timestamp
 * is subtracted from MCU time. Version 1 uses flagged receipt-silence fallback; v2/v3 use source age. */
supervisor_state_t supervisor_receive_frame(supervisor_t *sv,
                                             const struct hea_frame *frame,
                                             uint64_t generation,
                                             uint64_t received_at_ticks,
                                             uint64_t now_ticks);

#endif
