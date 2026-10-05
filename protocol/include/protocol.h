#ifndef PROTOCOL_H
#define PROTOCOL_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Protocol version definition.
 */
#define PROTOCOL_VERSION_CURRENT 1U

/**
 * Message types supported by the protocol core.
 */
typedef enum {
    PROTOCOL_MSG_HEARTBEAT  = 0x01,
    PROTOCOL_MSG_PERCEPTION = 0x02
} protocol_msg_type_t;

/**
 * Sender-side status and validity flags.
 */
#define PROTOCOL_FLAG_VALID     (1U << 0)
#define PROTOCOL_FLAG_DEGRADED  (1U << 1)

/**
 * Return codes for protocol operations.
 */
typedef enum {
    PROTOCOL_OK                      = 0,
    PROTOCOL_ERR_NULL_PTR            = -1,
    PROTOCOL_ERR_BUFFER_TOO_SMALL    = -2,
    PROTOCOL_ERR_UNSUPPORTED_VERSION = -3,
    PROTOCOL_ERR_INVALID_MSG_TYPE    = -4,
    PROTOCOL_ERR_MALFORMED           = -5
} protocol_error_t;

/**
 * @brief Semantic representation of a message exchanged between Linux and STM32.
 *
 * This struct represents the domain payload independent of physical UART framing.
 */
typedef struct {
    uint8_t version;         /* Protocol version identifier */
    uint8_t msg_type;        /* Message type (heartbeat, perception, etc.) */
    uint8_t flags;           /* Sender-side validity & health flags */
    uint8_t confidence;      /* Quality/confidence metric (0-100) */
    uint32_t sequence_id;    /* Monotonically increasing sequence number */
    int32_t result_value;    /* Quantized inference class or control target */
} protocol_msg_t;

/**
 * Serialized payload size in bytes for the canonical semantic representation.
 *
 * Layout (12 bytes, big-endian byte order):
 * [0]   : uint8_t  version
 * [1]   : uint8_t  msg_type
 * [2]   : uint8_t  flags
 * [3]   : uint8_t  confidence
 * [4-7] : uint32_t sequence_id
 * [8-11]: int32_t  result_value
 *
 * TODO(ARCH-DECISION): Wire Framing & Transport Encoding
 * The physical UART wire framing (e.g., COBS framing vs delimiter bytes 0xAA 0x55)
 * is deliberately OPEN at stage P0.5. Once UART topology and DMA/interrupt reception
 * strategy are finalized on hardware, framing delimiters and packet length markers
 * will be implemented in a dedicated transport layer that encapsulates this payload.
 *
 * TODO(ARCH-DECISION): Integrity Checksum / CRC Selection
 * The error detection algorithm (CRC-16-CCITT vs CRC-32 vs Fletcher-16) is
 * deliberately OPEN at stage P0.5 until UART baud rate and STM32 hardware CRC
 * peripheral availability are evaluated.
 */
#define PROTOCOL_PAYLOAD_SIZE 12U

/**
 * @brief Encode a semantic message struct into a canonical byte buffer.
 *
 * Encodes multi-byte integers in network byte order (big-endian) without
 * reliance on host architecture or compiler struct packing.
 *
 * @param msg Source message to encode.
 * @param buf Destination buffer.
 * @param buf_len Length of destination buffer.
 * @param bytes_written Number of bytes written to buffer.
 * @return PROTOCOL_OK on success, or error code.
 */
protocol_error_t protocol_encode(
    const protocol_msg_t *msg,
    uint8_t *buf,
    size_t buf_len,
    size_t *bytes_written
);

/**
 * @brief Decode a canonical byte buffer into a semantic message struct.
 *
 * Validates version and message type during decoding.
 *
 * @param buf Source byte buffer.
 * @param buf_len Length of source buffer.
 * @param msg Destination struct to populate.
 * @return PROTOCOL_OK on success, or error code.
 */
protocol_error_t protocol_decode(
    const uint8_t *buf,
    size_t buf_len,
    protocol_msg_t *msg
);

#ifdef __cplusplus
}
#endif

#endif /* PROTOCOL_H */
