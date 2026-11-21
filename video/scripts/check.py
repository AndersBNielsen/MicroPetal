#!/usr/bin/env python3
"""Artifact checks: actual media timing/streams, caption bounds, and decode."""
import json, re, subprocess, wave
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def run(*args):
    return subprocess.run([str(a) for a in args],check=True,capture_output=True,text=True).stdout

def main():
    t = json.loads((ROOT/'src/timeline.json').read_text()); fps=t['fps']; cursor=0
    for s in t['scenes']:
        assert s['from']==cursor, 'Scene gap or overlap'
        with wave.open(str(ROOT/'public'/s['audio'])) as audio:
            duration=audio.getnframes()/audio.getframerate()
            assert abs(duration-s['durationInFrames']/fps)<1/48000
        end=0
        for c in s['captions']:
            assert c['start']>=end and c['end']>c['start'] and c['end']<=duration
            end=c['end']
        cursor += s['durationInFrames']
    assert cursor==t['durationInFrames']
    media=ROOT/'out/micropetal-explainer.mp4'
    probe=json.loads(run('ffprobe','-v','error','-show_streams','-show_format','-of','json',media))
    video=next(s for s in probe['streams'] if s['codec_type']=='video')
    audio=next(s for s in probe['streams'] if s['codec_type']=='audio')
    assert (video['width'],video['height'])==(t['width'],t['height'])
    assert video['codec_name']=='h264' and audio['codec_name']=='aac'
    assert int(video['nb_frames'])==cursor
    assert abs(float(probe['format']['duration'])-cursor/fps)<0.1
    assert abs(float(audio['duration'])-cursor/fps)<0.1
    run('ffmpeg','-v','error','-i',media,'-f','null','-')
    stats=subprocess.run(['ffmpeg','-i',str(media),'-af','volumedetect','-vn','-sn','-dn','-f','null','-'],capture_output=True,text=True,check=True).stderr
    levels=[line.strip() for line in stats.splitlines() if 'mean_volume:' in line or 'max_volume:' in line]
    mean=float(re.search(r'mean_volume: ([\-0-9.]+)',stats).group(1))
    peak=float(re.search(r'max_volume: ([\-0-9.]+)',stats).group(1))
    assert mean > -50, 'Narration is silent or too quiet'
    assert peak < 0, 'Possible clipping: inspect narration levels'
    for name in ['thumbnail.png','narration.wav','captions.srt','description.txt','script.md']+[f'scene-{s["id"]}.png' for s in t['scenes']]:
        assert (ROOT/'out'/name).stat().st_size>0
    report={'status':'pass','scenes':len(t['scenes']),'captions':sum(len(s['captions']) for s in t['scenes']),'durationSeconds':cursor/fps,'width':video['width'],'height':video['height'],'videoCodec':video['codec_name'],'audioCodec':audio['codec_name'],'voiceSource':t['voiceSource'],'levels':levels,'checks':['contiguous scene timeline','audio-measured caption bounds','frame count and duration','H.264/AAC 1080p streams','full decode without errors','publishing and review artifacts present'],'editorialReview':'Review six exported scene stills separately; synthetic voice quality needs human listening approval before publication.'}
    (ROOT/'out/qa.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
