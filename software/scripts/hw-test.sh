#!/bin/bash
# MicroPetal Uno R1 hardware upload test: back up flash, upload Blink via the Arduino path,
# then via the PlatformIO path, then restore the previous (Firestarter) firmware.
#
# Run from the software/ directory of a checkout or extracted release:
#   scripts/hw-test.sh                 # interactive hardware run
#   scripts/hw-test.sh --dry-run       # install + builds + print upload commands; no USB access
# Options:
#   --out DIR            results directory (default: build/hw-test-<timestamp>)
#   --firestarter BIN    Firestarter image to restore (default: newest known bench image, see below)
#   --restore-backup     restore the exact pre-test backup instead of BIN + saved config
#   --serial SERIAL      ROM loader USB serial (default: require exactly one loader)
#   --arduino-cli PATH   default: Arduino IDE 2 bundled CLI, else arduino-cli on PATH
#
# Manual restore if this script is interrupted (J3 3-4 fitted, USB plugged, ROM HID present):
#   tools/.venv/bin/python scripts/hw_isp.py restore <OUT>                     # exact backup
#   tools/.venv/bin/python scripts/hw_isp.py restore <OUT> --image <BIN>       # image + saved config
#   or plain puyaisp (writes full 128 KiB backup incl. config, verifies, leaves option bytes alone):
#   tools/.venv/bin/puyaisp -t hid -f <OUT>/backup-flash.bin
# then unplug USB, remove the J3 3-4 shunt, reconnect.
set -euo pipefail
cd "$(dirname "$0")/.."
SW=$(pwd)
DRY=0; OUT=""; FS=""; RESTORE_BACKUP=0; SERIAL=""; ACLI=""
while [ $# -gt 0 ]; do case "$1" in
  --dry-run) DRY=1;; --out) OUT=$2; shift;; --firestarter) FS=$2; shift;;
  --restore-backup) RESTORE_BACKUP=1;; --serial) SERIAL=$2; shift;; --arduino-cli) ACLI=$2; shift;;
  -h|--help) sed -n 2,21p "$0"; exit 0;; *) echo "unknown option $1"; exit 2;; esac; shift; done
OUT=${OUT:-$SW/build/hw-test-$(date +%Y%m%d-%H%M%S)}; OUT=$(mkdir -p "$OUT" && cd "$OUT" && pwd)
exec > >(tee -a "$OUT/hw-test.log") 2>&1
BENCH=/Users/abn/.openclaw/workspace/output/bench
if [ -z "$FS" ]; then
  FS=$(ls -t "$BENCH"/micropetal-read-speed-20261124/firestarter*.bin "$BENCH"/micropetal-read-speed-20261124/*/firestarter*.bin 2>/dev/null | head -1 || true)
  FS=${FS:-$BENCH/micropetal-full-20261123/firestarter_micropetal_uno_mp3.bin}
fi
if [ -z "$ACLI" ]; then
  ACLI="/Applications/Arduino IDE.app/Contents/Resources/app/lib/backend/resources/arduino-cli"
  [ -x "$ACLI" ] || ACLI=$(command -v arduino-cli || true)
fi
[ -x "$ACLI" ] || { echo "arduino-cli not found; pass --arduino-cli"; exit 2; }
PY=$SW/tools/.venv/bin/python; PIO=$SW/tools/.venv/bin/pio
ISP=("$PY" "$SW/scripts/hw_isp.py"); [ -n "$SERIAL" ] && ISP+=(--serial "$SERIAL")
trap 'echo; echo "!!! Stopped with an error. If flash was already erased, restore manually (see header): $PY $SW/scripts/hw_isp.py restore $OUT"' ERR
step(){ echo; echo "=== $(date +%H:%M:%S) $*"; }
ask(){ [ $DRY = 1 ] && { echo "[dry-run] would ask: $1"; return 0; }; local r; read -r -p "$1 [y/N] " r </dev/tty; [[ $r =~ ^[Yy] ]]; }
must(){ ask "$1" || { echo "Stopped by operator."; exit 1; }; }
wait_rom(){ [ $DRY = 1 ] && { echo "[dry-run] would wait for ROM HID ffff:0448"; return; }; "${ISP[@]}" wait --timeout 90; }
echo "MicroPetal hardware upload test  out=$OUT  dry-run=$DRY"
echo "Firestarter restore image: $FS"; [ -f "$FS" ] && shasum -a 256 "$FS"

step "1. Install exactly as documented (isolated sketchbook; does not touch your Arduino IDE settings)"
mkdir -p "$OUT/sketchbook"
python3 tools/install.py --sketchbook "$OUT/sketchbook" > "$OUT/install.log" 2>&1 || { tail -20 "$OUT/install.log"; exit 1; }
tail -3 "$OUT/install.log"
printf 'directories:\n  data: %s/arduino15\n  downloads: %s/arduino15/staging\n  user: %s/sketchbook\n' "$OUT" "$OUT" "$OUT" > "$OUT/arduino-cli.yaml"
A=("$ACLI" --config-file "$OUT/arduino-cli.yaml"); FQBN=micropetal:py32:micropetal_uno
EX="$OUT/sketchbook/hardware/micropetal/py32/libraries/MicroPetal/examples"

step "2. Build: Arduino Blink (1 Hz) and PlatformIO Blink variant (4 Hz, own-project flow) so the two uploads are visually distinct"
"${A[@]}" compile -b $FQBN --output-dir "$OUT/arduino-Blink" "$EX/Blink" > "$OUT/arduino-compile.log" 2>&1 || { cat "$OUT/arduino-compile.log"; exit 1; }
P="$OUT/pio-blink4hz"; mkdir -p "$P/src"
printf '[env:micropetal_uno]\nplatform = symlink://%s/platform\nboard = micropetal_uno\nframework = arduino\n' "$SW" > "$P/platformio.ini"
sed 's/delay(500)/delay(125)/g' examples/platformio/src/main.cpp > "$P/src/main.cpp"
grep -q 'delay(125)' "$P/src/main.cpp" || { echo "could not make 4 Hz variant"; exit 1; }
(cd "$P" && "$PIO" run > "$OUT/pio-build.log" 2>&1) || { tail -30 "$OUT/pio-build.log"; exit 1; }
shasum -a 256 "$OUT/arduino-Blink/Blink.ino.bin" "$P/.pio/build/micropetal_uno/program.bin"
echo "Arduino upload recipe:"; "${A[@]}" compile -b $FQBN --show-properties "$EX/Blink" 2>/dev/null | grep -E '^tools\.puyaisp\.(cmd|upload\.pattern)='
echo "PlatformIO uploader: $(cat platform/upload-config.json)"

if [ $DRY = 1 ]; then
  step "dry-run: hardware steps that would follow"
  cat <<EOF
  [operator] Firestarter shield OFF (Blink toggles D13); USB unplugged; fit J3 3-4 (BOOT0-VCC); plug USB
  ${ISP[*]} wait --timeout 90
  ${ISP[*]} backup $OUT
  ${ACLI} --config-file $OUT/arduino-cli.yaml upload -v -b $FQBN --input-dir $OUT/arduino-Blink $EX/Blink
  [operator] LED 1 Hz?  tap RST (shunt still fitted)
  (cd $P && $PIO run -t upload -v)
  [operator] LED 4 Hz?  tap RST
  ${ISP[*]} restore $OUT --image $FS      (or: ${ISP[*]} restore $OUT)
  [operator] unplug USB, remove J3 3-4, refit shield, reconnect; check Firestarter CDC port + version
EOF
  exit 0
fi

step "3. Prepare board"
echo "This ERASES the MicroPetal flash (Firestarter will be restored at the end)."
must "Firestarter work finished, no other program using the board (Firestarter CLI/serial monitor closed)?"
must "Firestarter shield REMOVED (Blink toggles D13; do not run it with the shield fitted)?"
must "USB unplugged, then J3 pins 3-4 shunted (BOOT0-VCC, never 5-6), then USB plugged back in?"
wait_rom

step "4. Back up full 128 KiB flash + option bytes"
"${ISP[@]}" backup "$OUT"
if [ -f "$FS" ]; then "${ISP[@]}" check-image "$OUT" "$FS" || echo "NOTE: board was not running $FS exactly; consider --restore-backup at the end."; fi
echo "(Tap RST with the shunt still fitted so the loader starts from a clean state.)"
must "Tapped RST (J3 3-4 still fitted)?"; wait_rom

step "5. Arduino path upload (arduino-cli upload == IDE Upload button recipe, no port selected)"
"${A[@]}" upload -v -b $FQBN --input-dir "$OUT/arduino-Blink" "$EX/Blink" 2>&1 | tee "$OUT/arduino-upload.log" || true
grep -q 'bytes written and verified' "$OUT/arduino-upload.log" || { echo "Arduino upload did not report write+verify"; ARD=FAIL; }
ARD=${ARD:-PASS}
ask "Green LED blinking ~1 Hz (500 ms on / 500 ms off, active-low, may be faint)?" && ARD_LED=yes || ARD_LED=no
must "Tap RST (J3 3-4 still fitted) to re-enter the loader. Done?"; wait_rom

step "6. PlatformIO path upload (pio run -t upload)"
(cd "$P" && "$PIO" run -t upload -v) 2>&1 | tee "$OUT/pio-upload.log" || true
grep -q 'bytes written and verified' "$OUT/pio-upload.log" || { echo "PlatformIO upload did not report write+verify"; PIOR=FAIL; }
PIOR=${PIOR:-PASS}
ask "Green LED now blinking FASTER, ~4 Hz?" && PIO_LED=yes || PIO_LED=no
must "Tap RST (J3 3-4 still fitted) to re-enter the loader for restore. Done?"; wait_rom

step "7. Restore Firestarter"
if [ $RESTORE_BACKUP = 1 ] || [ ! -f "$FS" ]; then "${ISP[@]}" restore "$OUT"
elif "${ISP[@]}" check-image "$OUT" "$FS" >/dev/null; then "${ISP[@]}" restore "$OUT" --image "$FS"
elif ask "Backup differs from $FS. Restore the exact pre-test backup instead (recommended)?"; then "${ISP[@]}" restore "$OUT"
else "${ISP[@]}" restore "$OUT" --image "$FS"; fi

step "8. Finish"
echo "Now: unplug USB, REMOVE the J3 3-4 shunt, refit the Firestarter shield (socket empty), reconnect USB."
must "Done?"
sleep 3; ls /dev/cu.usbmodem* 2>/dev/null && echo "Firestarter CDC port present (not opened by this script)." || echo "No CDC port yet - check shunt removed, replug."
echo "Query the firmware version with the usual Firestarter CLI before continuing bench work."
cat > "$OUT/result.json" <<EOF
{"arduino_upload":"$ARD","arduino_led_1hz":"$ARD_LED","pio_upload":"$PIOR","pio_led_4hz":"$PIO_LED","restore":$(cat "$OUT/restore.json"),"out":"$OUT"}
EOF
cat "$OUT/result.json"
