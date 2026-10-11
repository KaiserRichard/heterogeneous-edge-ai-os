CC ?= cc
CFLAGS ?= -std=c99 -O2 -g -Wall -Wextra -Wpedantic -Wshadow -Wconversion -Werror
SAN ?= -fsanitize=address,undefined
CPPFLAGS += -D_GNU_SOURCE -D_DEFAULT_SOURCE -D_DARWIN_C_SOURCE -D_POSIX_C_SOURCE=200809L -Iinclude -I../protocol/include
BUILD := build
COMMON := src/hea_runtime.c src/hea_ipc.c ../protocol/src/hea_proto.c
HEADERS := $(wildcard include/*.h) ../protocol/include/hea_proto.h
PROGRAMS := hea_source hea_infer_stub hea_bridge hea_rx
UNAME := $(shell uname -s)
ifeq ($(UNAME),Linux)
PTY_LIB := -lutil
endif

.PHONY: all test clean
all: $(addprefix $(BUILD)/,$(PROGRAMS))
$(BUILD)/%: src/%.c $(COMMON) $(HEADERS) | $(BUILD)
	$(CC) $(CPPFLAGS) $(CFLAGS) $< $(COMMON) $(LDFLAGS) $(LDLIBS) -o $@
$(BUILD)/test_core: tests/test_core.c src/hea_ipc.c include/hea_ipc.h | $(BUILD)
	$(CC) $(CPPFLAGS) $(CFLAGS) $(SAN) tests/test_core.c src/hea_ipc.c -o $@
$(BUILD)/san/%: src/%.c $(COMMON) $(HEADERS) | $(BUILD)/san
	$(CC) $(CPPFLAGS) $(CFLAGS) $(SAN) $< $(COMMON) $(LDFLAGS) $(LDLIBS) -o $@
$(BUILD)/test_pipeline: tests/test_pipeline.c $(COMMON) $(HEADERS) | $(BUILD)
	$(CC) $(CPPFLAGS) $(CFLAGS) $(SAN) $< $(COMMON) $(PTY_LIB) -o $@
test: $(BUILD)/test_core $(BUILD)/test_pipeline $(addprefix $(BUILD)/san/,$(PROGRAMS))
	./$(BUILD)/test_core
	./$(BUILD)/test_pipeline
	python3 tests/test_summary.py
$(BUILD) $(BUILD)/san:
	mkdir -p $@
clean:
	rm -rf $(BUILD)
