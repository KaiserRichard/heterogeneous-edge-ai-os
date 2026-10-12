FREERTOS_REF ?= /Users/quockaiser/Desktop/OS/OS-project/heterogeneous-edge-ai-os/third_party/nucleo-f446re-freertos
REF_BOARD := $(FREERTOS_REF)/004LEDsNotifyISR
KERNEL := $(FREERTOS_REF)/ThirdParty/FreeRTOS
CROSS_COMPILE ?= /usr/local/bin/arm-none-eabi-
CC := $(CROSS_COMPILE)gcc
OBJCOPY := $(CROSS_COMPILE)objcopy
SIZE := $(CROSS_COMPILE)size
BUILD := build
CLOCK_SOURCE ?= HSE
ifeq ($(CLOCK_SOURCE),HSE)
CLOCK_HSE := 1
else ifeq ($(CLOCK_SOURCE),HSI)
CLOCK_HSE := 0
else
$(error CLOCK_SOURCE must be HSE or HSI)
endif
UART_BAUD ?= 921600
DEBUG_VCP ?= 0
BRINGUP_BLINK ?= 0
ARCH := -mcpu=cortex-m4 -mthumb -mfloat-abi=hard -mfpu=fpv4-sp-d16
CPPFLAGS := -I. -I../include -I../../protocol/include -I$(REF_BOARD)/src -I$(KERNEL)/include -I$(KERNEL)/portable/GCC/ARM_CM4F -DCLOCK_HSE=$(CLOCK_HSE) -DUART_BAUD=$(UART_BAUD) -DDEBUG_VCP=$(DEBUG_VCP) -DBRINGUP_BLINK=$(BRINGUP_BLINK)
CFLAGS := $(ARCH) -std=c11 -Os -g3 -Wall -Wextra -Werror -ffunction-sections -fdata-sections -fno-common -MMD -MP
SOURCES := main.c ../src/supervisor.c ../src/supervisor_protocol.c ../../protocol/src/hea_proto.c $(KERNEL)/tasks.c $(KERNEL)/queue.c $(KERNEL)/list.c $(KERNEL)/stream_buffer.c $(KERNEL)/portable/GCC/ARM_CM4F/port.c
OBJECTS := $(addprefix $(BUILD)/,$(notdir $(SOURCES:.c=.o))) $(BUILD)/startup.o
.PHONY: all clean FORCE
all: $(BUILD)/firmware.elf $(BUILD)/firmware.bin
	$(SIZE) $(BUILD)/firmware.elf | tee $(BUILD)/size.txt
$(BUILD):
	mkdir -p $@
# Rebuild when command-line configuration changes, without requiring clean.
$(BUILD)/config: FORCE | $(BUILD)
	@printf '%s\n' '$(CC) $(CPPFLAGS) $(CFLAGS)' > $@.tmp
	@cmp -s $@.tmp $@ || cp $@.tmp $@
	@rm $@.tmp
define compile
$(BUILD)/$(notdir $(1:.c=.o)): $(1) $(BUILD)/config | $(BUILD)
	$$(CC) $$(CPPFLAGS) $$(CFLAGS) -c $$< -o $$@
endef
$(foreach src,$(SOURCES),$(eval $(call compile,$(src))))
$(BUILD)/startup.o: startup.S $(BUILD)/config | $(BUILD)
	$(CC) $(ARCH) -c $< -o $@
$(BUILD)/firmware.elf: $(OBJECTS) $(REF_BOARD)/lnk/lk_f446re.ld stack.ld
	$(CC) $(ARCH) -nostartfiles --specs=nosys.specs -T$(REF_BOARD)/lnk/lk_f446re.ld -Tstack.ld -Wl,--gc-sections,-Map=$(BUILD)/firmware.map $(OBJECTS) -o $@
$(BUILD)/firmware.bin: $(BUILD)/firmware.elf
	$(OBJCOPY) -O binary $< $@
clean:
	rm -rf $(BUILD)
-include $(OBJECTS:.o=.d)
