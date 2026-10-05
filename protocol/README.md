# Shared Protocol Core

## Purpose
Defines the transport-independent semantic message model and serialization for Linux-to-STM32 telemetry.

## Components
- `include/protocol.h`: Semantic data model (`protocol_msg_t`), message types, flags, and payload constants.
- `src/protocol.c`: Platform-independent encode/decode logic using canonical big-endian byte serialization.

## Canonical Payload Layout (12 bytes)
```
[0]    : uint8_t  version (PROTOCOL_VERSION_CURRENT = 1)
[1]    : uint8_t  msg_type (0x01: Heartbeat, 0x02: Perception)
[2]    : uint8_t  flags (bit 0: valid, bit 1: degraded)
[3]    : uint8_t  confidence (0-100)
[4-7]  : uint32_t sequence_id (big-endian)
[8-11] : int32_t  result_value (big-endian)
```

## Architectural Status
- **Wire Framing**: Deliberately OPEN (TBD: COBS vs delimiter bytes).
- **Integrity**: Deliberately OPEN (TBD: CRC-16 vs CRC-32 vs Fletcher-16).
