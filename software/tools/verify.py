#!/usr/bin/env python3
"""Compile both frontends and all examples. Does not access a board or upload firmware."""
import argparse,json,subprocess,sys,shutil
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--arduino-cli',default='arduino-cli');p.add_argument('--config-file',required=True);p.add_argument('--pio',default='pio');args=p.parse_args()
logs=root/'build/verification';logs.mkdir(parents=True,exist_ok=True);results=[]
def run(name,cmd):
 log=logs/(name+'.log')
 with log.open('w') as f:status=subprocess.run(cmd,cwd=root,stdout=f,stderr=subprocess.STDOUT).returncode
 results.append({'name':name,'passed':status==0,'log':str(log.relative_to(root))});print(('PASS ' if status==0 else 'FAIL ')+name,flush=True)
 if status:print(log.read_text()[-5000:])
run('pin-vector-map',[sys.executable,str(root/'tools/check_hardware_mapping.py')])
for sketch in sorted((root/'examples').glob('*/*.ino'))+[root/'tests/CompileSmoke/CompileSmoke.ino']:
 run('arduino-'+sketch.stem,[args.arduino_cli,'compile','--config-file',str(Path(args.config_file).resolve()),'--fqbn','micropetal:py32:micropetal_uno','--output-dir',str(root/'build'/('arduino-'+sketch.stem)),str(sketch.parent)])
for name,path in [('pio-Blink','examples/platformio'),('pio-CompileSmoke','tests/platformio')]:run(name,[args.pio,'run','-d',str(root/path)])
(logs/'results.json').write_text(json.dumps(results,indent=2)+'\n')
raise SystemExit(not all(x['passed'] for x in results))
