#include "protocol.h"
#include "test_common.h"
#include <string.h>

static void test_protocol_valid_encode_decode(void) {
    printf("Running: %s...\n", __func__);
    protocol_msg_t original_msg = {
        .version = PROTOCOL_VERSION_CURRENT,
        .msg_type = PROTOCOL_MSG_PERCEPTION,
        .flags = PROTOCOL_FLAG_VALID,
        .confidence = 95,
        .sequence_id = 42000,
        .result_value = -12345
    };

    uint8_t buffer[PROTOCOL_PAYLOAD_SIZE];
    size_t written = 0;

    protocol_error_t enc_res = protocol_encode(&original_msg, buffer, sizeof(buffer), &written);
    TEST_ASSERT_EQ(enc_res, PROTOCOL_OK);
    TEST_ASSERT_EQ(written, PROTOCOL_PAYLOAD_SIZE);

    /* Verify big-endian byte layout manually */
    TEST_ASSERT_EQ(buffer[0], PROTOCOL_VERSION_CURRENT);
    TEST_ASSERT_EQ(buffer[1], PROTOCOL_MSG_PERCEPTION);
    TEST_ASSERT_EQ(buffer[2], PROTOCOL_FLAG_VALID);
    TEST_ASSERT_EQ(buffer[3], 95);
    /* 42000 = 0x0000A410 */
    TEST_ASSERT_EQ(buffer[4], 0x00);
    TEST_ASSERT_EQ(buffer[5], 0x00);
    TEST_ASSERT_EQ(buffer[6], 0xA4);
    TEST_ASSERT_EQ(buffer[7], 0x10);

    /* Decode into new struct */
    protocol_msg_t decoded_msg;
    memset(&decoded_msg, 0, sizeof(decoded_msg));

    protocol_error_t dec_res = protocol_decode(buffer, sizeof(buffer), &decoded_msg);
    TEST_ASSERT_EQ(dec_res, PROTOCOL_OK);
    TEST_ASSERT_EQ(decoded_msg.version, original_msg.version);
    TEST_ASSERT_EQ(decoded_msg.msg_type, original_msg.msg_type);
    TEST_ASSERT_EQ(decoded_msg.flags, original_msg.flags);
    TEST_ASSERT_EQ(decoded_msg.confidence, original_msg.confidence);
    TEST_ASSERT_EQ(decoded_msg.sequence_id, original_msg.sequence_id);
    TEST_ASSERT_EQ(decoded_msg.result_value, original_msg.result_value);

    /* Test heartbeat message type */
    original_msg.msg_type = PROTOCOL_MSG_HEARTBEAT;
    original_msg.flags = 0;
    original_msg.confidence = 0;
    original_msg.sequence_id = 1;
    original_msg.result_value = 0;

    enc_res = protocol_encode(&original_msg, buffer, sizeof(buffer), &written);
    TEST_ASSERT_EQ(enc_res, PROTOCOL_OK);
    dec_res = protocol_decode(buffer, sizeof(buffer), &decoded_msg);
    TEST_ASSERT_EQ(dec_res, PROTOCOL_OK);
    TEST_ASSERT_EQ(decoded_msg.msg_type, PROTOCOL_MSG_HEARTBEAT);
}

static void test_protocol_malformed_input(void) {
    printf("Running: %s...\n", __func__);
    protocol_msg_t msg = {
        .version = PROTOCOL_VERSION_CURRENT,
        .msg_type = PROTOCOL_MSG_PERCEPTION,
        .flags = PROTOCOL_FLAG_VALID,
        .confidence = 80,
        .sequence_id = 10,
        .result_value = 100
    };

    uint8_t buffer[PROTOCOL_PAYLOAD_SIZE];
    size_t written = 0;

    /* NULL pointers */
    TEST_ASSERT_EQ(protocol_encode(NULL, buffer, sizeof(buffer), &written), PROTOCOL_ERR_NULL_PTR);
    TEST_ASSERT_EQ(protocol_encode(&msg, NULL, sizeof(buffer), &written), PROTOCOL_ERR_NULL_PTR);
    TEST_ASSERT_EQ(protocol_encode(&msg, buffer, sizeof(buffer), NULL), PROTOCOL_ERR_NULL_PTR);
    TEST_ASSERT_EQ(protocol_decode(NULL, sizeof(buffer), &msg), PROTOCOL_ERR_NULL_PTR);
    TEST_ASSERT_EQ(protocol_decode(buffer, sizeof(buffer), NULL), PROTOCOL_ERR_NULL_PTR);

    /* Buffer too small */
    TEST_ASSERT_EQ(protocol_encode(&msg, buffer, PROTOCOL_PAYLOAD_SIZE - 1, &written), PROTOCOL_ERR_BUFFER_TOO_SMALL);
    TEST_ASSERT_EQ(protocol_decode(buffer, PROTOCOL_PAYLOAD_SIZE - 1, &msg), PROTOCOL_ERR_BUFFER_TOO_SMALL);
}

static void test_protocol_unsupported_version_and_type(void) {
    printf("Running: %s...\n", __func__);
    uint8_t buffer[PROTOCOL_PAYLOAD_SIZE];
    size_t written = 0;

    /* Unsupported version in encode */
    protocol_msg_t bad_version_msg = {
        .version = 99, /* Invalid */
        .msg_type = PROTOCOL_MSG_PERCEPTION,
        .flags = 0,
        .confidence = 50,
        .sequence_id = 1,
        .result_value = 0
    };
    TEST_ASSERT_EQ(protocol_encode(&bad_version_msg, buffer, sizeof(buffer), &written), PROTOCOL_ERR_UNSUPPORTED_VERSION);

    /* Unsupported message type in encode */
    protocol_msg_t bad_type_msg = {
        .version = PROTOCOL_VERSION_CURRENT,
        .msg_type = 0xAA, /* Invalid type */
        .flags = 0,
        .confidence = 50,
        .sequence_id = 1,
        .result_value = 0
    };
    TEST_ASSERT_EQ(protocol_encode(&bad_type_msg, buffer, sizeof(buffer), &written), PROTOCOL_ERR_INVALID_MSG_TYPE);

    /* Decode buffer with invalid version */
    protocol_msg_t valid_msg = {
        .version = PROTOCOL_VERSION_CURRENT,
        .msg_type = PROTOCOL_MSG_PERCEPTION,
        .flags = 0,
        .confidence = 50,
        .sequence_id = 1,
        .result_value = 0
    };
    TEST_ASSERT_EQ(protocol_encode(&valid_msg, buffer, sizeof(buffer), &written), PROTOCOL_OK);

    /* Corrupt version byte */
    buffer[0] = 0xFE;
    protocol_msg_t decoded_msg;
    TEST_ASSERT_EQ(protocol_decode(buffer, sizeof(buffer), &decoded_msg), PROTOCOL_ERR_UNSUPPORTED_VERSION);

    /* Restore version, corrupt msg_type byte */
    buffer[0] = PROTOCOL_VERSION_CURRENT;
    buffer[1] = 0x55; /* Unknown type */
    TEST_ASSERT_EQ(protocol_decode(buffer, sizeof(buffer), &decoded_msg), PROTOCOL_ERR_INVALID_MSG_TYPE);
}

int main(void) {
    printf("=== Starting Protocol Unit Tests ===\n");
    test_protocol_valid_encode_decode();
    test_protocol_malformed_input();
    test_protocol_unsupported_version_and_type();
    TEST_REPORT();
    return (g_test_failures == 0) ? 0 : 1;
}
