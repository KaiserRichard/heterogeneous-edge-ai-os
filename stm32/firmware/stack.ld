/* The reference linker lays out flash/data/bss; reserve 2 KiB for MSP. */
ASSERT(_ebss <= 0x2001f800, "RAM exhausted: reserve 2 KiB interrupt stack")
