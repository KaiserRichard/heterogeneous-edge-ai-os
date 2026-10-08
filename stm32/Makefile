# Portable supervisor tests; shared hea_proto is the only wire implementation.
CC ?= cc
CFLAGS ?= -std=c99 -O2 -g -Wall -Wextra -Wpedantic -Wshadow -Wconversion -Werror
SAN ?= -fsanitize=address,undefined
BUILD := build
SOURCES := src/supervisor.c src/supervisor_protocol.c ../protocol/src/hea_proto.c
HEADERS := include/supervisor.h include/supervisor_protocol.h ../protocol/include/hea_proto.h

.PHONY: test clean
test: $(BUILD)/test_supervisor
	./$(BUILD)/test_supervisor

$(BUILD)/test_supervisor: tests/test_supervisor.c $(SOURCES) $(HEADERS) | $(BUILD)
	$(CC) $(CFLAGS) $(SAN) -Iinclude -I../protocol/include tests/test_supervisor.c $(SOURCES) -o $@

$(BUILD):
	mkdir -p $@

clean:
	rm -rf $(BUILD)
