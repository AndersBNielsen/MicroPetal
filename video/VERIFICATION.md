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
