#include "FreeRTOS.h"
#include "task.h"

#define CYCCNT (*(volatile uint32_t *)0xe0001004u)
volatile uint32_t max_irq_masked_cycles;
static uint32_t started;
static unsigned active;

/* All callers run with BASEPRI raised. Nested mask operations must not restart
 * the outer measurement. Unsigned subtraction tolerates a DWT wrap (<51 s). */
static void begin(void)
{
    if (!active) {
        started = CYCCNT;
        active = 1;
    }
}
static void end(void)
{
    if (active) {
        uint32_t elapsed = CYCCNT - started;
        if (elapsed > max_irq_masked_cycles) max_irq_masked_cycles = elapsed;
        active = 0;
    }
}
void hea_irq_timing_reset(void)
{
    uint32_t mask = ulPortRaiseBASEPRI();
    active = 0;
    max_irq_masked_cycles = 0;
    vPortSetBASEPRI(mask);
}
uint32_t hea_irq_mask(void)
{
    uint32_t previous = ulPortRaiseBASEPRI();
    begin();
    return previous;
}
void hea_irq_restore(uint32_t mask)
{
    if (mask == 0) end();
    vPortSetBASEPRI(mask);
}

/* PendSV raises BASEPRI in assembly, bypassing port macros. Its only masked
 * call is vTaskSwitchContext (including stack checks). Measure that call too.
 * Other scheduler calls already inside a measured mask retain their owner. */
void __real_vTaskSwitchContext(void);
void __wrap_vTaskSwitchContext(void)
{
    uint32_t mask;
    __asm volatile ("mrs %0, basepri" : "=r" (mask));
    unsigned owner = mask != 0 && !active;
    if (owner) begin();
    __real_vTaskSwitchContext();
    if (owner) end();
}
