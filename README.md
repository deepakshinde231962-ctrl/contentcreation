# Deep Explains — Content Engine 🎬

Hinglish money-book series ka **research → 550–650-word script → narration assets → video → Shorts → publish kit**.
**Rendered videos are reproducible locally** with Python + ffmpeg from the committed MP3 narration clips;
recording *new* narration needs a voice service. YouTube upload and clickable end-screen elements
need channel access; the baked end-screen canvas by itself is not clickable.

**Series:** *The Richest Man in Babylon* (George S. Clason, 1926). The episode numbers are our **series order**, not necessarily the book's numbered cures or laws. Original paraphrases only.

| Episode | Theme | Final video | Short | SRT | Thumbnails |
|---|---|---|---|---|---|
| 1 | पहले खुद को दो | 3:56 · `out/deep-explains-babylon-niyam-1.mp4` | `out/short-1.mp4` | `out/deep-explains-babylon-niyam-1.hi.srt` | `out/thumbnail-{A,B,C}-1280x720.jpg` |
| 2 | ख़र्चे काबू में | 3:32 · `out/deep-explains-babylon-niyam-2.mp4` | `out/short-2.mp4` | `out/deep-explains-babylon-niyam-2.hi.srt` | `out/thumbnail-niyam2-{A,B,C}-1280x720.jpg` |
| 3 | पैसा पैसा कमाए | 3:41 · `out/deep-explains-babylon-niyam-3.mp4` | `out/short-3.mp4` | `out/deep-explains-babylon-niyam-3.hi.srt` | `out/thumbnail-niyam3-{A,B,C}-1280x720.jpg` |
| 4 | पैसा बचाओ, खो मत दो | 3:38 · `out/deep-explains-babylon-niyam-4.mp4` | `out/short-4.mp4` | `out/deep-explains-babylon-niyam-4.hi.srt` | `out/thumbnail-niyam4-{A,B,C}-1280x720.jpg` |
| 5 | कर्ज़ से आज़ादी (दबासीर) | 3:59.96 · `out/deep-explains-babylon-niyam-5.mp4` | `out/short-5.mp4` | `out/deep-explains-babylon-niyam-5.hi.srt` | `out/thumbnail-niyam5-{A,B,C}-1280x720.jpg` |
| 6 | घर: ख़र्च या निवेश? | 3:46.40 · `out/deep-explains-babylon-niyam-6.mp4` | `out/short-6.mp4` · 29.3s | `out/deep-explains-babylon-niyam-6.hi.srt` · 65 cues | `out/thumbnail-niyam6-{A,B,C}-1280x720.jpg` |
| 7 | बुढ़ापे की कमाई | 3:55.88 · `out/deep-explains-babylon-niyam-7.mp4` | `out/short-7.mp4` · 26.5s | `out/deep-explains-babylon-niyam-7.hi.srt` · 74 cues | `out/thumbnail-niyam7-{A,B,C}-1280x720.jpg` |
| 8 | खुद को बड़ा बनाओ | 3:43.40 · `out/deep-explains-babylon-niyam-8.mp4` | `out/short-8.mp4` · 26.3s | `out/deep-explains-babylon-niyam-8.hi.srt` · 69 cues | `out/thumbnail-niyam8-{A,B,C}-1280x720.jpg` |
| 9 | Five Laws of Gold · finale | **Script done; full video pending narration** | pending | pending | art prepared |

All long videos: 1920×1080/25 fps, mixed AAC 48 kHz audio, 12-second baked end-screen canvas.
Shorts: 1080×1920/30 fps with the same palette and original narrations.

## Publish-ready content

- `content/01-book-review.md` — book review, limitations and source audit.
- `content/13-episode5-script.md` — Episode 5's six-part, 610-word readable script;
  `video/episode05.py` is the single source of truth for timing, text, cards, and soundtrack.
- `content/14-episode5-publish-pack.md` — Episode 5 titles (<60 characters), thumbnails,
  Short idea, chapters, disclaimer, sources, pinned comment, channel-style description.
  Earlier episodes: `content/08-publish-pack.md`, `content/10-episode2-publish-pack.md`,
  `content/11-episode3-publish-pack.md`, `content/12-episode4-publish-pack.md`.
- `content/15-episode6-script.md`, `content/17-episode7-script.md`,
  `content/19-episode8-script.md` — complete six-part scripts. `video/remaining_content.py`
  stores exact spoken words for Episodes 6–9. The finale's script is
  `content/21-episode9-script.md`; its video is not complete yet.
- `content/16-episode6-publish-pack.md`, `content/18-episode7-publish-pack.md`,
  `content/20-episode8-publish-pack.md` — title options, sources,
  chapters, disclaimer, Short idea and end-screen instructions for Episodes 6–8.
- `out/upload-{1,2,3,4,5,6,7,8}.md` — one-page paste-ready sheet per finished episode
  (title, description, tags, pinned comment, captions and exact end-screen timer).
- `content/07-end-screen.md` — clickable element positions and Studio setup.
- `content/03-series-plan.md`, `content/04-channel-strategy.md` — rollout, measurement,
  and monetisation/policy safeguards.

**Important:** Without uploaded video IDs, description links fall back to the channel's playlist page;
there are no invented or dead YouTube video URLs. `links.json` (local, gitignored) or `EP1_ID`…`EP9_ID`
can supply real IDs after upload. Source clips/assets and the video deliverables are in Git;
`out/_work/` is a regenerable render scratch folder and ignored.

## Build / verify

```bash
python3 -m pip install pillow numpy scipy imageio-ffmpeg
python3 -m unittest discover -s tests -v

# Episode 5 — other episodes use episode02.py ... episode04.py
python3 scripts/build_video.py --episode video/episode05.py --stills
python3 scripts/build_video.py --episode video/episode05.py
python3 scripts/make_captions.py --episode video/episode05.py \
  --out out/deep-explains-babylon-niyam-5.hi.srt
python3 scripts/make_thumbnail.py A B C --episode video/episode05.py
python3 scripts/build_short.py --short video/short5.py
python3 scripts/publish.py 5

# Episodes 6–8 (replace 6 with 7 or 8; committed narration MP3s are enough).
# Compact H.264 keeps the 1080p deliverable small enough for Git.
DEEP_BUILD_PRESET=veryfast DEEP_COMPACT=1 python3 scripts/build_video.py --episode video/episode06.py
python3 scripts/make_captions.py --episode video/episode06.py \
  --out out/deep-explains-babylon-niyam-6.hi.srt
python3 scripts/make_thumbnail.py A B C --episode video/episode06.py
DEEP_BUILD_PRESET=veryfast DEEP_COMPACT=1 python3 scripts/build_short.py --short video/short6.py
python3 scripts/build_remaining_docs.py 6
python3 scripts/publish.py 6

# Optional: point a specific episode to its real uploaded YouTube ID
EP4_ID=YOUR_UPLOADED_VIDEO_ID python3 scripts/publish.py 5
# or set links.json locally from links.example.json, then:
python3 scripts/make_links.py --block 5
```

Episodes 6–9 use `video/remaining_content.py` (exact script) and
`video/remaining_storyboards.py` (scenes, voice-derived captions, cards, end screen),
wrapped by `video/episode0N.py`. `assets/audio/epN/narr_*.mp3` contains one spoken
clip per scene. The same timing source drives burned captions and external `.srt`;
`video/remaining_shorts.py` aligns the vertical beats to those clips. `out/_work/`
contains *ignored temporary TTS halves*; the committed scene MP3s and art are enough
to reproduce finished videos locally. All art uses generated stills; music is
synthesized by the renderer, not taken from a commercial track.
Typography uses Pillow/libraqm for Devanagari shaping; video assembly uses `imageio-ffmpeg`.

## Episode 5: accuracy notes

The story is **fiction**, not an actual Babylonian archaeological finding. Clason's Dabasir
plan is **10% savings + 20% repaid to all creditors + 70% living expenses**. Our 2026 version
keeps every card's required minimum current and directs extra toward the highest rate
instead of splitting the extra evenly. RBI's 2025/2026 directions warn that minimum-only
payment can stretch repayment and forfeit the interest-free period.

The ₹60,000 comparison is *illustrative*: monthly interest 3.5%, no new purchases,
fees or tax, month-end payment. First month: ₹2,100 interest; ₹3,000 paid leaves
₹59,100 (principal down ₹900). If ₹10,000 is paid at each month-end instead,
the simplified model closes in **7 payments** with **₹8,542.68** total interest.
Real card terms vary. The exact formula and assertions live in `tests/test_episode05.py`.
Sources and disclaimers are in `content/14-episode5-publish-pack.md`.

## Series roadmap

1. पहले खुद को दो ✅
2. ख़र्चे काबू में ✅
3. पैसा पैसा कमाए ✅
4. पैसा बचाओ, खो मत दो ✅
5. कर्ज़ से आज़ादी (दबासीर) ✅ · 3:59.96 · Short 25.6s · 40-cue SRT · 3 thumbnails
6. घर: ख़र्च या निवेश? ✅ · 3:46.40 · Short 29.3s · 65-cue SRT · 3 thumbnails
7. बुढ़ापे की कमाई ✅ · 3:55.88 · Short 26.5s · 74-cue SRT · 3 thumbnails
8. ख़ुद को बड़ा बनाओ ✅ · 3:43.40 · Short 26.3s · 69-cue SRT · 3 thumbnails
9. Five Laws of Gold (finale) · 572-word script and first four scene recordings done; video pending

© Deep Explains · educational content, not personalised financial advice.
