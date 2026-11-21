# MicroPetal explainer production

A local, repeatable **script → narration → timed React animations → MP4 + captions + thumbnail + description** workflow. First episode: approximately 69 seconds, English, 1920×1080 at 30 fps.

## Run

Requirements: Node.js 22+, Python 3, FFmpeg/ffprobe, Google Chrome, macOS `say` for draft voice. No paid service or cloud account is used. Dependencies are pinned in `package-lock.json`.

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

The built-in Daniel voice is a **scratch track**, not a voice clone or a claimed match for any creator. For your own narration, record/export one WAV for each cue, named `intro-0.wav`, `intro-1.wav`, `targets-0.wav`, etc. See scene IDs and cue order in `content/episode.json`.

```sh
python3 scripts/prepare.py --voice-dir /absolute/path/to/recordings
npm run render
npm run check
```

Recordings are normalized to mono 48 kHz PCM and remeasured. The animation timeline and captions follow the new durations. Keep each recording's wording identical to its corresponding cue (or update the cue text). External TTS can provide the same cue files later. No ElevenLabs credentials were requested, no credits spent, and no paid subscription is required. True word highlighting would require forced alignment or provider timestamps; it is not faked here.

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
