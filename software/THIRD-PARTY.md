# Source and licensing

Original MicroPetal glue, variant, platform, scripts, docs and examples: MIT (LICENSE). Third-party files retain their own licenses; the MIT license does not relicense them or the hardware CAD.

- ArduinoCore-API: https://github.com/arduino/ArduinoCore-API , commit in UPSTREAM.json. `cores/micropetal/api`: LGPL-2.1-or-later. Full corresponding source is included, along with the license; modifications can be rebuilt/relinked using the supplied recipes. No API sources were modified.
- Puya F07x HAL/CMSIS-device and linker template: https://github.com/IOsetting/py32f0-template , pinned in UPSTREAM.json. BSD-3-Clause notices retained per file. HAL configuration, memory layout/section flags and F071-specific startup vector selection are board-specific modifications. No F072 MCU identity is used in compilation.
- Arm CMSIS core headers: Apache-2.0 as marked per file, carried by the same SDK snapshot.
- Compiler: Arm GCC 12.3.1 via PlatformIO `toolchain-gccarmnoneeabi` 1.120301.0. Downloaded by installer, not redistributed here. Toolchain's own licenses apply.
- Uploader: https://github.com/wagiminator/MCU-Flash-Tools (`puyaisp` 1.6.0, installed by pip, not redistributed). PlatformIO 6.1.19 is likewise installed, not redistributed.
- Arduino CLI was used for local verification only, not included in the release ZIP.

The py32duino and regimantas Arduino-PY32 cores were inspected during preflight; their listed MCU support did not supply an F071 variant. Neither was copied into this package.

Hardware source remains under its owner's existing license (schematic title block CC BY-NC 4.0). CAD snapshots/netlists used for analysis are not included in the software release ZIP.
