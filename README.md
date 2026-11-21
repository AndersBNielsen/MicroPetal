# MicroPetal Uno R1

Arduino Uno-format board accommodating PY32F071 and PY32F072. The initial assembly and software target is **PY32F071C1BU6**; F072 software support is not implemented yet.

## Hardware

KiCad sources and fabrication outputs are at the repository root and in `production/`.

## Software

The experimental Arduino core, PlatformIO platform, tools and examples live in [`software/`](software/README.md).

- [Arduino beginner guide](software/docs/ARDUINO-START.md)
- [PlatformIO beginner guide](software/docs/PLATFORMIO-START.md)
- [Schematic analysis and first-power instructions](software/docs/SCHEMATIC-ANALYSIS.md)
- [Hardware bring-up checklist](software/docs/BRINGUP.md)

**Before first power-on, read the jumper instructions: the fitted SN65HVD230 requires a 3.3 V supply.** Software is compile-tested, not yet hardware-validated.

Run software commands from `software/`, e.g. `cd software` before following either guide.
