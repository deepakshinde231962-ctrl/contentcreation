# 9-Video Series Plan — The Richest Man in Babylon (Hindi)

Channel positioning: **"Har hafte ek kitab, aasaan Hindi me — aaj ke India ke examples ke saath."**
Fixed template = ek jaise thumbnail + same voice + same structure. Isse YouTube ko series samajhne
me aasaani hoti hai aur returning viewers bante hain.

Har episode ka structure (fixed):
`Hook → Niyam → Evidence → India example → Kahan fail hota hai → 2026 version → Takeaway + next teaser`

| # | Episode | What the actual episode covers | Indian illustration | Repo status |
|---|---|---|---|---|
| 1 | **पहले खुद को दो** | पहले बचत; सीमा और सुधार | ₹40,000 की काल्पनिक कमाई | Video + Short ready |
| 2 | **ख़र्चे काबू में** | ज़रूरत बनाम आदत | मान लिए गए ₹500 + ₹4,000 + ₹2,000 प्रति माह = ₹6,500/माह × 12 = ₹78,000/साल के खर्च; बचत का वादा नहीं | Video + Short ready |
| 3 | **पैसा पैसा कमाए** | समय, compounding और जोखिम | काल्पनिक monthly savings | Video + Short ready |
| 4 | **पैसा बचाओ, खो मत दो** | नुकसान और धोखे से बचना | स्रोत दिए गए उदाहरण | Video + Short ready |
| 5 | **कर्ज़ से आज़ादी (दबासीर)** | कर्ज़ पर किताब का 10/20/70 तरीका और आज की सीमाएँ | ₹60,000 कार्ड बकाया, 3.5%/माह सिर्फ़ अनुमान | Video + Short ready |
| 6 | **घर: ख़र्च या निवेश?** | किताब का पाँचवाँ इलाज; किराया बनाम खरीद की *पूरी* लागत | ₹50 लाख घर, ₹40 लाख लोन, 8.5%/20 वर्ष, ₹18,000 किराया — सभी अनुमान | Video + 29.3s Short ready |
| 7 | **बुढ़ापे की कमाई** | किताब का छठा इलाज; भविष्य का खर्च और निर्भर परिवार | ₹30,000/माह का खर्च, 25 साल, 6% अनुमानित महँगाई | Video + 26.5s Short ready |
| 8 | **खुद को बड़ा बनाओ** | किताब का सातवाँ इलाज; कौशल ≠ पक्की कमाई | ₹2,000 कोर्स + 40 घंटे, काम मिलने/न मिलने के दो परिणाम | Video + 26.3s Short ready |
| 9 | **Five Laws of Gold (finale)** | सात इलाज से *अलग* पाँच नियम; 1926 की काल्पनिक कहानी, ऐतिहासिक प्रमाण नहीं | ₹30,000/माह की मान ली गई आय, 10% = ₹3,000, बिना रिटर्न | Video 3:58.96 + 28.7s Short + 73-cue SRT ready |

**Rollout idea:** हर long video के साथ उसी narration से निकला एक Short है।
YouTube publication/playlist/interactive end-screen setup को channel access के बिना पूरा हुआ नहीं मानें।

**Playlist:** "The Richest Man in Babylon — Hindi" (episode order me). Playlist description same template.

---

## Growth actions (jo aap aaj kar sakte ho)

1. **Series ek jagah rakho.** Nine-episode playlist banaane ka plan tabhi poora hai jab video upload ho; repo-ready file ko published na kahen.
2. **Har long video ke end me next episode ka teaser** rakho; clickable card Studio se *alag* jodna hota hai.
3. **Pinned comment me ek sachcha sawaal** rakho; kisi se account number ya private details na mangna.
4. **Thumbnail options:** teen alag, isi series template ke JPG bane hain; Studio me A/B test sirf channel access ho to.
5. **Community post** mein hypothetical ₹ maths aur assumptions saath dena; guaranteed return ya viral claim nahi.
6. **Analytics:** upload ke baad apne channel ka CTR aur retention *apne* baseline se compare karo; 4%/60% universal benchmarks nahi hain.
7. **Rights aur accuracy:** किताब के संवाद/उद्धरण कॉपी नहीं; generated visuals और locally synthesised bed के इस्तेमाल की शर्तें बनाए रखें; copyright claim न आने की गारंटी कोई नहीं दे सकता।

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
> **rendering** ffmpeg + Pillow se locally chalti hai; nayi AI voice aur visuals ke liye alag generation service chahiye.


---

## Channel ke apne format ke saath alignment (important)

Aapke maujooda 4 videos ka pattern (public feed se):

| Pehlu | Aapka pattern | Is episode me kya kiya |
|---|---|---|
| Title | `सवाल? | Joseph Murphy Hindi` (Roman/Sanskrit mix, question) | `सैलरी का 10% क्यों गायब?` — wahi question format, Roman suffix `| Richest Man in Babylon Hindi` |
| Description | Intro line → bullet list "इस वीडियो में" → links to previous parts → disclaimer → comment CTA | Same skeleton, plus timestamps + sources (trust) |
| Disclaimer | "यह personalised investment/credit advice नहीं है…" | Same tone, same place (before CTA) |
| Comment CTA | "आज आप क्या शुरू करेंगे…? कमेंट में बताएं" | "आपकी salary का कितना % agle din auto-transfer hota hai? Number likh do" |
| Series chaining | Part 1/2/3 ke links description me | Video 1 me Part 3 ka link + end screen card |
| End screen | (abhi tak nahi) | 12s dedicated frame, exact placeholder zones (`content/07-end-screen.md`) |

**Ek suggestion:** aapke purane titles me book ka naam Roman me hai (`Joseph Murphy Hindi`), isliye
is episode ka title variant 4 (`Richest Man in Babylon Hindi`) search ke liye zyada kaam karega.
A/B test karte waqt wahi use karein.
