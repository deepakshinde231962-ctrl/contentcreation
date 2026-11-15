# Channel Growth Strategy — Deep Explains (Hindi money books)

> **Historical planning draft for the first episode.** The nine release files and current
> Studio instructions are in `out/release-readiness.md` and `out/upload-{1..9}.md`;
> the old timing/asset names and sample rollout below are not a live upload status.
>
> Ye document aapke channel ke public signals + current YouTube algorithm + 2026 India ke
> money-content market par based hai. Jahan mujhe aapka private analytics nahi mila, wahan
> saaf likha hai `[aapka data chahiye]`.

---

## 0. Jo main dekh paaya (honest)

- Channel URL se public page open hota hai: **title "Deep Explains"**, handle/description
  JS ke peeche hai. Videos list aur view counts mujhe reliably nahi mile (YouTube public
  scraping block karta hai) → `[aapka data chahiye: last 10 videos ke views, CTR, avg view duration]`.
- Aapke pichhle message ke mutabik channel par abhi **~4 videos** hain aur next week se series
  shuru karni hai. Isliye strategy **"4 videos wale channel"** ke hisaab se likhi hai — bare-scale
  channel ke liye nahi.

Agar aap 3 numbers bhej dein (last 10 videos: **views / CTR / avg view duration %**), main
next brief me plan ko exactly us par calibrate kar dunga.

---

## 1. Positioning (ek line)

> **"Har hafte ek kitab — aasaan Hindi me, aaj ke India ke examples ke saath. Bina hype."**

Isse aap in 3 galtiyon se bachte hain:
- **Hype trap:** "3 mahine me lakhpati" — short-term views deta hai, long-term trust khaata hai.
- **Summary trap:** book ka summary = commodity (1 lakh channels). **Aapka differentiator = "kahan fail hota hai" + India ke numbers.**
- **Scatter trap:** har hafte nayi topic = algorithm ko audience samajh nahi aati.

---

## 2. Pehle 90 din ka plan

### Phase 1 — Foundation (Week 1–4)
| Kaam | Detail |
|---|---|
| 1 series ghusao | Babylon ke 8-9 episodes. Sab same template. |
| Channel ko "series-first" banao | Homepage par playlist pin; banner par "Niyam 1–7" |
| 1 Short per long video (minimum) | Long video ke best 30s se cut |
| Thumbnail template freeze | `out/thumbnail-1280x720.jpg` wala style — poore series me same |
| Description template | Chapters + sources + disclaimer (already `content/02-script.md` me) |

### Phase 2 — Signal (Week 5–8)
- **A/B test titles:** har video ke 2 titles pehle likho; 48 ghante baad CTR dekh ke swap.
- **Community post** hafte me 2: poll ("aapki salary ka kitna % auto-save hota hai?").
- **Pinned comment sawaal** — comments sabse sasta ranking signal hain.
- **Playlist ko "series" ki tarah promote karo** — end screen me next episode, na ki random video.

### Phase 3 — Scale (Week 9–12)
- Top 2 videos ke basis par **next book choose karo** (jo topic me sabse zyada retention diya).
- Shorts ko alag hook se banao (Shorts audience long-video audience se alag hoti hai).
- 1 "collab/reaction" format try karo: kisi finance creator ke claim ka factual review.

---

## 3. Video-level checklist (har video se pehle)

**Hook (0–10s)**
- [ ] Pehle 3 second me "aap" ki problem (EMI, salary, credit card)
- [ ] 10 second tak promise (kya milega) — bina "aaj hum baat karenge" filler

**Retention (10s–end)**
- [ ] Har 30–40s par visual change (is video me: 9 scenes, 40+ cards)
- [ ] Ek "differentiator beat" — yahan woh **"kahan fail hota hai"** section hai (minute ~1:47)
- [ ] Numbers on screen (log sunte nahi, dekhte hain)

**End**
- [ ] Next episode ka naam + 1 line teaser (series binge)
- [ ] CTA chhota: "subscribe" ek baar, video ke end me

**Metadata**
- [ ] Title ≤60 chars + sawaal
- [ ] Thumbnail me 3-4 shabd, mobile par 15% size me bhi readable
- [ ] Chapters (description ke pehle 3 lines me)
- [ ] Sources + disclaimer (trust + monetisation safety)

---

## 4. 2026 me kya kaam karta hai (aur kya nahi)

| Kaam karta hai | Kyun |
|---|---|
| **Specific numbers** (₹40,000, ₹4,000, 37%→86%) | Screenshot-able, share-able, comment-able |
| **Honest limitation section** | Trust = returning viewers; AI-generated summary channels isse nahi karte |
| **Series/playlist** | Session time + subscribe intent |
| **Shorts → long funnel** | Shorts reach deta hai, long video watch-time |
| **Fixed thumbnail system** | Recognition = CTR (brand recall) |

| Kaam nahi karta | Kyun |
|---|---|
| Motivational montage + EDM | 2026 me commodity, retention girta hai |
| Book ki lines padhna | Copyright risk + "reused content" policy |
| Har video me nayi book | Algorithm confuse, audience build nahi hoti |
| "Guaranteed returns" type claims | Policy risk + trust loss |
| 100 tags / keyword stuffing | Koi asar nahi |

---

## 5. Monetisation & policy safety (important)

1. **Copyright:** Babylon public domain hai, par **Hindi translations copyrighted** ho sakti hain. Isliye
   kahani apne shabdon me — koi line copy nahi. (Details: `content/01-book-review.md`)
2. **Reused content:** AI voice + AI images + original script = generally safe, par **added value** dikhna
   chahiye (analysis, India numbers, limitations). Isliye har video me "fine print" section rakha hai.
3. **Financial advice:** koi specific stock/fund/scheme nahi. Disclaimer description me.
4. **Music:** current episode mix renders a local synthetic bed; `assets/music/bed.mp3` is an older repository asset. Confirm origin and usage rights before publication; generation alone does not guarantee claim-free use.
5. **Images/voice/fonts:** locally stored generated art and narration still need a pre-publish terms/licence review for the intended channel and monetisation; do not assume "AI-generated" means no rights issue.

---

## 6. Publish checklist (is episode ke liye, ready)

- [x] Video: `out/deep-explains-babylon-niyam-1.mp4` (3:45, 1080p25, –14 LUFS)
- [x] Thumbnail: `out/thumbnail-1280x720.jpg`
- [x] Title (3 options) + description + tags + pinned comment: `content/02-script.md`
- [x] Chapters timestamps (video ke actual timings se)
- [x] Shorts script (30s): `content/02-script.md`
- [ ] Upload + "Test & Compare" thumbnail (agar available ho)
- [ ] Playlist me add karo ("The Richest Man in Babylon")
- [ ] Pinned comment turant post karo
- [ ] 48 ghante baad CTR/retention dekho → title/thumbnail adjust

---

## 7. Numbers jo aapko track karne chahiye (weekly)

| Metric | Healthy target (naye channel) | Kya karna hai agar kam ho |
|---|---|---|
| CTR | 4–8% | Thumbnail/title badlo (photo se pehle text) |
| Avg view duration | >45% | Hook 3s me tighten, mid-video me pattern interrupt |
| 30s retention | >65% | Intro chhota karo — seedha problem par aao |
| Subs per 1000 views | 3–8 | End me teaser + ek clear CTA |
| Comments per 1000 views | 5–15 | Pinned sawaal + "number likho" CTA |

---

## 8. Agli 3 hafte ka calendar

| Din | Kaam |
|---|---|
| Day 1 | Video 1 upload (private) → thumbnail test → publish 7–9 PM IST |
| Day 2 | Short 1 publish + community poll |
| Day 3 | Comments ke reply + next video ka script (`content/06-next-script.md`) |
| Day 4 | Video 2 narration + visuals |
| Day 5 | Video 2 upload |
| Day 6–7 | Analytics review → thumbnail/title tweak |
| Week 2–3 | Video 3, 4 (same pipeline — `make episode` command) |

---

## 9. Agar aapke paas 1 ghanta hai (sabse zyada ROI)

1. Video 1 upload karo (30 min) — thumbnail + description ready hai.
2. Short 1 banao (15 min) — script ready hai.
3. Pinned comment post karo (2 min).
4. Playlist banao (5 min).
5. Next video ka script review karo (8 min).
