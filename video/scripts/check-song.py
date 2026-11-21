"""Verify rendered song streams, length, full decode, and audio levels."""
import json
from pathlib import Path
import re
import subprocess
root=Path(__file__).resolve().parents[1]
p=root/'out/revision2/micropetal-song.mp4'
def run(*args):
    return subprocess.run(list(map(str,args)),check=True,capture_output=True,text=True)
probe=json.loads(run('ffprobe','-v','error','-show_streams','-show_format','-of','json',p).stdout)
v=next(s for s in probe['streams'] if s['codec_type']=='video')
a=next(s for s in probe['streams'] if s['codec_type']=='audio')
assert (v['codec_name'],v['width'],v['height'])==('h264',1920,1080)
assert a['codec_name']=='aac'
assert abs(float(probe['format']['duration'])-85)<.1
assert abs(float(v['duration'])-float(a['duration']))<.1
stats=run('ffmpeg','-hide_banner','-i',p,'-af','silencedetect=n=-50dB:d=2,volumedetect','-f','null','-').stderr
peak=float(re.search(r'max_volume: ([\-0-9.]+)',stats).group(1))
assert peak<0, 'Possible clipped audio'
for i in range(12):
    assert (root/f'out/revision2/song-scene-{i}.png').stat().st_size > 0
report=dict(status='pass',durationSeconds=float(probe['format']['duration']),peakDb=peak,decode='full decode passed',silenceEvents=[s for s in stats.splitlines() if 'silence_' in s],listeningReview='Human listening still required; ASR is screening only.')
(root/'out/revision2/song-qa.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
