# Board-arrival checks

None of the physical checks below have been performed. Do them in order, with no shield fitted.

1. Compare assembly MCU marking to F071C1BU6 / non-E target; check U4 type and solder bridges.
2. With power off, select JP3 3.3 V; leave JP7 1–2, JP4/JP5/JP6 open. Meter-check no 5V-to-3V3 short. Use USB only initially.
3. Current-limited first power; measure +5V, +3V3, VCC, VCCA. Confirm VCC/VCCA ≈3.3 V. Check abnormal heat/current before continuing.
4. Enter J3 3–4 BOOT mode and confirm HID enumeration; record VID:PID and host OS. Upload Blink with `puyaisp -t hid -f ...`. Capture actual write/verify result; remove BOOT shunt and reset.
5. Check LED polarity and 500ms intervals with scope; measure actual HSI/SysTick timing if accurate timing is needed.
6. Run Button; confirm active-low state. Check D12/MISO sharing behavior without attaching an SPI peripheral.
7. UART: D2 TX to external 3.3 V adapter RX, D0 RX to adapter TX; exercise receive burst/overflow behavior and 115200 TX. USB is not serial.
8. ADC: check A0 tied to GND and then 3.3V, plus a known intermediate voltage. Sweep A0–A7; never exceed VCCA. Check 10-bit and 12-bit output. DAC A4/A5: meter at 0/128/255, high impedance load.
9. Scope PWM D3–D7/D11 at 0/128/255, confirm 1kHz and shared timer channels do not reset one another. Repurpose each with digitalWrite/pinMode and verify PWM stops. Avoid D9/U4.
10. I2C: 3.3 V sensor on dedicated SDA/SCL; scan, repeated START register read, NACK and stuck-bus/clock-stretch timeout tests. Leave JP4/JP5 open.
11. SPI loopback: D11 to D12, test all modes/bit orders and 16-bit transfers. Do not press BTN. Check CS and LED/SCK loading.
12. Test edge interrupts, duplicate EXTI-line exclusion, tone stop/duration and serial input while normal sketches run.
13. Confirm reset and repeat USB-HID programming after a bad sketch. Do not change protection/option bytes as part of routine upload.

Record results before declaring a hardware-tested release. CAN is not a firmware test on F071: resolve the missing controller/hardware choice first.
