"""Encode smaller, fast-start H.264/AAC copies for app review."""
import argparse
from pathlib import Path
import subprocess
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args()
root=Path(__file__).resolve().parents[1];args.output.mkdir(parents=True,exist_ok=True)
for source,name in [('out/micropetal-explainer.mp4','micropetal-narrated-v2.mp4'),('out/revision2/micropetal-song.mp4','micropetal-song-v2.mp4')]:
    target=args.output/name
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(root/source),'-vf','scale=1280:720:out_range=tv,format=yuv420p','-c:v','libx264','-preset','fast','-b:v','260k','-maxrate','400k','-bufsize','800k','-pix_fmt','yuv420p','-color_range','tv','-c:a','aac','-b:a','96k','-movflags','+faststart',str(target)],check=True)
    assert 0<target.stat().st_size<4_800_000,(name,target.stat().st_size)
    print(target,target.stat().st_size,flush=True)
