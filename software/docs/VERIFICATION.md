# Verification — 21 November 2026

**10/10 compile checks pass.** Hardware results are recorded only in [BRINGUP.md](BRINGUP.md) (USB-HID upload of Blink verified 23 November 2026; other physical checks pending).

## Fresh-user install check — 24 November 2026

The release ZIP was extracted to an empty folder and installed exactly as the beginner guides say (`tools/install.py --sketchbook <empty sketchbook>`, then `--no-arduino`, then a second `--sketchbook` run), with a private PlatformIO core and Arduino CLI 1.1.1 as bundled with Arduino IDE 2 (macOS, Apple Silicon). Results:

- Installer: pinned toolchain, PlatformIO 6.1.19 and puyaisp 1.6.0 installed into `tools/.venv`; rerun preserved the old board install under `micropetal-backups`.
- Arduino: board listed as `micropetal:py32:micropetal_uno`; all six File → Examples → MicroPetal sketches and CompileSmoke compile with `--warnings all` and no warnings. Installed examples are identical to `examples/`.
- PlatformIO: shipped `examples/platformio`, `tests/platformio`, and a project per example in another folder using an absolute `symlink://` platform path all build.
- `tools/verify.py` against the fresh install: 10/10 PASS.
- Upload commands, captured with a recording stand-in for puyaisp (no USB access): `arduino-cli upload` with **no port** and `pio run -t upload` both run `<package>/tools/.venv/bin/puyaisp -t hid -f <build>.bin`.
- Arduino Blink, PlatformIO Blink and `firmware/Blink.bin` are byte-identical (SHA-256 `c7fb1461…a29d`), the binary that was uploaded to a board on 23 November.

`scripts/hw-test.sh` (repository only) repeats the uploads on hardware through both IDE paths and restores the previous flash contents afterwards.

## Compile checks — 21 November 2026

Host: macOS / Apple Silicon. Arduino CLI 1.6.0, PlatformIO 6.1.19, GCC Arm 12.3.1 (package 1.120301.0). No warning/error diagnostics in the final compile logs.

| Check | Result |
|---|---|
| 24 header mappings vs schematic XML and core table | PASS |
| 32 external IRQ slots vs F071 header | PASS (same mapping/vector check) |
| Arduino Blink | PASS |
| Arduino Button | PASS |
| Arduino AnalogSerial | PASS |
| Arduino Fade | PASS |
| Arduino I2CScanner | PASS |
| Arduino SPILoopback | PASS |
| Arduino CompileSmoke | PASS |
| PlatformIO Blink | PASS |
| PlatformIO CompileSmoke | PASS |

The mapping and IRQ assertions are one check; seven Arduino builds and two PlatformIO builds make ten checks total. CompileSmoke exercises linkage for UART Print/Stream/String (including floating-point String), ADC, DAC, PWM, Wire repeated START calls, SPI, GPIO interrupts, tone and random. It is **not** a safe first-run sketch and should not be used for board bring-up.

Blink: **2,788 bytes flash**, **220 bytes static RAM**. CompileSmoke: **34,684 bytes flash**, **1,460 bytes static RAM**. Limits: 131,072 / 16,384 bytes. Dynamic heap and stack are not represented by the static RAM count.

## Installation and uploader checks

- Ran installer against a separate `.install-test` sketchbook, preserving/replacing its previous installation. No changes to the user's actual IDE sketchbook/preferences.
- Compiled Arduino examples against that copied installation **without a compiler-path override**, exercising the generated `platform.local.txt`.
- Executed installed `puyaisp` 1.6.0 `--help`; confirmed HID `-t hid -f` syntax. No USB flash attempt was made.
- No GUI clicking, physical enumeration, timing/analog measurements, Windows or Linux installation test has been performed. Arduino IDE behavior is supported through its normal hardware-package recipes but verified here with Arduino CLI, not an IDE GUI session.

## Reproduce

Install the package into an isolated sketchbook with `tools/install.py --sketchbook /path/to/test-sketchbook`. Make a temporary Arduino CLI YAML config whose `directories.user` points at that sketchbook and whose data/download directories are suitable for that host. Then:

```sh
python3 tools/verify.py --arduino-cli /path/to/arduino-cli \
  --config-file /path/to/test-config.yaml --pio /path/to/pio
```

Logs and machine-readable results go under `build/verification`. To also check the repository CAD directly, export a temporary XML netlist and provide it explicitly (run from `software/`):

```sh
kicad-cli sch export netlist --format kicadxml --output /tmp/micropetal.net.xml ../MicroPetal_Uno.kicad_sch
python3 tools/check_hardware_mapping.py --netlist /tmp/micropetal.net.xml
```

Without a netlist, the checker verifies the retained expected mapping plus device vectors; the portable release ZIP excludes CAD. PCB pad mapping was additionally inspected locally; the duplicate schematic pin-35 inconsistency is documented separately.

Physical acceptance criteria: [BRINGUP.md](BRINGUP.md). Do not describe this release as hardware-tested until those results are recorded.
