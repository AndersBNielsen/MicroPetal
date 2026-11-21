"""Generate replaceable neural narration cues using existing Kokoro ONNX assets."""
import argparse
import hashlib
import json
from pathlib import Path
import soundfile as sf
from kokoro_onnx import Kokoro

parser = argparse.ArgumentParser()
parser.add_argument('--models', type=Path, required=True)
parser.add_argument('--voice', default='bm_george')
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
out = root/'out/revision2/voice'
out.mkdir(parents=True, exist_ok=True)
kokoro = Kokoro(str(args.models/'kokoro-v1.0.onnx'), str(args.models/'voices-v1.0.bin'))
for scene in json.loads((root/'content/episode.json').read_text())['scenes']:
    for i, text in enumerate(scene['cues']):
        target = out/f'{scene["id"]}-{i}.wav'
        cache = target.with_suffix('.sha256')
        fingerprint = hashlib.sha256((text + args.voice + '1.06').encode()).hexdigest()
        if target.exists() and cache.exists() and cache.read_text() == fingerprint:
            continue
        samples, rate = kokoro.create(text, voice=args.voice, speed=1.06, lang='en-gb')
        sf.write(target, samples, rate)
        cache.write_text(fingerprint)
        print(scene['id'], i, len(samples)/rate, flush=True)
