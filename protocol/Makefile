# Host build of the shared protocol library and its unit tests (macOS or Linux).
CC ?= cc
CFLAGS ?= -std=c99 -O2 -g -Wall -Wextra -Wpedantic -Wshadow -Wconversion -Werror
SAN ?= -fsanitize=address,undefined

BUILD := build

.PHONY: test test-char-modes clean
test: $(BUILD)/test_proto $(BUILD)/test_clock_sync
	./$(BUILD)/test_proto
	./$(BUILD)/test_clock_sync

$(BUILD)/test_proto: tests/test_proto.c src/hea_proto.c include/hea_proto.h | $(BUILD)
	$(CC) $(CFLAGS) $(SAN) -Iinclude tests/test_proto.c src/hea_proto.c -o $@

$(BUILD)/test_clock_sync: tests/test_clock_sync.c src/hea_clock_sync.c include/hea_clock_sync.h | $(BUILD)
	$(CC) $(CFLAGS) $(SAN) -Iinclude tests/test_clock_sync.c src/hea_clock_sync.c -lm -o $@

test-char-modes:
	$(MAKE) clean
	$(MAKE) test CFLAGS="$(CFLAGS) -fsigned-char"
	$(MAKE) clean
	$(MAKE) test CFLAGS="$(CFLAGS) -funsigned-char"

$(BUILD):
	mkdir -p $@

clean:
	rm -rf $(BUILD)
