# Video production conventions

- Keep this workflow inside the MicroPetal repository. Do not edit CAD or the Arduino core for video work.
- Edit editorial content in `content/episode.json`; record evidence in `content/SOURCES.md`.
- F071 is the initial target. F072 is accommodated by the board, not implemented firmware support. Never imply physical validation before the bring-up record exists.
- Use project CAD artwork or real footage with known provenance. Label CAD exports as layout artwork, not photographs.
- Keep paid TTS, voice cloning and publishing opt-in. Default narration is local macOS `say`; recordings use the same cue interface.
- Caption timings must come from actual audio. Phrase timing is not word-level alignment.
- Keep generated media, dependencies, credentials and host-specific paths out of Git. Do not add a local .env file to a release.
- After changes, run `npm run build` and `npm run check`; inspect all six scene stills and review the whole voice track before publication. Preserve a clear distinction between automated checks and listening/editorial review.
- Existing tooling covers rendering (Remotion), conversions/checks (FFmpeg), and optional finishing (Final Cut Pro/Motion). Add dependencies only when needed.
