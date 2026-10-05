# Host build of the shared protocol library and its unit tests (macOS or Linux).
CC ?= cc
CFLAGS ?= -std=c99 -O2 -g -Wall -Wextra -Wpedantic -Wshadow -Wconversion -Werror
SAN ?= -fsanitize=address,undefined

BUILD := build

.PHONY: test clean
test: $(BUILD)/test_proto
	./$(BUILD)/test_proto

$(BUILD)/test_proto: tests/test_proto.c src/hea_proto.c include/hea_proto.h | $(BUILD)
	$(CC) $(CFLAGS) $(SAN) -Iinclude tests/test_proto.c src/hea_proto.c -o $@

$(BUILD):
	mkdir -p $@

clean:
	rm -rf $(BUILD)
