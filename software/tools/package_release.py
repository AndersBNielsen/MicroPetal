#!/usr/bin/env python3
"""Create a portable source release, no host paths/venvs/CAD or symlinks."""
from pathlib import Path
import zipfile,hashlib,json
ROOT=Path(__file__).resolve().parents[1];version='0.1.0';dist=ROOT/'dist';dist.mkdir(exist_ok=True)
files={}
def addtree(source,prefix):
 for p in source.rglob('*'):
  rel=p.relative_to(source)
  # Skip build output and host junk such as macOS .DS_Store.
  if p.is_file() and not any(x in rel.parts for x in ['.pio','__pycache__']) and not any(x.startswith('.') for x in rel.parts):files[str(Path(prefix)/rel)]=p.read_bytes()
# AGENTS.md is maintainer/agent guidance and is not shipped.
for name in ['README.md','LICENSE','THIRD-PARTY.md','UPSTREAM.json']:files[name]=(ROOT/name).read_bytes()
for name in ['docs','hardware','examples','tests']:addtree(ROOT/name,name)
# Dereference the development symlink explicitly. Windows users need no symlink privileges.
addtree(ROOT/'hardware','platform/hardware')
for name in ['platform.py','platform.json']:files['platform/'+name]=(ROOT/'platform'/name).read_bytes()
for name in ['builder','boards']:addtree(ROOT/'platform'/name,'platform/'+name)
for name in ['install.py','verify.py','check_hardware_mapping.py','package_release.py']:files['tools/'+name]=(ROOT/'tools'/name).read_bytes()
files['firmware/Blink.bin']=(ROOT/'examples/platformio/.pio/build/micropetal_uno/program.bin').read_bytes()
files['firmware/README.md']=b'Experimental F071C1BU6 / non-E Blink (D13 LED, 1 Hz). Source in examples/Blink. Written and readback-verified on one board via the factory USB-HID loader; LED timing not yet confirmed. Follow docs/ARDUINO-START.md (power/jumpers, J3 3-4 BOOT) and verify your board matches, then: tools/.venv/bin/puyaisp -t hid -f firmware/Blink.bin\n'
files['verification-results.json']=(ROOT/'build/verification/results.json').read_bytes()
manifest={name:hashlib.sha256(data).hexdigest() for name,data in files.items()}
files['SHA256SUMS.json']=(json.dumps(manifest,indent=2)+'\n').encode()
archive=dist/f'MicroPetal-Uno-R1-software-{version}.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for name,data in sorted(files.items()):z.writestr('MicroPetal-Uno-R1/'+name,data)
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for name,sha in manifest.items():assert hashlib.sha256(z.read('MicroPetal-Uno-R1/'+name)).hexdigest()==sha
 assert not any('upload-config.json' in n or '.venv/' in n or 'kicad' in n or '/.' in n or n.endswith('AGENTS.md') for n in z.namelist())
print(f'{archive}\n{len(files)} files; {archive.stat().st_size} bytes; SHA256 {hashlib.sha256(archive.read_bytes()).hexdigest()}')
