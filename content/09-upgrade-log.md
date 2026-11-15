# Upgrade log — v1 se v2 (kya improve hua aur kyun)

Ye file batati hai ki pichle build se is build me **kya badla** aur **kaunse evidence** par.
Publish karte waqt yahi cheezein aapke favou rme jayengi.

---

## 1. Video (v1 → v2)

| # | Pehle | Ab | Kyun |
|---|---|---|---|
| 1 | Ek hi dheema Ken Burns push poore scene me (18–37s) | Har **3–6 second** par punch-in cut: 1.0x wide ↔ 1.30x tighter + halka brightness lift | Scene ke andar movement na hone se retention girta hai. Cuts narration ke **sentence pause** par land karte hain (`silencedetect`), isliye edit musical lagta hai. |
| 2 | Captions 5 second tak ek jaise | Do-line cue me **active line gold**, doosri dim | Karaoke rhythm — aankh ko har 2-3s par naya signal milta hai. |
| 3 | Music constant, voice ke neeche db mein dabta nahi | Sidechain **ducking** (~6 dB) + ungated floor copy | Phone speaker par shabd saaf, gaps me music zinda. |
| 4 | End screen par audio **–70 LUFS** (silent) | –30 dB music tail | End screen par silencе = dead air; YouTube end screen par viewer ko hold nahi karta. |
| 5 | Bed me sirf drone + pluck | + soft frame-drum tick (4-beat) + last 12s me riser | Pulse se "video chal rahi hai" ka ehsaas; riser se end-screen hand-off. |
| 6 | Hook: "सैलरी आई..." (generic) | **"चालीस हज़ार की सैलरी, और तीसरे हफ़्ते खाता खाली"** | Pehle 3 second me number + dard + specificity = CTR/retention ka sabse bada lever. |
| 7 | End screen 12s **kat jaa raha tha** (video 3:44, joined 3:57) | Fix: `probe()` ab Duration header padhta hai; final mux `-t` use karta hai | Silent bug — YouTube end screen elements ek missing frame par lagte. |
| 8 | — | `-13.7 LUFS / -0.8 dBTP` verified | YouTube normalisation ke liye sahi range. |

---

## 2. Thumbnails (2 → 3 variants)

| Variant | Angle | Kab use karein |
|---|---|---|
| **A** — *पहले खुद को दो* + 10% | Authority / series identity | Warm audience, playlist visitors |
| **B** — *सैलरी गई / कहाँ?* | Pain + curiosity | Naye viewers (browse/suggested) |
| **C** — *10% नियम / फेल?* | Curiosity gap | Video ke "kami" promise se match |

**Layout rules** (teeno follow karte hain): type left 55% me, face right, kicker top-left,
bottom-right **duration stamp area khali**, mobile 15% size par bhi readable.

---

## 3. Packaging

- **Captions** `.srt` (52 cues) storyboard se auto-generate — video se kabhi out of sync nahi.
- **End screen** me exact coordinates (`content/07-end-screen.md`), timer `03:45`.
- **Description** me chapters (auto-computed), sources, aapke Part 1/2/3 links, disclaimer.
- **Shorts** (21s) narration-synced beats.

---

## 4. Jo abhi bhi weak hai (honest)

1. **Visual variety** — 8 AI stills hain, kuch scenes me repeat hote hain. Agle episode me 2-3 naye
   shots (hands, phone screen, notebook) add karna better hoga.
2. **Voice** — ek hi narrator, thoda flat. Paragraph breaks par 0.2s pause daalne se better lagega.
3. **Kinetic type** — abhi cards hard-cut hote hain; future me 6-frame fade/slide-in add kar sakte hain.
4. **B-roll** — real footage (apne hands, apna phone, apna notebook shoot karo) AI stills se zyada
   authentic lagta hai; 30 second ka phone footage kaafi hai.

---

## 5. Rebuild commands

```bash
python scripts/build_video.py                # full (~6 min)
python scripts/build_video.py --only hook    # ek scene test
python scripts/build_video.py --remux        # sirf audio (15 s)
python scripts/make_thumbnail.py A B C       # teeno thumbnails
python scripts/build_short.py                # Short
python scripts/make_captions.py              # .srt
```
