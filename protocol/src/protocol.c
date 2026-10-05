#include "protocol.h"

protocol_error_t protocol_encode(
    const protocol_msg_t *msg,
    uint8_t *buf,
    size_t buf_len,
    size_t *bytes_written
) {
    if (msg == NULL || buf == NULL || bytes_written == NULL) {
        return PROTOCOL_ERR_NULL_PTR;
    }

    if (buf_len < PROTOCOL_PAYLOAD_SIZE) {
        return PROTOCOL_ERR_BUFFER_TOO_SMALL;
    }

    if (msg->version != PROTOCOL_VERSION_CURRENT) {
        return PROTOCOL_ERR_UNSUPPORTED_VERSION;
    }

    if (msg->msg_type != PROTOCOL_MSG_HEARTBEAT && msg->msg_type != PROTOCOL_MSG_PERCEPTION) {
        return PROTOCOL_ERR_INVALID_MSG_TYPE;
    }

    /* Encode header fields */
    buf[0] = msg->version;
    buf[1] = msg->msg_type;
    buf[2] = msg->flags;
    buf[3] = msg->confidence;

    /* Encode sequence_id in big-endian */
    buf[4] = (uint8_t)((msg->sequence_id >> 24) & 0xFFU);
    buf[5] = (uint8_t)((msg->sequence_id >> 16) & 0xFFU);
    buf[6] = (uint8_t)((msg->sequence_id >> 8) & 0xFFU);
    buf[7] = (uint8_t)(msg->sequence_id & 0xFFU);

    /* Encode result_value in big-endian */
    uint32_t val_bits = (uint32_t)msg->result_value;
    buf[8] = (uint8_t)((val_bits >> 24) & 0xFFU);
    buf[9] = (uint8_t)((val_bits >> 16) & 0xFFU);
    buf[10] = (uint8_t)((val_bits >> 8) & 0xFFU);
    buf[11] = (uint8_t)(val_bits & 0xFFU);

    *bytes_written = PROTOCOL_PAYLOAD_SIZE;
    return PROTOCOL_OK;
}

protocol_error_t protocol_decode(
    const uint8_t *buf,
    size_t buf_len,
    protocol_msg_t *msg
) {
    if (buf == NULL || msg == NULL) {
        return PROTOCOL_ERR_NULL_PTR;
    }

    if (buf_len < PROTOCOL_PAYLOAD_SIZE) {
        return PROTOCOL_ERR_BUFFER_TOO_SMALL;
    }

    uint8_t ver = buf[0];
    if (ver != PROTOCOL_VERSION_CURRENT) {
        return PROTOCOL_ERR_UNSUPPORTED_VERSION;
    }

    uint8_t type = buf[1];
    if (type != PROTOCOL_MSG_HEARTBEAT && type != PROTOCOL_MSG_PERCEPTION) {
        return PROTOCOL_ERR_INVALID_MSG_TYPE;
    }

    msg->version = ver;
    msg->msg_type = type;
    msg->flags = buf[2];
    msg->confidence = buf[3];

    msg->sequence_id = ((uint32_t)buf[4] << 24) |
                       ((uint32_t)buf[5] << 16) |
                       ((uint32_t)buf[6] << 8)  |
                       ((uint32_t)buf[7]);

    uint32_t val_bits = ((uint32_t)buf[8] << 24)  |
                        ((uint32_t)buf[9] << 16)  |
                        ((uint32_t)buf[10] << 8)  |
                        ((uint32_t)buf[11]);
    msg->result_value = (int32_t)val_bits;

    return PROTOCOL_OK;
}
