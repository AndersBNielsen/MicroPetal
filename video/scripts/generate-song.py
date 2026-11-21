"""Run the installed ACE-Step with explicit paths; never duplicate model downloads."""
import os
from pathlib import Path
import subprocess
import tomllib

root = Path(__file__).resolve().parents[1]
ace = Path(os.environ['ACE_STEP_ROOT']).expanduser().resolve()
assert (ace/'checkpoints/acestep-v15-turbo').exists(), 'Existing turbo checkpoint required'
source = (root/'content/song.toml').read_text()
config = tomllib.loads(source)
output = root/'out/revision2/song'
output.mkdir(parents=True, exist_ok=True)
source = source.replace('save_dir = "'+config['save_dir']+'"', 'save_dir = "'+str(output)+'"')
source += '\ncheckpoint_dir = "'+str(ace/'checkpoints')+'"\nproject_root = "'+str(ace)+'"\n'
runtime = root/'out/revision2/song-run.toml'
runtime.write_text(source)
subprocess.run([str(ace/'.venv/bin/python'), str(ace/'cli.py'), '--config', str(runtime)], cwd=ace, check=True)
