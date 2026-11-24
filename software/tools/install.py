#!/usr/bin/env python3
"""Install local Arduino board support and USB-HID uploader; preserve prior installs."""
import argparse,json,os,shutil,subprocess,sys,venv
from pathlib import Path
from datetime import datetime
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--sketchbook',type=Path,help='Arduino IDE sketchbook location shown in Preferences')
parser.add_argument('--no-arduino',action='store_true',help='Install tools for PlatformIO only')
args=parser.parse_args()
if not args.no_arduino and not args.sketchbook:
 parser.error('Supply --sketchbook with the location shown in Arduino IDE Preferences, or --no-arduino for PlatformIO only.')
v=ROOT/'tools/.venv'
if not v.exists():venv.EnvBuilder(with_pip=True).create(v)
bin=v/('Scripts' if os.name=='nt' else 'bin');python=bin/('python.exe' if os.name=='nt' else 'python')
subprocess.run([str(python),'-m','pip','install','platformio==6.1.19','puyaisp==1.6.0'],check=True)
pio=bin/('pio.exe' if os.name=='nt' else 'pio');uploader=bin/('puyaisp.exe' if os.name=='nt' else 'puyaisp')
# Reuse an existing compatible toolchain, otherwise let PIO choose a host-specific package.
piohome=Path(os.environ.get('PLATFORMIO_CORE_DIR',str(Path.home()/'.platformio')))
toolchain=piohome/'packages/toolchain-gccarmnoneeabi'
subprocess.run([str(pio),'pkg','install','--global','--tool','platformio/toolchain-gccarmnoneeabi@~1.120301.0'],check=True)
if not (toolchain/'bin').is_dir():raise SystemExit('Toolchain location not found: '+str(toolchain))
(ROOT/'platform/upload-config.json').write_text(json.dumps({'uploader':str(uploader)}))
if not args.no_arduino:
 target=args.sketchbook.expanduser().resolve()/'hardware/micropetal/py32'
 if target.exists():
  backup=target.with_name('py32-backup-'+datetime.now().strftime('%Y%m%d-%H%M%S'))
  # Put backup outside hardware so Arduino does not discover duplicate platforms.
  backup=args.sketchbook.expanduser().resolve()/'micropetal-backups'/backup.name
  backup.parent.mkdir(parents=True,exist_ok=True);shutil.move(str(target),str(backup));print('Previous install preserved at',backup)
 shutil.copytree(ROOT/'hardware/micropetal/py32',target)
 (target/'platform.local.txt').write_text('compiler.path='+toolchain.as_posix()+'/bin/\ntools.puyaisp.cmd='+uploader.as_posix()+'\n')
 print('Arduino board installed at',target,'\nRestart Arduino IDE; choose MicroPetal Uno R1.')
print('PlatformIO tools:',bin,'\nUSB-HID uploader:',uploader)
