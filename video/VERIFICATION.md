# First explainer verification — 2026-11-21

Rendered and checked locally with Remotion 4.0.545, macOS Daniel draft narration and FFmpeg. `npm run check` passes.

- 69.00 seconds; 2,070 frames; 1920×1080 at 30 fps.
- H.264 video, AAC audio; audio/video duration agreement within 0.1 seconds.
- Six contiguous scenes; twelve phrase captions measured from synthesized audio.
- Full MP4 decode completed without errors. Mean audio level −22.0 dB, peak −3.8 dB (not a broadcast loudness-mastering claim).
- All six scene review stills and the thumbnail were visually inspected: no observed text clipping or layout overlap.
- MP4, full narration WAV, SRT, thumbnail, six review stills, script and draft description generated. Machine-readable checks: `out/qa.json` after a build/check run.
- Current narration is a scratch track. Full human listening/editorial approval is still pending; word-level forced alignment is not implemented.
- No YouTube upload, paid service, account configuration, CAD edit or core edit was performed.

Run `npm run build && npm run check` from `video/` to regenerate. Generated output is ignored, not committed. The initial hardware/software claims use the baseline recorded in `content/SOURCES.md`; update them when physical bring-up results become available.

## Revision 2 narrated comparison

- Full build completed with Kokoro ONNX `bm_george` neural narration; the Mac `say` scratch voice is no longer the current voice.
- 99.6 seconds, 2,988 frames, H.264/AAC 1920×1080 at 30 fps. `npm run check` passes after loudness mastering. Mean audio −17.3 dB, peak −1.5 dB; source cue WAVs remain unmastered voice stems.
- Six rendered scene stills visually inspected. Twelve caption cues follow measured audio. Local base.en ASR screening recovered the comparison and all key narration claims; ASR is not a listening review.
- Current source explicitly distinguishes 72 MHz silicon rating from 8 MHz experimental core startup. 4× flash / 8× SRAM are capacity comparisons, not measured throughput claims.
- 720p H.264/yuv420p/AAC fast-start playback copies are derived from masters. Actual in-app playback and human voice-quality approval remain unverified.
- CAD and core unchanged; no publishing or paid service used.

## Revision 2 song alternative

- Separate 85-second 1080p H.264/AAC animated electro-pop edit; twelve editorial fact cards and beat-based motion, not a second audio track muxed onto the narrated edit.
- ACE-Step 1.5 turbo; original lyrics, seed328072, female-vocal second take. First take328071 rejected after ASR flagged missing chorus and mangled lines. Both WAV masters retained locally under ignored output directories.
- ASR of the selected take recovered both capacity hooks and most lines; it still flagged proper-name/word pronunciation and an outro omission. Singing quality and exact lyric compliance are **not certified**; listening review remains necessary.
- Full decode, stream/duration agreement and non-clipping checks in `out/revision2/song-qa.json`. No multi-second silence events in the raw selected audio; ending fade applied to the derived soundtrack. Twelve visual-card stills inspected; encoded contact sheet inspected separately.
- Original WAV, finished 1080p MP4 and smaller 720p app-review copy retained. Neither video has been published.
