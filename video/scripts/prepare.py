#!/usr/bin/env python3
"""Build audio-measured timing using local neural TTS or supplied recordings."""
import argparse, hashlib, json, math, os, shutil, subprocess, wave
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def run(*args):
    return subprocess.run([str(a) for a in args], check=True, capture_output=True, text=True).stdout

def seconds(path):
    with wave.open(str(path)) as audio:
        return audio.getnframes() / audio.getframerate()

def stamp(value):
    ms = round(value * 1000)
    return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--voice-dir', type=Path, help='Use <scene-id>-<cue-index>.wav recordings instead of Mac say')
    opts = parser.parse_args()
    episode = json.loads((ROOT/'content/episode.json').read_text())
    gen = ROOT/'public/generated'; gen.mkdir(parents=True, exist_ok=True)
    out = ROOT/'out'; out.mkdir(exist_ok=True)
    voice_source = 'recorded' if opts.voice_dir else 'macOS say (draft)'
    if not opts.voice_dir and episode.get('voiceEngine') == 'kokoro':
        models = os.environ.get('KOKORO_MODELS')
        python = os.environ.get('KOKORO_PYTHON')
        if not models or not python:
            raise SystemExit('Set KOKORO_MODELS and KOKORO_PYTHON for local neural TTS; see README.')
        subprocess.run([python, str(ROOT/'scripts/neural-voice.py'), '--models', models, '--voice', episode['voice']], check=True)
        opts.voice_dir = ROOT/'out/revision2/voice'
        voice_source = 'Kokoro ONNX / ' + episode['voice'] + ' (local neural synthetic voice)'
    fps = episode['fps']; cursor = 0; captions = []; scenes = []; scripts = []
    for scene in episode['scenes']:
        scene = dict(scene); cue_cursor = 0; chunks = []; cues = []
        for i, text in enumerate(scene['cues']):
            base = gen/f'{scene["id"]}-{i}'
            wav = base.with_suffix('.wav')
            fingerprint = hashlib.sha256(json.dumps([text,episode['voice'],episode['rate']]).encode()).hexdigest()
            cache = base.with_suffix('.sha256')
            if opts.voice_dir:
                shutil.copyfile(opts.voice_dir/f'{scene["id"]}-{i}.wav', base.with_suffix('.input.wav'))
                run('ffmpeg','-y','-v','error','-i',base.with_suffix('.input.wav'),'-ar','48000','-ac','1','-c:a','pcm_s16le',wav)
                cache.unlink(missing_ok=True)
            elif not (wav.exists() and cache.exists() and cache.read_text()==fingerprint):
                run('say','-v',episode['voice'],'-r',episode['rate'],'-o',base.with_suffix('.aiff'),text)
                run('ffmpeg','-y','-v','error','-i',base.with_suffix('.aiff'),'-ar','48000','-ac','1','-c:a','pcm_s16le',wav)
                cache.write_text(fingerprint)
            duration = seconds(wav)
            # One exact caption per synthesized/recorded cue. No invented word timestamps.
            cue = {'text':text,'start':cue_cursor,'end':cue_cursor+duration}
            cues.append(cue)
            captions.append({'text':text,'start':cursor/fps+cue_cursor,'end':cursor/fps+cue_cursor+duration})
            chunks.append(wav); cue_cursor += duration
        length = math.ceil((cue_cursor+episode['pauseSeconds'])*fps)
        audio = gen/f'{scene["id"]}.wav'
        with wave.open(str(audio),'wb') as target:
            target.setparams((1,2,48000,0,'NONE','not compressed'))
            for chunk in chunks:
                with wave.open(str(chunk)) as source:
                    target.writeframes(source.readframes(source.getnframes()))
            target.writeframes(b'\x00\x00'*round((length/fps-cue_cursor)*48000))
        scene.update({'from':cursor,'durationInFrames':length,'audio':f'generated/{audio.name}','captions':cues})
        scenes.append(scene); cursor += length
        scripts.append(f'## {scene["eyebrow"]}\n\n'+ ' '.join(scene['cues']))
    timeline = {**episode,'scenes':scenes,'durationInFrames':cursor,'voiceSource':voice_source}
    (ROOT/'src/timeline.json').write_text(json.dumps(timeline,indent=2)+'\n')

    with wave.open(str(out/'narration.wav'),'wb') as target:
        target.setparams((1,2,48000,0,'NONE','not compressed'))
        for scene in scenes:
            with wave.open(str(ROOT/'public'/scene['audio'])) as source:
                target.writeframes(source.readframes(source.getnframes()))

    (out/'captions.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{c["text"]}' for i,c in enumerate(captions))+'\n')
    (out/'script.md').write_text('# '+episode['title']+'\n\n'+'\n\n'.join(scripts)+'\n')
    description = episode['title']+'\n\nAn introduction to the MicroPetal Uno-format PY32 board. F071 is the initial target; F072 is a hardware option, not implemented software support.\n\nhttps://github.com/AndersBNielsen/MicroPetal\n\nBefore first power: follow software/docs/SCHEMATIC-ANALYSIS.md. JP3 needs the documented 3.3 V configuration for the fitted transceiver.\n\nStatus: software compile-tested; physical upload/runtime validation pending. Draft synthetic narration; PCB artwork exported from project CAD, not a board photograph.\n\n'
    for scene in scenes:
        sec = int(scene['from']/fps)
        description += f'{sec//60:02}:{sec%60:02} {scene["eyebrow"].title()}\n'
    (out/'description.txt').write_text(description)
    print(f'Prepared {len(scenes)} scenes, {len(captions)} measured captions, {cursor/fps:.2f}s. Voice: {timeline["voiceSource"]}')

if __name__ == '__main__': main()
