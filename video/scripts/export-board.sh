#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
KICAD_CLI=${KICAD_CLI:-kicad-cli}
"$KICAD_CLI" pcb export svg --layers F.Cu,F.SilkS,Edge.Cuts \
  --page-size-mode 2 --exclude-drawing-sheet --mode-single \
  --output public/assets/board.svg ../MicroPetal_Uno.kicad_pcb
