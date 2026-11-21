# MicroPetal software

- This is the canonical software directory inside the MicroPetal repository. Keep software here alongside the CAD; do not create a separate software project.
- The board accommodates F071 and F072. F071 is the initial target; the transceiver is for the F072 option. Do not imply F072 software support until implemented and verified.
- Target non-E PY32F071C1BU6; do not substitute F030/F072 device headers.
- Read docs/SCHEMATIC-ANALYSIS.md before hardware actions. JP3 default 5V conflicts with U4's 3.3V specification. No CAN controller on F071.
- Keep hardware and public website untouched unless separately requested.
- The platform/hardware symlink shares one Arduino core; release ZIP must dereference it for cross-platform extraction.
- After core/platform edits, run tools/check_hardware_mapping.py and tools/verify.py using an isolated installed Arduino sketchbook; see docs/VERIFICATION.md.
- Never upload the compile-only smoke sketch as a first-run example. Physical tests remain pending until recorded in docs/BRINGUP.md.
- Preserve third-party license notices. No secrets, host-specific configs, virtualenvs or upstream .git directories in release archives.
