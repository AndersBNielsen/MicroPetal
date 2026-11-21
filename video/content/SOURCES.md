# Episode fact sheet and sources

Reviewed 2026-11-21. Hardware/software baseline: commit `aac78d00f8a6a22d707f618e8768e87cb3ba26a4` of this repository. This is a concise overview, not a replacement for first-power or flashing instructions.

| Claim | Evidence |
| --- | --- |
| Uno-format PY32 board; F071 initial target, F072 accommodated | Root `README.md`, schematic and user clarification, 2026-11-21 |
| F072 firmware not implemented | `software/AGENTS.md`, `software/docs/SCHEMATIC-ANALYSIS.md` |
| Experimental Arduino core / PlatformIO support | `software/README.md`, `software/docs/VERIFICATION.md` |
| Active-low LED, UART D2 TX/D0 RX, dedicated I²C pins | `software/docs/SCHEMATIC-ANALYSIS.md`, checked schematic/PCB mapping |
| JP3 defaults 5 V; fitted SN65HVD230 requires 3.3 V configuration | `software/docs/SCHEMATIC-ANALYSIS.md`; [TI transceiver datasheet](https://www.ti.com/lit/ds/symlink/sn65hvd230.pdf) |
| Software checks passed, physical validation pending | `software/docs/VERIFICATION.md`, `software/docs/BRINGUP.md` |
| Board visual | Front copper/silkscreen/outline export of `MicroPetal_Uno.kicad_pcb` |

No claims are made about price, measured performance, shield compatibility beyond physical format, actual assembled-board operation, or F072 firmware readiness. The F071 does not have a CAN controller; the existing transceiver is for the F072 option. The script does not imply that F071 gains CAN from a transceiver.

Workflow references: [Remotion rendering](https://www.remotion.dev/docs/renderer/render-media), [composition selection](https://www.remotion.dev/docs/renderer/select-composition), [license](https://www.remotion.dev/docs/license). Exact dependencies are locked locally.

Creator inspiration: user-supplied description of “I ran Qwen3.8 27B on $78 Card! (Better than expected)”. No footage or identifiable creator likeness/voice was used. The title alone is insufficient to verify the creator's actual production tools; the supplied workflow remains a hypothesis.

## Revision 2: comparison, humor and music (2026-11-21)

- Puya PY32F071 datasheet: https://www.puyasemi.com/download_path/%E6%95%B0%E6%8D%AE%E6%89%8B%E5%86%8C/MCU%20%E5%BE%AE%E5%A4%84%E7%90%86%E5%99%A8/PY32F071_Datasheet_V0.8.pdf — Cortex-M0+, max 72 MHz; C1B target 128 KB flash / 16 KB SRAM, DMA. Capacities agree with project board manifest. Not measured board performance.
- Arduino Uno Rev3: https://docs.arduino.cc/hardware/uno-rev3/ and https://docs.arduino.cc/resources/datasheets/A000066-datasheet.pdf — ATmega328P, 16 MHz board clock, 32 KB flash / 2 KB SRAM. 4× and 8× refer to capacity, not speed.
- Project platform/boards/micropetal_uno.json and cores/micropetal/system_py32f07x.c: experimental core f_cpu and HSI startup are **8 MHz**, not 72 MHz. No implied tested 72 MHz configuration.
- DMA is a chip capability, not an implemented Arduino API or hardware-validated feature. F071 first; F072 option only. No price or power superiority claim.
- Neural TTS: https://github.com/thewh1teagle/kokoro-onnx (MIT wrapper, Apache-2.0 Kokoro model). Stock bm_george voice, not a cloned person.
- Original song lyrics in song.toml; generated with installed ACE-Step 1.5 turbo, seed 328072 (first take 328071 rejected after ASR screening), no LM rewriting. Song capacities are the same documented comparison.
