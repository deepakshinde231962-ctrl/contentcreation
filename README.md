# Deep Explains — Content Engine 🎬

Hindi money-book channel ka poora **research → script → voiceover → video → publish kit** ek jagah.
Sab kuch **offline chalta hai** (ffmpeg + Python), koi paid API nahi.

**Series:** *The Richest Man in Babylon* (George S. Clason, 1926)
**Episode 1:** Niyam 1 — *पहले खुद को दो* (3:56 incl. end screen, 1080p)

---

## Watch / publish

| File | Kya hai |
|---|---|
| `out/deep-explains-babylon-niyam-1.mp4` | **final video** — 3:56, 1080p25, AAC 48 kHz stereo, −14 LUFS, **12s end screen included** |
| `out/deep-explains-babylon-niyam-1.hi.srt` | Hindi captions (YouTube me upload karo) |
| `out/thumbnail-A-1280x720.jpg` | thumbnail A — authority frame (*पहले खुद को दो*, 10%) |
| `out/thumbnail-B-1280x720.jpg` | thumbnail B — pain frame (*सैलरी गई / कहाँ?*) |
| `out/short-1.mp4` | 21s vertical Short (1080×1920), same voice |
| `content/08-publish-pack.md` | **title + description + tags + pinned comment + upload checklist** |
| `content/07-end-screen.md` | end screen ke exact coordinates + Studio steps |
| `content/02-script.md` | script + titles + thumbnail text + Shorts + description |
| `content/01-book-review.md` | book ka scientific review, kahan fail hota hai, 2026 upgrades |
| `content/05-fact-check.md` | har claim ka source / `[CHECK]` status |
| `content/03-series-plan.md` | 8–9 episode plan + publishing rhythm |
| `content/04-channel-strategy.md` | 90-din growth plan, metrics, policy safety |
| `content/06-next-script.md` | Episode 2 ka ready script |

---

## Reproduce / edit

```bash
pip install pillow numpy imageio-ffmpeg scipy       # once

python scripts/build_video.py --stills     # fast preview frames -> out/stills/
python scripts/build_video.py              # full render  -> out/…mp4  (~6 min)
python scripts/build_video.py --remux      # rebuild only audio mix (15s)
python scripts/make_thumbnail.py A B        # thumbnails (A = authority, B = pain)
python scripts/build_short.py               # 21s vertical Short -> out/short-1.mp4
python scripts/make_captions.py             # .srt from the same storyboard
```

**Script edit karna ho?** Sirf `video/storyboard.py` badlo — narration, captions, on-screen cards
aur timing sab wahin hai. Renderer scene duration khud narration clip se naapta hai, isliye
kuch bhi re-time manually nahi karna padta.

```bash
python scripts/build_video.py --only hook,rule   # sirf kuch scenes
```

---

## Structure

```
video/storyboard.py       # EPISODE DEFINITION: narration, captions, cards, camera moves, end screen
video/short1.py           # Short #1 beats + narration-synced timings
scripts/build_video.py    # render pipeline (probe -> plates -> overlays -> motion -> mix)
scripts/render_lib.py     # typography / palette / gradient text (Devanagari-safe via libraqm)
scripts/make_thumbnail.py # 1280x720 thumbnail template (A/B variants)
scripts/build_short.py    # vertical Shorts renderer (1080x1920)
scripts/make_captions.py  # .srt generator (timing from narration audio)
assets/audio/             # narration clips (1 per scene)
assets/img/               # AI-generated cinematic stills
assets/fonts/             # Hind, Mukta (OFL) — Devanagari + Latin
assets/music/bed.mp3      # generated locally (no license issues)
out/                      # final mp4 + thumbnail + QA stills
```

---

## Technical notes

- **Devanagari is rendered with PIL + libraqm, not ffmpeg `drawtext`.** ffmpeg's text filters do not
  guarantee correct matra/conjunct shaping; PIL does. ffmpeg only handles motion + encoding.
- **Ken Burns** motion via `zoompan`; typography is a separate transparent overlay layer, so text
  stays crisp and the photo still moves underneath.
- **Audio:** each narration clip is filtered (high-pass, presence EQ, gentle compression), placed on
  the timeline with `adelay`, mixed with a generated music bed, then `loudnorm I=-14 TP=-1.5` → YouTube-ready.
- **No copyrighted material:** original script, AI-generated stills, self-generated music. Book is public
  domain (1926), but we do not copy any translated lines. See `content/01-book-review.md` §2.

---

## Series roadmap

1. **पहले खुद को दो** ← *this episode (+ Short, `out/short-1.mp4`)*
2. ख़र्चे काबू में (`content/06-next-script.md`, ready)
3. पैसा पैसा कमाए (compounding)
4. पैसा बचाओ, खो मत दो (fraud / F&O — SEBI data)
5. कर्ज़ से आज़ादी (Dabasir)
6. घर: खर्च या निवेश?
7. बुढ़ापे की कमाई
8. खुद को बड़ा बनाओ
9. Five Laws of Gold (finale)

© Deep Explains · educational content, not financial advice.
