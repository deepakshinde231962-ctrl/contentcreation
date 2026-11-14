"""
Short #1 — "₹40,000 सैलरी, ₹48,000 बचत" (30 s, vertical 1080x1920)

Built from footage that already exists in this repo (no new generation needed):
the same AI stills, the same speaker audio, the same type system. Rendered by
`scripts/build_short.py`.

Structure (Shorts retention maths: a pattern change every 2-3 seconds)
  0.0-2.5  hook        "सैलरी आई"            (photo + punch-in)
  2.5-8.0  the trick   ₹4,000 auto-debit      (₹ numbers animate)
  8.0-14.0 the maths   12 × 4,000 = ₹48,000   (counter)
  14.0-24.0 the truth  "default, not willpower"
  24.0-30.0 CTA        "पूरा वीडियो" + subscribe
"""

SHORT = dict(
    id="short1",
    title="₹40,000 सैलरी → ₹48,000 बचत?",
    fps=30,
    width=1080,
    height=1920,
    audio="assets/audio/short1.mp3",
    beats=[
        dict(t=0.0, dur=2.6, image="assets/img/04_india.png", focus=(0.5, 0.42),
             kicker="", big="सैलरी आई", sub="", accent="gold"),
        dict(t=2.6, dur=5.4, image="assets/img/07_transfer.png", focus=(0.5, 0.45),
             kicker="अगले दिन", big="₹4,000", sub="अलग खाते में", accent="gold"),
        dict(t=8.0, dur=6.0, image="assets/img/03_gold.png", focus=(0.5, 0.5),
             kicker="12 महीने", big="₹48,000", sub="बिना कोई बड़ा कदम", accent="gold"),
        dict(t=14.0, dur=10.0, image="assets/img/02_arkad.png", focus=(0.5, 0.32),
             kicker="सच", big="default,", big2="willpower नहीं", sub="", accent="cream"),
        dict(t=24.0, dur=6.0, image="assets/img/01_babylon.png", focus=(0.5, 0.45),
             kicker="पूरा वीडियो", big="Deep Explains", sub="हर हफ़्ते एक किताब", accent="gold"),
    ],
)


# Where each beat should start/end so the picture follows the spoken line.
# Timings measured from assets/audio/short1.mp3 (19.9 s):
#   0.0  salary line
#   2.3  "सैलरी के अगले दिन… चार हज़ार"
#   7.6  "बारह महीने में अड़तालीस हज़ार"
#  12.6  "जादू नहीं — सिर्फ़ एक ऑटो डेबिट"
#  16.9  "पूरा वीडियो चैनल पर"
SHORT_BEATS_AT = [0.0, 2.3, 7.6, 12.6, 16.9]
