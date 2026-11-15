# Asset provenance and rights handoff — Episodes 1–9

**Scope:** what this repository can establish locally. This is not a licence opinion, YouTube approval, or evidence of publication. Confirm any platform terms and channel-specific permissions **before** making a video public or monetising it.

| Asset | Local evidence | Remaining owner check |
|---|---|---|
| Book and script | Narration is a new paraphrase of George S. Clason's *The Richest Man in Babylon*. Sources and limitations are in the episode publish packs and `content/01-book-review.md`. | Confirm text/translation rights if any externally supplied translation, cover, or excerpt is introduced. Review financial claims/disclaimers personally. |
| Typography | The six bundled TTF files declare SIL OFL 1.1 in their embedded name tables. Copyright notices, licence text and upstream reference links are in `assets/fonts/README.md`. | Preserve OFL notices when distributing the font files. Recheck if replacing a font. |
| Narration | Recorded MP3 assets are under `assets/audio/` and `assets/audio/epN/`; Episode 2's corrected clips were synthesized for this project. The repository does **not** contain usage terms, consent records or an independent audit of every earlier voice clip. | Confirm the applicable voice-provider terms and any speaker/voice permissions for the intended commercial use. Do not assume that an AI voice is automatically cleared. |
| Visual art | Still images used by the renderers are under `assets/img/`. Project docs describe generated art, but no complete prompt/model/terms register or separate licence grant accompanies every image. | Confirm origin and current commercial-use terms for each image; replace anything whose rights cannot be established. Inspect videos/thumbnails for unintended logos or identifiable third parties. |
| Music and sound | Long-video beds are synthesized locally by `scripts/build_video.py:synth_music_safe` into ignored per-episode scratch; `scripts/build_short.py` mixes narration without that bed. The older tracked `assets/music/bed.mp3` is **not** the current long-video mix source. | Confirm the origin/rights of any replacement music or sound, and check the channel for Content ID claims after upload. Do not assume generation guarantees a claim-free track. |
| Output media | `out/deep-explains-babylon-niyam-N.mp4`, `out/short-N.mp4`, `.hi.srt`, thumbnails and `out/upload-N.md` are local files. `out/release-readiness.md` verifies technical package properties, not publication or licences. | Review the processed Studio preview, audience/visibility, clickable end-screen targets, captions and actual claim/rights status. |

## Owner sign-off (repeat before scheduling)

- [ ] Record the applicable narration and image provider terms/permissions for the upload date and intended use.
- [ ] Check each long video, Short and thumbnail for factual errors, third-party marks, faces and unsuitable or copyrighted material.
- [ ] Review the sources, calculations, financial disclaimer and audience setting in each episode's `out/upload-N.md`.
- [ ] Inspect YouTube's copyright/Content ID checks and processed preview; resolve issues before choosing public visibility.
- [ ] Keep the attached font notices with the font binaries and any redistributed source project.

The local audit cannot sign these boxes on the channel owner's behalf. No private YouTube credentials or imaginary publication IDs belong in Git.
