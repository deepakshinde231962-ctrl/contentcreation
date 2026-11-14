# End screen — Deep Explains house style

> Video ke last **12 second** (`03:44–03:56`) ek dedicated end-screen frame hain — `video/storyboard.py`
> me scene `endscreen`. Frame me exactly wahi jagah khali chhodi gayi hai jahan YouTube ke end-screen
> elements girenge, isliye jo bhi aap udaas lagega wahi element key frame ke **upar** aayega.
>
> **Coordinate source:** video 1920×1080 hai. YouTube editor 2560×1440 me kaam karta hai, isliye
> editor ke **(X, Y, W, H)** ko **×0.75** karke 1080p me convert kiya gaya hai.

---

## 1. Placeholder zones (video me jo bane hue hain)

| Element | Video pixel (1920×1080) | Editor value (2560×1440) — yahan paste karo |
|---|---|---|
| **Subscribe circle** | centre `(1490, 470)`, radius `120` | X **1987**, Y **627**, size **320 × 320** |
| **Video card 1** (पहले देखें) | box `(222, 690) → (830, 985)` | X **296**, Y **920**, W **811**, H **393** |
| **Video card 2** (NEXT · EPISODE 2) | box `(1090, 690) → (1698, 985)` | X **1453**, Y **920**, W **811**, H **393** |

Safe margin check: left/right margin ~118 px (editor me ~157 px), bottom strip `1030` ke neeche
(editor ~1373) — sab YouTube ke 5% safe area ke andar hai.

---

## 2. YouTube Studio me step-by-step

1. Video → **Details** → playlist: *The Richest Man in Babylon — Hindi*.
2. Left menu → **End screen** → **Add element**:
   - **Subscribe** → choose channel → drag circle to `(1987, 627)` → resize to `320`.
   - **Video** → *Niyam 2: ख़र्चे काबू में* → `(1453, 920)`, size `811 × 393`.
   - **Video** → *30-Day Money Reset Plan (Part 3)* → `(296, 920)`, size `811 × 393`.
   - Optional **Playlist** → *Babylon series* (agar 3 elements rakhna hai to card 1 ki jagah).
3. Timer: `03:44` → **save**. (Video 3:56 hai; last 12s end screen ke liye reserved.)
4. Preview me dekho: koi text card ke neeche chhupna nahi chahiye.

---

## 3. Aapke channel ke hisaab se kya rakha gaya hai

Aapke channel ka data (13 Nov 2026 tak public feed):

| Video | Views signal |
|---|---|
| कर्ज़ और खर्चों से परेशान? 30-Day Money Reset Plan (Part 3) | series ka latest, sabse relevant |
| दूसरों की Success से जलन (Part 2) | |
| सिर्फ सोचने से पैसा आता है? (Part 1) | |
| Hanuman Chalisa | alag audience — end screen me nahi rakha |

Isliye **card 1 = Part 3** (warm series), **card 2 = Niyam 2** (next episode, aap agle hafte
publish karne wale ho). Jab Niyam 2 live ho jaye, Studio me sirf card 2 ka video badalna —
frame same rahega.

---

## 4. End screen ka "ek sekal" rule (channel-wide)

1. **Last 12s = end screen** (voice khatam, sirf music tail).
2. **1 subscribe + 2 videos** — na kam, na zyada.
3. **Right card = next episode** of the series (binge), **left card = best-performing older video**.
4. **Text end screen ke upar na likho** — sirf placeholder boxes.
5. Screen ke neeche `@DeepExplainsOfficial` + "हर हफ़्ते एक किताब" — brand recall.

---

## 5. Rebuild / adjust

```bash
# placeholders ke size badalne ho:
# scripts/build_video.py  ->  SUB_CIRCLE / CARD_L / CARD_R  (1920x1080 pixels)
# end screen ki length:    video/storyboard.py -> fixed_dur=12.0

python scripts/build_video.py --only endscreen     # sirf end screen test
python scripts/build_video.py                      # full render
```


---

## Episode 2 (Niyam 2) ke liye

- Video length **3:32** → timer **`03:20`**
- Right card → **Niyam 3: पैसा पैसा कमाए** (agle hafte)
- Left card → **Niyam 1: पहले खुद को दो**
- Coordinates same (ye template do saal tak same rehta hai)
- **Episode 1 ka end screen bhi update karo**: right card ab Niyam 2 ho
