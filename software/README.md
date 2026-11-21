# MicroPetal Uno R1 — Arduino + PlatformIO

Experimental **0.1.0** board support for the PY32F071C1BU6, 128 KB flash / 16 KB SRAM.
The board also supports PY32F072, but **F071 is the initial assembly/software target**. F072 support is not implemented or validated in this release; its CAN option is not an F071 board defect.

Uses the official ArduinoCore-API and Puya F07x HAL, rather than pretending this chip is an F030 or STM32. Normal `setup()` / `loop()` sketches; no Arduino Uno/AVR bootloader.

**Software compiled on Apple Silicon; not hardware-tested.** Boards are expected next week. Read the first-power instructions before connecting one.

- [Arduino IDE beginner guide](docs/ARDUINO-START.md)
- [PlatformIO beginner guide](docs/PLATFORMIO-START.md)
- [Schematic analysis and power corrections](docs/SCHEMATIC-ANALYSIS.md)
- [Pinout and implemented API](docs/PINOUT.md)
- [Bring-up checklist](docs/BRINGUP.md)
- [Verification results](docs/VERIFICATION.md)
- [Licenses and upstream sources](THIRD-PARTY.md)

## What is included

A classic Arduino hardware package (`hardware/micropetal/py32`), a local PlatformIO platform (`platform`), a cross-platform tool installer, USB-HID ROM-ISP upload recipes, examples, and build/check scripts. The factory loader means **no custom bootloader and no application flash offset**: sketches start at 0x08000000.

The first release deliberately runs from the internal **8 MHz HSI**. The board's 8 MHz and 32.768 kHz crystals are not required for first Blink. No USB CDC/Serial, CAN, EEPROM emulation, Servo integration, or blanket AVR-library compatibility is claimed. `Serial` is a physical UART, not USB.

No CAD, jumpers, option bytes, or live websites were modified. This package is local; no public Boards Manager URL is available yet.
