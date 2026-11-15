"""
Short #2 — "₹72,000 साल के — सिर्फ़ 3 आदतें" (vertical, narration-synced)

Rendered by scripts/build_short.py --short video/short2.py
"""

SHORT = dict(
    id="short2",
    title="₹72,000 साल के — सिर्फ़ 3 आदतें",
    fps=30,
    width=1080,
    height=1920,
    audio="assets/audio/ep2/short2.mp3",
    beats=[
        dict(t=0.0, dur=2.6, image="assets/img/11_budget.png", focus=(0.5, 0.5),
             kicker="", big="70% खर्च", sub="ज़रूरी नहीं था"),
        dict(t=2.6, dur=4.2, image="assets/img/10_subscriptions.png", focus=(0.5, 0.45),
             kicker="सब्सक्रिप्शन", big="₹500", sub="महीना"),
        dict(t=6.8, dur=4.4, image="assets/img/12_upi.png", focus=(0.5, 0.45),
             kicker="बाहर खाना", big="₹4,000", sub="महीना"),
        dict(t=11.2, dur=3.6, image="assets/img/14_notebook.png", focus=(0.5, 0.5),
             kicker="रोज़ का ऑटो", big="₹2,000", sub="महीना"),
        dict(t=14.8, dur=6.0, image="assets/img/03_gold.png", focus=(0.5, 0.5),
             kicker="साल के", big="₹72,000", sub="सिर्फ़ 3 आदतें"),
        dict(t=20.8, dur=4.5, image="assets/img/01_babylon.png", focus=(0.5, 0.45),
             kicker="पूरा वीडियो", big="Deep Explains", sub="Niyam 2 · चैनल पर"),
    ],
    beats_at=[0.0, 2.4, 6.4, 10.6, 14.2, 20.2, 24.4],
)
