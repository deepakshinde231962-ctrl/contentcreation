"""Episode 2 Short — corrected arithmetic, with beat cuts following the voice.

Illustrative ₹500 + ₹4,000 + ₹2,000 per month = ₹6,500/month, or
₹78,000 for 12 months. Source voice: ep2/short2.mp3.
"""

SHORT = dict(
    id="short2",
    title="तीन खर्च, साल में ₹78,000? | Babylon Ep 2",
    fps=30,
    width=1080,
    height=1920,
    audio="assets/audio/ep2/short2.mp3",
    beats=[
        dict(t=0.0, dur=3.8, image="assets/img/11_budget.png", focus=(0.5, 0.5),
             kicker="मान लो · ₹50,000 आय", big="3 खर्च", sub="महीने का हिसाब"),
        dict(t=3.8, dur=1.45, image="assets/img/10_subscriptions.png", focus=(0.5, 0.45),
             kicker="सब्सक्रिप्शन", big="₹500", sub="महीना"),
        dict(t=5.25, dur=1.55, image="assets/img/12_upi.png", focus=(0.5, 0.45),
             kicker="बाहर खाना", big="₹4,000", sub="महीना"),
        dict(t=6.8, dur=2.1, image="assets/img/14_notebook.png", focus=(0.5, 0.5),
             kicker="ऑटो", big="₹2,000", sub="महीना"),
        dict(t=8.9, dur=4.7, image="assets/img/03_gold.png", focus=(0.5, 0.5),
             kicker="₹6,500/माह × 12", big="₹78,000", sub="सिर्फ़ जोड़ का उदाहरण"),
        dict(t=13.6, dur=3.4, image="assets/img/11_budget.png", focus=(0.5, 0.5),
             kicker="सब बंद मत करो", big="हिसाब देखो", sub="फिर तय करो क्या बदलना है"),
        dict(t=17.0, dur=2.2, image="assets/img/01_babylon.png", focus=(0.5, 0.45),
             kicker="पूरा वीडियो", big="Deep Explains", sub="Babylon · Episode 2"),
    ],
    # 1.2s cold-open before speech. Breaks follow actual phrase pauses in
    # the 18.00s corrected recording, not the earlier incorrect recording.
    beats_at=[0.0, 3.8, 5.25, 6.8, 8.9, 13.6, 17.0, 19.2],
)
