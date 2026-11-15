# End screens — nine-episode Studio setup

**Status:** Each local MP4 ends with a **12-second baked visual canvas**, not clickable
YouTube elements. Nothing here proves a channel upload. A channel owner must add
actual Subscribe/Video/Playlist elements in YouTube Studio **after the target
video exists**, then preview and save. Do not paste imaginary video URLs.

## Visual zones (all full-length videos are 1920 × 1080)

| Element | Baked 1080p canvas | Approximate 2560 × 1440 editor coordinates |
|---|---|---|
| Subscribe circle | centre `(1490, 470)`, radius `120` | centre `(1987, 627)`, size `320 × 320` |
| Left video | `(222, 690)` to `(830, 985)` | X `296`, Y `920`, W `811`, H `393` |
| Right video | `(1090, 690)` to `(1698, 985)` | X `1453`, Y `920`, W `811`, H `393` |

These are visual guides derived from `scripts/build_video.py` (×4/3 scale), **not
numeric fields promised by Studio**. Use the editor's drag/preview controls
and keep the baked labels legible under the real interactive cards. Actual
Studio layouts and allowed element sizes can vary.

## Exact video timings and destinations

The canvas begins after all narrated scenes. Final mux/frame rounding can make
`MP4 duration − 12s` differ from the scene cut by a few frames. Studio uses
whole seconds: start at the **ceil of the scene cut**, not the truncated
chapter timestamp. `scripts/publish.py` computes this from recorded voice clips.

| Ep | MP4 length | Canvas starts | Studio start | Left video | Right video |
|---|---:|---:|---:|---|---|
| 1 | 03:56.28 | 03:44.20 | **03:45** | Existing 30-Day Money Reset, if live | Episode 2, after upload |
| 2 | 03:38.44 | 03:26.44 | **03:27** | Episode 1 | Episode 3, after upload |
| 3 | 03:40.88 | 03:28.88 | **03:29** | Episode 2 | Episode 4, after upload |
| 4 | 03:38.84 | 03:26.76 | **03:27** | Episode 3 | Episode 5, after upload |
| 5 | 03:59.88 | 03:47.88 | **03:48** | Episode 4 | Episode 6, after upload |
| 6 | 03:46.40 | 03:34.37 | **03:35** | Episode 5 | Episode 7, after upload |
| 7 | 03:55.88 | 03:43.87 | **03:44** | Episode 6 | Episode 8, after upload |
| 8 | 03:43.40 | 03:31.40 | **03:32** | Episode 7 | Episode 9, after upload |
| 9 | 03:58.96 | 03:46.96 | **03:47** | Episode 8 | Best for viewer; link next book only when actually live |

Right-hand cards in the videos are **suggestions, not embedded links**. If a
next episode is not published yet, add a live playlist/other suitable video,
or come back after it is available. Do not pretend the upcoming book is live.

## Do this in Studio for EACH long video

1. Review rights/terms for the intended use, then upload the MP4 and choose
   a visibility setting **after reviewing** the processed preview. Create the
   series playlist in episode order (1–9). None of this happens from Git.
2. Set Hindi language/captions (`out/deep-explains-babylon-niyam-N.hi.srt`),
   pick a 1280 × 720 JPG thumbnail and paste title/description/tags from
   `out/upload-N.md` (regenerate after obtaining real YouTube IDs).
3. In **Editor → End screen**, begin at the episode's **Studio start** above.
   Add the actual left video, right video and subscribe element; choose only
   live targets. The three drawn placeholder shapes alone do nothing.
4. Drag elements over the corresponding zones, preview on desktop and mobile,
   check titles/captions remain readable, then save. Verify the link targets
   and playback before publishing or scheduling.
5. Upload `out/short-N.mp4` **separately**. Shorts do not acquire these long-
   video end-screen elements automatically; its suggested title/description
   and link guidance are in the same `out/upload-N.md`.

To regenerate and check locally: `python3 scripts/publish.py --all` and
`python3 scripts/check_release.py`. The audit checks files/timing only; it
cannot verify a real Studio configuration, monetisation clearance or upload.
