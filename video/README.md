# MicroPetal explainer production

A local, repeatable **script → narration → timed React animations → MP4 + captions + thumbnail + description** workflow. Current episode: approximately 100 seconds, English, 1920×1080 at 30 fps; plus an 85-second original song edit.

## Run

Requirements: Node.js 22+, Python 3, FFmpeg/ffprobe, Google Chrome, a separate Kokoro ONNX environment for neural voice (see Revision 2). No paid service or cloud account is used. Dependencies are pinned in `package-lock.json`.

```sh
cd video
npm ci
npm run build
npm run check
# Optional interactive editing/preview:
npm run studio
```

Outputs are in `out/`: `micropetal-explainer.mp4`, `narration.wav` (full-length voice stem), `captions.srt`, `thumbnail.png`, `description.txt` (including chapter timestamps), `script.md`, six scene stills and `qa.json`. Generated media, caches and dependencies are intentionally ignored by Git. `CHROME_PATH` overrides the render browser path. On non-macOS, supply recorded WAVs as below and set `CHROME_PATH`.

## Edit the next episode

1. Verify claims against project CAD, device documentation and bring-up results. Record them in `content/SOURCES.md`.
2. Edit `content/episode.json`: title, scene text, narration cues, labels, voice and speaking rate. This is the single editorial source. The scene layouts (`board`, `targets`, `code`, `pins`, `power`) live in `src/index.tsx`.
3. Run `npm run narrate`. Audio is cached by text/voice/rate hash. Every narration cue is synthesized separately and measured; captions use those exact cue boundaries. These are **phrase-level timestamps, not word-level alignment**.
4. Preview with `npm run studio`. Run `npm run render` for the final MP4 and thumbnail. The render also emits a still from every scene for editorial checking.
5. Run `npm run check`, watch/listen to the entire MP4, review pronunciations, then import into Final Cut Pro, Motion, Resolve or another editor if desired. The MP4 audio and SRT are portable; no editor-specific project is required.
6. Upload manually only after editorial approval. `description.txt` is a draft. No uploader, scheduled publishing or account connection is installed.

The first episode's scene set is deliberately hardware-specific; a new subject may need a new React panel, not just replacement labels. All scene/thumbnail generation is programmatic. No generated bitmap assets or borrowed video footage are required.

## Replace the draft voice

The first draft used the built-in Daniel scratch voice. The current edit uses Kokoro neural narration; neither is a voice clone or a claimed match for any creator. For your own narration, record/export one WAV for each cue, named `intro-0.wav`, `intro-1.wav`, `targets-0.wav`, etc. See scene IDs and cue order in `content/episode.json`.

```sh
python3 scripts/prepare.py --voice-dir /absolute/path/to/recordings
npm run render
npm run check
```

Recordings are normalized to mono 48 kHz PCM and remeasured. The animation timeline and captions follow the new durations. Keep each recording's wording identical to its corresponding cue (or update the cue text). The current Kokoro neural TTS provides the same cue files. No ElevenLabs credentials were requested, no credits spent, and no paid subscription is required. True word highlighting would require forced alignment or provider timestamps; it is not faked here.

## PCB asset provenance

`public/assets/board.svg` is exported from the repository PCB, not a photograph and not a representation of an assembled unit. Regenerate without modifying CAD:

```sh
kicad-cli pcb export svg --layers F.Cu,F.SilkS,Edge.Cuts \
  --page-size-mode 2 --exclude-drawing-sheet --mode-single \
  --output public/assets/board.svg ../MicroPetal_Uno.kicad_pcb
```

The JP3 animation is an electrical connection diagram, **not physical pad orientation**. Follow the hardware guide for actual work. No hardware or core implementation is changed by this video project.

## Stack and scope

Existing-tool preflight selected [Remotion](https://www.remotion.dev/docs/) for reusable React scenes and [FFmpeg](https://ffmpeg.org/) for audio conversion and media checks. [Remotion licensing](https://www.remotion.dev/docs/license) must remain applicable to the organization using it; no license or paid plan was purchased. Existing Final Cut Pro and Motion can serve as optional final-edit tools; no need to install Resolve or Manim for this episode.

This is an original technical explainer inspired by a described high-throughput workflow. Kai's actual tools, production cadence and use of AI were **not verified**. Research, scripts and public claims require editorial review; publishing remains manual. Missing production-quality pieces are a final human voice/listening pass, optional real board footage after arrival, and hardware demonstration once validated. There are no invented benchmark numbers or implied successful physical tests.

## Revision 2 — comparison + original song

The current episode is a ~100-second humorous ATmega328P comparison. `content/episode-v1.json` preserves the first script. Visuals use an exported PNG of the actual project PCB to keep rendering fast; the SVG remains the source. Regenerate PNG with `rsvg-convert -w 1000 -o public/assets/board.png public/assets/board.svg`.

Local neural narration uses [Kokoro ONNX](https://github.com/thewh1teagle/kokoro-onnx), stock `bm_george` voice (not a voice clone). Create a separate Python 3.12 venv, install `kokoro-onnx==0.6.1 soundfile`, and download the model/voice files per upstream instructions. Set `KOKORO_PYTHON` to that venv's Python and `KOKORO_MODELS` to the model directory, then `npm run build && npm run check`. Alternatively use the existing `--voice-dir` interface with recordings. No paid TTS fallback is configured.

`content/song.toml` contains original lyrics, style, seed and generation settings for the installed ACE-Step 1.5 turbo. Run it through ACE-Step's `cli.py --config`, supplying your **existing** checkpoint directory and absolute output directory in a generated runtime config outside Git. Keep `thinking=false` and all `use_cot_*` flags false to avoid old `instruction.txt` prompt reuse. Do not auto-download a second checkpoint set in this repository. Copy the resulting 85-second WAV to `public/generated/song.wav`, retaining the original master; apply a two-second ending fade to the derived copy. `node scripts/render-song.mjs` renders a separate 85-second animated song edit with twelve visual cards and beat-based motion. The bars are designed animation, not a measured audio spectrum; cards are not synchronized lyric captions. Keep the Song composition duration consistent if regenerating with a different audio length.

Key editorial constraint: **128 KB vs 32 KB flash, 16 KB vs 2 KB SRAM** are chip capacities. 72 MHz is the PY32F071 chip rating; **current experimental core startup is 8 MHz**. These are not measured speed results. DMA is hardware capability, not an implemented Arduino DMA API. Both edits retain the F071/F072 and physical-validation status distinction.

Review outputs and vocals before publication. ASR is only a screening tool, not proof of lyric fidelity or voice quality. Nothing is uploaded automatically.

For a portable local ACE-Step launch, set `ACE_STEP_ROOT` to its installed checkout and run `python3 scripts/generate-song.py`. This creates a host-specific runtime config only under ignored `out/`, with explicit existing checkpoints. Check the music render with `python3 scripts/check-song.py`.
