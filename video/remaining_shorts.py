"""Vertical Shorts repurposing each episode's *actual* scene voice, not new TTS.

Beat changes are derived from the same scene-level captions used by SRT and
video. The renderer adds 1.2s of visual cold-open before the spoken audio.
No extra claim appears on-screen without an explicit assumption/disclaimer.
"""
from __future__ import annotations

from remaining_storyboards import episode

# (scene index, caption indexes at which later visual beats begin, visual cards)
SHORTS = {
    6: (3, (2, 3, 5, 7), (
        dict(image='assets/img/40_home_keys.jpg', kicker='उदाहरण · ₹50 लाख', big='घर या किराया?', sub='₹10 लाख डाउन पेमेंट'),
        dict(image='assets/img/42_emi_ledger.jpg', kicker='8.5% · 20 साल मानकर', big='₹40 लाख', sub='कर्ज़ का उदाहरण'),
        dict(image='assets/img/42_emi_ledger.jpg', kicker='मानकर निकाली EMI', big='₹34,713', sub='महीने की किस्त'),
        dict(image='assets/img/41_rent_vs_buy.jpg', kicker='ऐसा ही घर · मान लो', big='₹18,000', sub='महीने का किराया'),
        dict(image='assets/img/40_home_keys.jpg', kicker='सीधा घटाव गलत', big='मुनाफ़ा नहीं', sub='शुल्क · मरम्मत · दर भी देखो'),
    )),
    7: (0, (1, 3, 4, 6), (
        dict(image='assets/img/43_retirement_clock.jpg', kicker='BABYLON · EPISODE 7', big='₹30,000', sub='आज का मासिक खर्च'),
        dict(image='assets/img/44_future_jar.jpg', kicker='पच्चीस साल बाद?', big='वही खर्च?', sub='आज जैसा सामान'),
        dict(image='assets/img/43_retirement_clock.jpg', kicker='6% सिर्फ़ मानकर', big='₹1.29 लाख?', sub='भविष्यवाणी नहीं'),
        dict(image='assets/img/45_family_safety.jpg', kicker='ध्यान दीजिए', big='सिर्फ़ उदाहरण', sub='असली महँगाई बदलती है'),
        dict(image='assets/img/45_family_safety.jpg', kicker='फ्यूचर इनकम', big='तैयारी किसकी?', sub='अपना और परिवार का हिसाब'),
    )),
    8: (0, (1, 2, 4, 5), (
        dict(image='assets/img/46_craft_tools.jpg', kicker='BABYLON · EPISODE 8', big='₹2,000', sub='कोर्स का खर्च'),
        dict(image='assets/img/47_skill_notebook.jpg', kicker='पहला सवाल', big='कमाई बढ़ेगी?', sub='अगले महीने से?'),
        dict(image='assets/img/48_skill_portfolio.jpg', kicker='सर्टिफिकेट काफ़ी?', big='गारंटी नहीं', sub='काम का नमूना चाहिए'),
        dict(image='assets/img/46_craft_tools.jpg', kicker='छोटा प्रयोग', big='जाँच करो', sub='बड़ा दांव नहीं'),
        dict(image='assets/img/48_skill_portfolio.jpg', kicker='तीन अलग चीजें', big='पैसा · समय', big2='नई कमाई', sub='पूरा वीडियो देखें'),
    )),
    9: (4, (1, 3, 5, 7), (
        dict(image='assets/img/49_five_coins.jpg', kicker='FIVE LAWS · FINALE', big='₹30,000', sub='मान ली गई मासिक आय'),
        dict(image='assets/img/03_gold.png', kicker='किताब का 10% नियम', big='₹3,000', sub='हर महीने अलग'),
        dict(image='assets/img/49_five_coins.jpg', kicker='12 महीने · बिना रिटर्न', big='₹36,000', sub='सिर्फ़ जोड़ का हिसाब'),
        dict(image='assets/img/03_gold.png', kicker='2026 की जाँच', big='कर्ज़ · खर्च', sub='और आपात बचत'),
        dict(image='assets/img/33_freedom_dawn.png', kicker='सबके लिए तय नहीं', big='जितना संभव', sub='बिना समझे पैसा न लगाओ'),
    )),
}


def short(n: int) -> dict:
    ep = episode(n)
    scene_i, cue_starts, beat_cards = SHORTS[n]
    sc = ep['scenes'][scene_i]
    # Episode scene audio is already at exactly the target spoken pace.
    audio = f'assets/audio/ep{n}/narr_{scene_i + 1:02d}_{sc["id"]}.mp3'
    ends = [0.] + [round(sc['captions'][i][0] + 1.2, 2) for i in cue_starts]
    ends.append(round(sc['captions'][-1][1] + 1.2, 2))
    beats = []
    for i, spec in enumerate(beat_cards):
        beats.append(dict(t=ends[i], dur=round(ends[i+1]-ends[i], 2), **spec))
    return dict(id=f'short{n}', title=ep['title'], fps=30, width=1080, height=1920,
                audio=audio, beats=beats, beats_at=ends)
