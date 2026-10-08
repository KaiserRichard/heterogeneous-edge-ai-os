# UART Protocol v2 (legacy v1 decoding)

Status: approved v2 age-at-send extension, software-tested (`make -C protocol test`). Not yet run on the STM32 or over a real UART.
This fills the framing/integrity TBD in `PROJECT.md` section 5.3; it can still change before firmware work starts.

## Frame

| Field | Size | Notes |
|---|---|---|
| SOF | 2 | `0xA5 0x5A`. Two bytes make false sync in payload data less likely than one. |
| version | 1 | Encoder emits `2`; decoder accepts `1` and `2`. Unknown versions are counted and dropped after CRC validation. |
| type | 1 | See below. |
| seq | 2 | Per-sender counter, little-endian. Gaps = lost frames. |
| len | 1 | Payload length, 0..64. Larger values are rejected before reading the payload. |
| payload | len | Little-endian fields. |
| crc | 2 | CRC-16/CCITT-FALSE over version..payload, little-endian. |

Overhead is unchanged at 9 bytes. Version 1 inference payload is 22 bytes (31-byte
frame); version 2 is 26 bytes (35-byte frame). V2 nominal serialization is about
3.04 ms at 115200 baud and 0.38 ms at 921600 baud (8N1, 10 bits per byte; CALCULATED).
These times exclude software queues and are not validated transit bounds.

Why this shape: a SOF + length + CRC frame with a byte-at-a-time state machine is
small enough to read in full, runs unchanged in an ISR, a FreeRTOS task or a Linux
`read()` loop, and its failure counters (`crc_errors`, `len_errors`, `bytes_dropped`)
are measurements in their own right. COBS framing would give cleaner resync but adds an
encoding step that hides less of the OS-level behaviour we want to observe.

## Messages

| Type | Direction | Payload | Purpose |
|---|---|---|---|
| `0x01` HEARTBEAT | Pi to STM32 | `linux_send_ns` u64 | Liveness for the supervisor watchdog. |
| `0x02` INFERENCE | Pi to STM32 | `linux_input_ns` u64, `linux_done_ns` u64, `input_seq` u32, `class_id` u8, `confidence_pct` u8, **v2 only:** `age_at_send_us` u32 | Result, Pi timestamps and Pi-local input-to-send duration. Step 1 supervisor uses receipt silence only. |
| `0x03` ECHO_REQ | Pi to STM32 | `linux_t1_ns` u64 | Round-trip time and clock-offset estimation. |
| `0x83` ECHO_RESP | STM32 to Pi | `linux_t1_ns` u64 (T1), `mcu_rx_us` u32 (T2), `mcu_tx_us` u32 (T3) | Linux adds T4 on receipt; offset and delay per RFC 4330 section 5 (see `docs/research/R8.md`). |
| `0x84` MCU_STATUS | STM32 to Pi | `mcu_us` u32, `state` u8, `missed_heartbeats` u16, `rx_crc_errors` u16 | Supervisor state (INIT / FRESH / HOLD / FAILSAFE), matching the supervisor state machine. |

Pi timestamp fields and the age-at-send calculation must use the same Pi monotonic
clock (the planned sender uses `CLOCK_MONOTONIC_RAW`). `mcu_*_us` fields belong to the
STM32 timer; `age_at_send_us` is a Pi duration. Never subtract a Pi timestamp from
an MCU timestamp without an explicit mapping.

## Version 2 age-at-send contract

KNOWN: Append `age_at_send_us` at payload offset 22, uint32 little-endian. It covers
`t_send - t_input` on one Pi clock, including inference and outbound queue residence,
and must be computed at the actual software-send boundary rather than inference
completion. The library does not sample clocks. Hardware transit accounting is
separate and remains UNKNOWN.

`hea_age_at_send_us(input_ns, send_ns, &age)` converts the same-clock difference,
rounds up to whole microseconds (less than 1 us quantization), and saturates at
`UINT32_MAX` instead of wrapping. It rejects backward clocks or NULL output, leaving
the output unchanged. The sender must drop/count such a failed calculation. The
maximum value denotes saturation or an exact maximum age; future source-age policy
must treat it conservatively, never as an exact finite upper bound for older data.

Version 1 requires exactly 22 INFERENCE payload bytes; version 2 requires exactly
26. There is no silent version/length fallback. Legacy decoding sets the member to
zero for initialization, but **the age is absent**, not a measured zero. Callers
must inspect `frame.version` for presence and label legacy observations receipt
silence. Other message payload layouts are unchanged and accepted in both versions.
Old v1-only decoders will reject v2; update both peers before physical-link tests.

Acceptance: v2 round-trip and endian field position; independent captured v1 golden
frame; both version/length mismatch directions; unknown version; zero/sub-us/exact
us conversion; regression; exact maximum, overflow and UINT64_MAX durations;
supervisor receipt-only behavior for both versions.

## Known limitation

After a CRC or length error the parser resumes SOF hunting at the next byte and does
not rescan the rejected bytes, so a valid frame that starts inside a corrupted one is
lost. One false candidate consumes at most a maximum-size frame (73 bytes); that can
overlap more than one shorter valid frame. CRC does not guarantee lossless resync.

## Reproducible noise test

KNOWN: Noise uses test-local xorshift32, seed 12345, with defined uint32 arithmetic.
The noise-only FNV-1a fingerprint is `8c9204cd`. All wire bytes are `uint8_t`.
The CRC known vector also uses an explicit uint8 array; no plain-char wire buffers
exist. Build both the protocol and supervisor tests with `-fsigned-char` and
`-funsigned-char`; CI exercises both modes.

MEASURED (software test on macOS and Ubuntu aarch64): the fixed noise stream recovers
20,000/20,000 frames, zero false accepts, zero CRC errors and one rejected oversize
noise header. These counts are asserted, not just a 95% recovery threshold.

The earlier `srand(12345)`/`rand()` stream was platform-dependent. Captured Pi losses:

| Real sequence | Noise immediately before frame (hex) | Parser behavior |
|---|---|---|
| 13355 | `bb fd a5 5a` | Noise SOF starts a false candidate; first five real-frame bytes `a5 5a 01 02 2b` become its header: len `0x2b` = 43; after the real frame, payload index is 26 |
| 13356 | `9c b4 b1 d4` | Continues false payload to index 30; consumes the start of this frame, fails CRC once, resumes SOF hunting |

Captured real frames, including their unchanged CRCs:

```
13355: a55a01022b3416887766554433221100ffeeddccbbaa99efbeadde075d70a8
13356: a55a01022c3416887766554433221100ffeeddccbbaa99efbeadde075d5d60
```

`test_false_sync_consumes_two_frames` reproduces these bytes without libc random
functions: both frames are lost, one false candidate fails CRC, and sequence 13357
decodes. This proves the previous two losses are resync behavior under a different
input stream, not a byte-signedness or platform-specific parser defect.
