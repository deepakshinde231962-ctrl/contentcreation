# 8-9 Video Series Plan — The Richest Man in Babylon (Hindi)

Channel positioning: **"Har hafte ek kitab, aasaan Hindi me — aaj ke India ke examples ke saath."**
Fixed template = ek jaise thumbnail + same voice + same structure. Isse YouTube ko series samajhne
me aasaani hoti hai aur returning viewers bante hain.

Har episode ka structure (fixed):
`Hook → Niyam → Evidence → India example → Kahan fail hota hai → 2026 version → Takeaway + next teaser`

| # | Episode | Core idea | Hook (10s) | India example | Shorts |
|---|---|---|---|---|---|
| 1 | **पहले खुद को दो** (published/ready) | Kamai ka 10% pehle | "Salary aayi aur teesre hafte khaali" | ₹40,000 salary → ₹4,000 auto-debit | 1 (ready, `out/short-1.mp4`) |
| 2 | **खर्चे काबू में** | Needs vs wants, "90% me jiyo" | "70% kharche 'zaroori' lagte hain, par hain nahi" | Kirana + subscriptions audit | 1 |
| 3 | **पैसा पैसा कमाए** | Compounding | "₹500 mehine se kya hoga?" | 20 saal ka SIP math (no product) | 2 |
| 4 | **पैसा बचाओ, kho mat do** | Guard from loss | "Guaranteed 3% monthly" = scam | Cyber-fraud + F&O data (SEBI) | 2 |
| 5 | **कर्ज़ से आज़ादी (Dabasir)** | Debt payoff | "Credit card ka minimum due" | ₹50,000 card balance math | 2 |
| 6 | **घर: खर्च या निवेश?** | Rent vs buy | "EMI 30 saal ka, ghar 20 saal ka" | Pune/Mumbai rent vs EMI | 1 |
| 7 | **बुढ़ापे की कमाई** | Retirement | "60 ke baad kaun dega?" | EPF/NPS/term insurance basics | 1 |
| 8 | **खुद को बड़ा बनाओ** | Skill = highest ROI | "₹2,000 course vs ₹2,000 phone case" | Freelance/skill upgrade | 2 |
| 9 | **Five Laws of Gold (finale)** | Recap + 5 laws | "5 niyam jo 4,000 saal purane hain" | Full checklist | 2 |

**Publishing rhythm:** hafte me 1 long (3:30–5:00) + 2 Shorts, same day/times.
Shorts ko long video se hi cut karo (retention data compare hoga).

**Playlist:** "The Richest Man in Babylon — Hindi" (episode order me). Playlist description same template.

---

## Growth actions (jo aap aaj kar sakte ho)

1. **Pehle 30 din: sirf 1 book.** In 9 episodes me channel ki identity ban jayegi; beech me doosri books na lo.
2. **Har video ke end me next episode ka teaser** — series binge hoti hai.
3. **Pinned comment me ek sawaal** — comments early reach ke liye sabse sasta signal.
4. **Thumbnail A/B:** 2 variants rakho (same photo, text badlo) — YouTube "Test & Compare" use karo.
5. **Community post** har Shorts ke baad: ek line ka poll ("10% ya 20%?").
6. **Analytics dekho 48 ghante baad:** CTR <4% → thumbnail/title badlo; retention 30s par <60% → hook badlo.
7. **Monetisation safety:** book ki lines copy nahi, sirf ideas; images AI-generated (license-safe);
   music self-generated (`assets/music/bed.mp3`) → koi copyright claim nahi.

---

## Repo coverage — aapke diye reference repos se kya liya

| Repo | Kaam ka idea | Is repo me kahan use hua |
|---|---|---|
| `darkzOGx/youtube-automation-agent` | Script → narration → visuals → MP4 pipeline, approval step | `scripts/build_video.py` ka scene pipeline + `video/storyboard.py` (data-driven episode file) |
| `harry0703/MoneyPrinterTurbo` | Topic → script → footage → subtitles → HD output | burned-in captions + scene timing engine (`fit_caption_chunks`, `caption_band`) |
| `diffusionstudio/editor` | code se timeline/composition banane ka idea | storyboard-as-code (har scene ka apna time, card, motion) |
| `omnichar/OmniChar` | consistent character | fixed series template (same grading, same type, same brand strip) |
| `debpalash/voicestudio` | TTS / narration workflow | narration per-scene clips + loudness-normalised mix (`mix_final`) |
| `latent-spaces/brag` | short, polished motion promo | Ken Burns + gold kinetic type + graded stills |
| `anil-matcha/open-generative-ai` | open image/video model generation | AI stills (`assets/img/01…08`) |

> Yani: un repos ke **ideas** yahan ek chhote, dependency-free pipeline me implement hue hain jo
> **laptop par offline** chalta hai (ffmpeg + PIL), kisi paid API ke bina.


---

## Channel ke apne format ke saath alignment (important)

Aapke maujooda 4 videos ka pattern (public feed se):

| Pehlu | Aapka pattern | Is episode me kya kiya |
|---|---|---|
| Title | `सवाल? | Joseph Murphy Hindi` (Roman/Sanskrit mix, question) | `सैलरी का 10% क्यों गायब हो जाता है?` — wahi question format, Roman suffix `| Richest Man in Babylon Hindi` |
| Description | Intro line → bullet list "इस वीडियो में" → links to previous parts → disclaimer → comment CTA | Same skeleton, plus timestamps + sources (trust) |
| Disclaimer | "यह personalised investment/credit advice नहीं है…" | Same tone, same place (before CTA) |
| Comment CTA | "आज आप क्या शुरू करेंगे…? कमेंट में बताएं" | "आपकी salary का कितना % agle din auto-transfer hota hai? Number likh do" |
| Series chaining | Part 1/2/3 ke links description me | Video 1 me Part 3 ka link + end screen card |
| End screen | (abhi tak nahi) | 12s dedicated frame, exact placeholder zones (`content/07-end-screen.md`) |

**Ek suggestion:** aapke purane titles me book ka naam Roman me hai (`Joseph Murphy Hindi`), isliye
is episode ka title variant 4 (`Richest Man in Babylon Hindi`) search ke liye zyada kaam karega.
A/B test karte waqt wahi use karein.
