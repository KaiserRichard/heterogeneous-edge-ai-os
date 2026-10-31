.syntax unified
.cpu cortex-m4
.thumb
.section .isr_vector,"a",%progbits
.global vectors
vectors:
.word 0x20020000, Reset_Handler
/* Exceptions 2..10: fault closed, including reserved entries. */
.rept 9
.word firmware_fault
.endr
.word SVC_Handler, firmware_fault, firmware_fault, PendSV_Handler, SysTick_Handler
/* External interrupts 0..27. */
.rept 28
.word firmware_fault
.endr
.word TIM2_Handler
.rept 8
.word firmware_fault
.endr
.word USART1_Handler
.rept 59
.word firmware_fault
.endr
.section .text.Reset_Handler,"ax",%progbits
.global Reset_Handler
.thumb_func
Reset_Handler:
/* Enable CP10/11 before any hard-float C code. */
ldr r0, =0xe000ed88
ldr r1, [r0]
orr r1, r1, #0x00f00000
str r1, [r0]
dsb
isb
ldr r0, =_la_data
ldr r1, =_sdata
ldr r2, =_edata
1: cmp r1, r2
bcs 2f
ldr r3, [r0], #4
str r3, [r1], #4
b 1b
2: ldr r1, =_sbss
ldr r2, =_ebss
movs r3, #0
3: cmp r1, r2
bcs 4f
str r3, [r1], #4
b 3b
4: bl main
b firmware_fault
