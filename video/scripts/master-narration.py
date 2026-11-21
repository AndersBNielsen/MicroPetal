"""Loudness-master rendered narration without re-encoding its video."""
from pathlib import Path
import subprocess
import json
root=Path(__file__).resolve().parents[1]
source=root/'out/micropetal-explainer.mp4'
timeline=json.loads((root/'src/timeline.json').read_text())
duration=timeline['durationInFrames']/timeline['fps']
output=source.with_name('micropetal-explainer-mastered.mp4')
subprocess.run(['ffmpeg','-y','-v','error','-i',str(source),'-c:v','copy','-af',f'loudnorm=I=-16:TP=-1.5:LRA=7,apad,atrim=duration={duration}','-c:a','aac','-b:a','192k','-ar','48000','-t',str(duration),'-movflags','+faststart',str(output)],check=True)
output.replace(source)
