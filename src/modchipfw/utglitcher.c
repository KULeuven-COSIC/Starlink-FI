#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/uart.h"
#include "hardware/gpio.h"
#include "hardware/pio.h"
#include "hardware/clocks.h"
#include "hardware/vreg.h"
#include "pulsegen.pio.h"

#define PIN_NRST   7
#define PIN_TRIG   6
#define PIN_PULSE  0
#define PIN_CAPS   1

#define PIN_LED1   16
#define PIN_LED2   17

int main()
{
    /* 
     * For some reason the serial communication fails after some time when running at 200MHz
     * For me everything worked fine at 250 MHz without changing the core voltage (vreg_set_voltage)
    */
    set_sys_clock_khz(250000, true);
    
    stdio_init_all();

    // GPIO initialisation.
    gpio_init(PIN_NRST);
    gpio_init(PIN_TRIG);
    gpio_init(PIN_PULSE);
    gpio_init(PIN_CAPS);
    gpio_init(PIN_LED1);
    gpio_init(PIN_LED2);
    gpio_set_dir(PIN_NRST, GPIO_OUT);
    gpio_set_dir(PIN_TRIG, GPIO_IN);
    gpio_set_dir(PIN_PULSE, GPIO_OUT);
    gpio_set_dir(PIN_CAPS, GPIO_OUT);
    gpio_set_dir(PIN_LED1, GPIO_OUT);
    gpio_set_dir(PIN_LED2, GPIO_OUT);
    gpio_set_pulls(PIN_CAPS, true, false);
    gpio_set_drive_strength(PIN_PULSE, GPIO_DRIVE_STRENGTH_12MA);
    gpio_set_drive_strength(PIN_CAPS, GPIO_DRIVE_STRENGTH_12MA);
    gpio_set_slew_rate(PIN_PULSE, GPIO_SLEW_RATE_FAST);

    // Setup PIO
    PIO pio = pio0;
    uint32_t sm = pio_claim_unused_sm(pio, true);
    uint32_t pio_offset = pio_add_program(pio, &pulsegen_program);
    pulsegen_program_init(pio, sm, pio_offset, PIN_TRIG, PIN_PULSE, PIN_CAPS);

    // Wait for serial connection
    while (!stdio_usb_connected()) {
      sleep_ms(500);
    }

    gpio_put(PIN_LED1, true);
    gpio_put(PIN_NRST, false);

    char cmd;
    uint32_t pulse_offset = 0;
    uint32_t pulse_width = 0;
    uint32_t trig_edges = 1;
    uint32_t gpio_states = 0;

    uint8_t gpio_pin = 0;
    uint8_t gpio_state = 0;

    while (true) {
        cmd = getchar();
        
        switch (cmd)
        {
            // Enable glitch SM
            case 'A':
                gpio_put(PIN_LED2, true);
                pio_sm_put_blocking(pio, sm, trig_edges);
                pio_sm_put_blocking(pio, sm, pulse_offset);
                pio_sm_put_blocking(pio, sm, pulse_width);

                gpio_put(PIN_NRST, true);
                sleep_ms(46); // Delay to make sure all UT signals are stable

                pio_sm_set_enabled(pio, sm, true);
                printf("A\n");
                break;

            // Wait for trigger
            case 'B':
                while(!pio_interrupt_get(pio0, 0)) {
                    cmd = getchar_timeout_us(1);
                    if (cmd == 'D') break; // Disarm
                };

                pio_sm_set_enabled(pio, sm, false);
                pio_interrupt_clear(pio, 0);
                pio_sm_clear_fifos(pio, sm);
                pio_sm_drain_tx_fifo(pio, sm);
                pio_sm_restart(pio, sm);
                pio_sm_set_enabled(pio, sm, false);
                
                pio_sm_exec_wait_blocking(pio, sm, pio_encode_set(pio_x, pio_offset));
                pio_sm_exec_wait_blocking(pio, sm, pio_encode_mov(pio_pc, pio_x));
                printf("T\n");
                gpio_put(PIN_LED2, false);
                break;
            
            // Set the number of edges before inserting a pulse
            case 'E':
                fread(&trig_edges, 1, 4, stdin);
                printf("%d\n", trig_edges);
                break;

            // Set the pulse offset
            case 'O':
                fread(&pulse_offset, 1, 4, stdin);
                printf("%d\n", pulse_offset);
                break;
            
            // Set the pulse width
            case 'W':
                fread(&pulse_width, 1, 4, stdin);
                printf("%d\n", pulse_width);
                break;

            // print the current pulse offset and width
            case 'S':
                printf("PulseGenerator offset: %d, width: %d, edges: %d\n", pulse_offset, pulse_width, trig_edges);
                break;

            // control a gpio pin, can be expanded to handle multiple pins
            case 'G':
                fread(&gpio_pin, 1, 1, stdin);
                fread(&gpio_state, 1, 1, stdin);

                if (gpio_pin == PIN_NRST) {
                    if (gpio_state == 0) {
                        gpio_put(PIN_NRST, false);
                    } else {
                        gpio_put(PIN_NRST, true);
                    }    
                }
                printf("G\n");
                break;

            // Read state of GPIOs
            case 'R':
                gpio_states = gpio_get_all();
                printf("%d\n", gpio_states);
                break;

            default:
                break;
        }
    }

    return 0;
}