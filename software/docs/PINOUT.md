# Pinout and API status — experimental 0.1.0

| Arduino | MCU | Notes |
|---|---|---|
| D0 | PB0 | USART3 RX, Serial |
| D1 | PB1 | GPIO; **not UART TX** |
| D2 | PB2 | USART3 TX, Serial |
| D3 | PB3 | PWM TIM2 CH2 |
| D4 | PB4 | PWM TIM3 CH1 |
| D5 | PB5 | PWM TIM3 CH2 |
| D6 | PB6 | PWM TIM1 CH3 |
| D7 | PB7 | PWM TIM1 CH1 |
| D8 | PB8 | U4 receive output connected; reserve |
| D9 | PB9 | U4 TX input connected; PWM exists but reserve with U4 fitted |
| D10 | PB12 | SPI2 SS (application controls CS) |
| D11 | PB15 | SPI2 MOSI, PWM TIM15 CH2 |
| D12 | PB14 | SPI2 MISO + active-low BTN |
| D13 | PB13 | SPI2 SCK + active-low LED |
| A0–A7 (14–21) | PA0–PA7 | ADC 0–7; A4/A5 also DAC1 channels 1/2 |
| SDA (22) | PB11 | Dedicated I2C data; 5.1k to VCC |
| SCL (23) | PB10 | Dedicated I2C clock; 5.1k to VCC |

`Serial`/`Serial1` are aliases of the same USART3, D2 TX / D0 RX. UART is 8N1 only, interrupt-driven 127-byte usable RX buffer, blocking TX. Overrun drops new bytes. `begin(baud, config)` rejects unsupported formats (`bool(Serial)` stays false), not silently converts them.

Implemented: digital I/O incl. pull-up/down/open-drain, `millis/micros/delay/delayMicroseconds`, `pulseIn`, shift I/O, GPIO edge interrupts, ADC, PWM, DAC, `tone/noTone`, Print/Stream/String, map/random, controller-mode Wire and SPI. Software compilation is not proof of electrical/timing accuracy.

- ADC defaults to 10 bits; `analogReadResolution(12)` uses full 12-bit range. `analogReference(DEFAULT)` is VCCA; no other reference mode is implemented.
- `analogWrite` defaults to 8 bits (0–255), selectable up to 12; A4/A5 output real DAC voltage. Listed PWM outputs run at nominal 1 kHz; other pins fall back to LOW/HIGH at half-scale. Do not use D9 with the connected transceiver as a generic PWM example.
- `tone` toggles any exposed pin with TIM14 IRQ, 8–20,000 Hz requested range, one tone at a time. Upper frequencies incur substantial CPU load; start at 440 Hz. No Servo/timer-library compatibility claim.
- EXTI permits only one GPIO per bit index: e.g. D0/PB0 and A0/PA0 cannot both own EXTI0. A later attach replaces that line. ISR callbacks must be short; no delay/Serial output inside them.
- `Wire`: **software open-drain controller**, dedicated pins 22/23; 32-byte buffers, repeated START, bounded 25ms clock-stretch wait, requested clock capped at 100 kHz (actual slower due GPIO overhead). No target/slave callbacks, multi-controller arbitration or hardware-I2C/DMA claims. `endTransmission`: 0 OK, 1 buffer overflow, 2 address failure, 3 data failure, 4 bus-start failure. Clock-stretch failures during byte transfer share address/data failure codes. Prefer ordinary I2C sensors with 3.3 V supplies.
- `SPI`: hardware SPI2, modes 0–3, both bit orders, maximum requested rate rounded down to an available divisor (at 8 MHz, max 4 MHz). `transfer16` respects byte order. Manually drive SS/CS around transfers; transaction methods do not select the device. `usingInterrupt` conservatively masks all IRQs for the transaction; keep these short or SysTick/UART may lose events. No peripheral/target mode or DMA.
- No USB CDC/Serial, USB application stack, CAN on F071, EEPROM emulation, AVR register compatibility, `SoftwareSerial`, bundled Servo or verified low-power support. `printf` standard file I/O is not routed to Serial; use `Serial.print`.
- Core runs internal HSI at 8 MHz; no crystal/PLL menus in this release. F071 only, not F072 or -E without a separate review.
