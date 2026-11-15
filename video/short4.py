"""
Short #4 — "गारंटीड 4% महीना" (vertical, narration-synced)
Rendered by: python scripts/build_short.py --short video/short4.py

Beats come straight from the narration's own silences (17.92s total):
  0.00  "एक कॉल में पच्चीस हज़ार?"
  2.20  "'चार प्रतिशत महीना, गारंटीड' — साल का अड़तालीस"
  4.70  "पचास हज़ार बन जाते हैं अस्सी हज़ार दिखने वाले"
  9.60  "फिर पता चलता है — नए लोगों का पैसा पुरानों को"
  13.60 "जो फ़ौरन फ़ैसला माँगे, वो तुम्हारा नहीं"
"""

SHORT = dict(
    id="short4",
    title="'गारंटीड 4% महीना' — सच या धोखा?",
    fps=30,
    width=1080,
    height=1920,
    audio="assets/audio/ep4/short4.mp3",
    beats=[
        dict(t=0.0, dur=2.2, image="assets/img/25_fraud_call.png", focus=(0.5, 0.45),
             kicker="एक कॉल", big="₹25,000", sub="चले गए?"),
        dict(t=2.2, dur=2.5, image="assets/img/24_scam_shield.png", focus=(0.5, 0.5),
             kicker="वादा", big="4% महीना", sub="'गारंटीड'"),
        dict(t=4.7, dur=4.9, image="assets/img/26_emergency_vault.png", focus=(0.5, 0.5),
             kicker="साल का", big="48%", sub="₹50,000 से ₹80,000"),
        dict(t=9.6, dur=4.0, image="assets/img/25_fraud_call.png", focus=(0.5, 0.45),
             kicker="असली सच", big="पोंज़ी", sub="नया पैसा, पुराना हिसाब"),
        dict(t=13.6, dur=4.3, image="assets/img/27_checklist_stone.png", focus=(0.5, 0.5),
             kicker="याद रखो", big="फ़ौरन?", sub="तो तुम्हारा नहीं"),
        # no closing card before the audio ends — the last line is the payoff
    ],
    beats_at=[0.0, 2.2, 4.7, 9.6, 13.6, 17.92],
)
