/* Instrument the reference port without changing third_party/. */
#ifndef HEA_PORTMACRO_H
#define HEA_PORTMACRO_H
#include HEA_REFERENCE_PORTMACRO
uint32_t hea_irq_mask(void);
void hea_irq_restore(uint32_t mask);
#undef portSET_INTERRUPT_MASK_FROM_ISR
#undef portCLEAR_INTERRUPT_MASK_FROM_ISR
#undef portDISABLE_INTERRUPTS
#undef portENABLE_INTERRUPTS
#define portSET_INTERRUPT_MASK_FROM_ISR() hea_irq_mask()
#define portCLEAR_INTERRUPT_MASK_FROM_ISR(x) hea_irq_restore(x)
#define portDISABLE_INTERRUPTS() ((void)hea_irq_mask())
#define portENABLE_INTERRUPTS() hea_irq_restore(0)
#endif
