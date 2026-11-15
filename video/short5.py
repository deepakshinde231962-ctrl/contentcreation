"""Ep5 Short: minimum due ka pehla-mahina math, narration-aligned.

Voice clip: assets/audio/ep5/short5.mp3 (24.36 s).
Beats derive from silences measured in that clip, PLUS the renderer's 1.2 s
voice delay: actual image cut times = 1.2 + voice-silence boundary.
The first image holds during the opening breath; final image continues to the
last spoken word. No fabricated quote or claim about real bank offers.
"""

SHORT = dict(
    id="short5", title="₹3,000 भरे, कर्ज़ सिर्फ़ ₹900 घटा?",
    fps=30, width=1080, height=1920,
    audio="assets/audio/ep5/short5.mp3",
    beats=[
        dict(t=0.00, dur=3.97, image="assets/img/31_debt_ledger.png",
             focus=(0.5, 0.5), kicker="कार्ड का बिल",
             big="₹60,000", sub="बकाया"),
        dict(t=3.97, dur=4.85, image="assets/img/32_debt_chain.png",
             focus=(0.5, 0.5), kicker="मान लो · 3.5% महीना",
             big="₹2,100", sub="पहले महीने का ब्याज"),
        dict(t=8.82, dur=5.20, image="assets/img/31_debt_ledger.png",
             focus=(0.5, 0.5), kicker="₹3,000 चुकाए",
             big="₹900", sub="असली कर्ज़ घटा"),
        dict(t=14.02, dur=8.52, image="assets/img/30_dabasir.png",
             focus=(0.5, 0.5), kicker="हरा टिक, पूरा बिल नहीं",
             big="मिनिमम समय पर", big2="महँगा पहले",
             sub="अपना स्टेटमेंट देखो"),
        dict(t=22.54, dur=3.02, image="assets/img/33_freedom_dawn.png",
             focus=(0.5, 0.5), kicker="सिर्फ़ उदाहरण",
             big="दर अलग होगी", sub="शर्तें पढ़ो"),
    ],
    beats_at=[0.0, 3.97, 8.82, 14.02, 22.54, 25.56],
)
