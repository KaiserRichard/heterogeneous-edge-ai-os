# Portable supervisor tests; shared hea_proto is the only wire implementation.
CC ?= cc
CFLAGS ?= -std=c99 -O2 -g -Wall -Wextra -Wpedantic -Wshadow -Wconversion -Werror
SAN ?= -fsanitize=address,undefined
BUILD := build
SOURCES := src/supervisor.c src/supervisor_protocol.c ../protocol/src/hea_proto.c
HEADERS := include/supervisor.h include/supervisor_protocol.h ../protocol/include/hea_proto.h

.PHONY: test clean
test: $(BUILD)/test_supervisor $(BUILD)/test_rx_dma $(BUILD)/test_tick_diagnostic $(BUILD)/test_imu_mpu6050
	./$(BUILD)/test_supervisor
	./$(BUILD)/test_rx_dma
	./$(BUILD)/test_tick_diagnostic
	./$(BUILD)/test_imu_mpu6050

$(BUILD)/test_supervisor: tests/test_supervisor.c $(SOURCES) $(HEADERS) | $(BUILD)
	$(CC) $(CFLAGS) $(SAN) -Iinclude -I../protocol/include tests/test_supervisor.c $(SOURCES) -o $@

$(BUILD):
	mkdir -p $@

clean:
	rm -rf $(BUILD)

.PHONY: firmware
firmware:
	$(MAKE) -C firmware

$(BUILD)/test_rx_dma: tests/test_rx_dma.c include/rx_dma_cursor.h ../protocol/src/hea_proto.c ../protocol/include/hea_proto.h | $(BUILD)
	$(CC) $(CFLAGS) $(SAN) -Iinclude -I../protocol/include tests/test_rx_dma.c ../protocol/src/hea_proto.c -o $@

$(BUILD)/test_tick_diagnostic: tests/test_tick_diagnostic.c include/tick_diagnostic.h | $(BUILD)
	$(CC) $(CFLAGS) $(SAN) -Iinclude $< -o $@

$(BUILD)/test_imu_mpu6050: firmware/imu_mpu6050_test.c firmware/imu_mpu6050.c firmware/imu_mpu6050.h | $(BUILD)
	$(CC) $(CFLAGS) $(SAN) -DIMU_MPU6050_HOST_TEST -Ifirmware firmware/imu_mpu6050_test.c firmware/imu_mpu6050.c -lm -o $@
