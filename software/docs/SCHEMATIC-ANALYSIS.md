# MicroPetal Uno R1 schematic analysis

Analyzed 21 November 2026 from the repository's `../MicroPetal_Uno.kicad_sch` and matching-named PCB. Schematic exported with KiCad 10 CLI; pin mapping also checked against PCB pads. The `production` files were not used to certify what the manufacturer actually built; confirm the arrived assembly/MCU marking matches these source files.

## Before the first USB connection: VCC must be 3.3 V

**JP3 defaults 1–2 closed, selecting +5 V for VCC. U4 SN65HVD230 is powered by VCC but is specified for 3.0–3.6 V operation.** The MCU itself supports a wider supply, but that does not make the complete assembly a 5 V board. This is out of U4's recommended operating range, not a claim that 5 V exceeds its absolute maximum.

With all power disconnected, cut/open JP3 **1–2** and bridge **2–3**. Confirm +5V is not shorted to +3V3. Leave JP7 at its default 1–2 connection so VCCA follows VCC (now 3.3 V). Use a meter to verify the jumper modification. A first current-limited power-up and measurement of VCC near 3.3 V is recommended. Treat all header I/O as **3.3 V** in these guides. Do not connect a 5 V-output shield directly.

JP3 pins: 1 = +5V, 2 = VCC, 3 = +3V3. JP7: 1 = VCCA, 2 = VCC, 3 = +3V3. Verify pad identity from CAD/continuity, not assumed left/right orientation.

## Programming

USB-C D−/D+ go directly to PA11/PA12, with a 1.5k pull-up to +3V3 on D+. R2/R3 provide 5.1k CC pulldowns. There is **no USB-UART bridge**. Puya's factory USB-HID ISP loader is the proposed upload path (`puyaisp -t hid -f firmware.bin`); it remains untested on this assembled R1.

J3 is a BOOT/power breakout, not a standard AVR ISP header:

| Pin | Net |
|---|---|
| 1 | VCC |
| 2 | +3V3 |
| 3 | BOOT0 (through R4 5.1k to PF8-BOOT0; R15 100k pull-down) |
| 4 | VCC |
| 5 | GND |
| 6 | +5V |

For ROM ISP, fit a shunt **J3 3–4** with power off, then connect USB or press/release RST. After programming, disconnect power, remove the shunt, and reconnect/reset. **SW1 BTN is not a BOOT button. Do not blindly put shunts on the other J3 pairs.** Do not jumper 5–6 (it shorts +5V to ground).

J1 SWD breakout: 1 GND, 2 PA14/SWCLK, 3 PA13/SWDIO, 4 VCC/reference. RST is available at SW2 / Arduino reset header. Leave debugger power output disconnected when USB powers the board. A 3.3 V-compatible probe and PY32F071-aware flash tool are a recovery route, not a verified generic STM32/ST-Link recipe.

## Header and peripherals

- D13 = PB13. D2 green LED anode goes through **22k R9** to VCC; cathode is PB13, so **LOW = on**. Expect a dim LED. SPI SCK shares it.
- SW1 BTN shorts PB14 / D12 / SPI MISO to ground; R7 22k pulls it up. **Do not press BTN during SPI transfers.**
- Dedicated SDA/SCL = PB11/PB10, exposed as Arduino pins 22/23. These are **not A4/A5**: A4/A5 = PA4/PA5 DAC outputs. R5/R6 are 5.1k pull-ups to VCC.
- JP4/JP5 are open by default. Closing JP4 links PA4/A4 to PB14/D12; JP5 links PA5/A5 to PB13/D13. Leave them open for these examples. They can otherwise join independently driven pins, the LED/button and bus lines.
- SPI2 maps correctly to D10 SS/PB12, D11 MOSI/PB15, D12 MISO/PB14, D13 SCK/PB13 (AF0).
- **D1 = PB1 has no UART TX function.** The usable header pair is USART3 RX on **D0/PB0 AF10**, TX on **D2/PB2 AF10**. `Serial` uses that pair; it cannot honestly emulate Uno's D0/D1 UART layout.
- PA9/PA10 are MCU USART1 pins but not on the Uno header in this CAD.
- A0–A7 = PA0–PA7, ADC channels 0–7; ADC input range is 0..VCCA, not automatically 5 V. A4/A5 have real DAC channels.

## CAN is not available with the specified F071

The board intentionally accommodates both F071 and F072; the initial intended assembly uses F071. The transceiver is present for the F072 option, not evidence that the initial F071 should provide CAN.

U4 is routed to PB8/PB9 (D8/D9). However, the **PY32F071 has no CAN controller** in its datasheet/device definitions. A transceiver cannot add one. No `CAN` API is provided and D8/D9 should not be used by starter examples (U4 remains connected). Confirm whether the actual assembly uses an F072 or an F071; a future F072 variant needs its own device definitions/vector table and testing. Merely changing the MCU name in a board menu is not a validated fix. Firmware cannot add missing F071 CAN hardware.

## Power and source consistency

- USB VBUS passes through default-closed JP1 to +5V and the 3.3V MIC5504. For first bring-up use USB only; do not simultaneously connect barrel/VIN power.
- AMS1117 output connects via default-open JP6. The design explicitly labels JP1 “Cut if using AMS1117”; do not close JP6 and mix sources without reviewing that selection/backfeed path.
- No AREF pin is exposed. `analogReference(DEFAULT)` means VCCA; other modes are not implemented.
- Schematic XML reports duplicate U1 pin **35** as VSS and PF5. The actual PCB pad 35 is `/PF5`, while pad 49 is GND. This is a CAD-symbol/netlist inconsistency, not evidence that PCB PF5 is grounded. Fix the symbol before a future schematic-to-PCB update; this task did not edit the hardware.

## References

- [Puya PY32F071 datasheet, V1.4](https://www.puyasemi.com/download_path/%E6%95%B0%E6%8D%AE%E6%89%8B%E5%86%8C/MCU%20%E5%BE%AE%E5%A4%84%E7%90%86%E5%99%A8/PY32F071%E7%B3%BB%E5%88%97%E6%95%B0%E6%8D%AE%E6%89%8B%E5%86%8C_V1.4.pdf): device table, QFN48 pinout, AF tables, supply limits. Targets non-E F071 as named in the CAD; do not substitute an -E datasheet unnoticed.
- [TI SN65HVD230 datasheet](https://www.ti.com/lit/ds/symlink/sn65hvd230.pdf): recommended supply 3.0–3.6 V.
- [Puya ISP uploader](https://github.com/wagiminator/MCU-Flash-Tools), `puyaisp` 1.6.0: F071 USB-HID protocol; use the board-specific PF8/J3 wiring above, not the uploader README's generic PF4 example.
