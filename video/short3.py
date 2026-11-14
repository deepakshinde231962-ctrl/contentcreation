"""
Short #3 — "10 साल देर = लाखों" (vertical, narration-synced)
Rendered by: python scripts/build_short.py --short video/short3.py
"""

SHORT = dict(
    id="short3",
    title="10 साल देर = लाखों का नुकसान",
    fps=30,
    width=1080,
    height=1920,
    audio="assets/audio/ep3/short3.mp3",
    beats=[
        dict(t=0.0, dur=2.6, image="assets/img/20_growing_coins.png", focus=(0.5, 0.45),
             kicker="", big="₹5,000", sub="हर महीने"),
        dict(t=2.6, dur=4.4, image="assets/img/22_old_clock.png", focus=(0.5, 0.45),
             kicker="सिर्फ़", big="10 साल", sub="का फ़र्क़"),
        dict(t=7.0, dur=4.6, image="assets/img/21_time_chart.png", focus=(0.5, 0.50),
             kicker="अंत में", big="3× से ज़्यादा", sub="का अंतर"),
        dict(t=11.6, dur=5.4, image="assets/img/02_arkad.png", focus=(0.5, 0.32),
             kicker="कंपाउंडिंग", big="शुरू के साल", sub="सबसे कीमती"),
        dict(t=17.0, dur=4.2, image="assets/img/03_gold.png", focus=(0.5, 0.5),
             kicker="सबसे महँगा फ़ैसला", big="देर करना", sub=""),
        dict(t=21.2, dur=4.0, image="assets/img/01_babylon.png", focus=(0.5, 0.45),
             kicker="पूरा वीडियो", big="Deep Explains", sub="Niyam 3 · चैनल पर"),
    ],
    beats_at=[0.0, 2.0, 5.2, 8.6, 12.4, 15.0, 18.2],
)
