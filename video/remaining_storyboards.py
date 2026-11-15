"""Episode 6–9 editorial storyboards in Deep Explains' established visual system.

Source-of-truth spoken words: remaining_content.py. Captions are made from
*those exact words* and timed against each delivered scene's actual voice clip;
short on-screen cards supplement (not replace) the verbatim .hi.srt track.
No statistics, stock tips, investment-product recommendations or book quotes.
"""
from __future__ import annotations

import os
import re
import subprocess
from functools import lru_cache
from pathlib import Path

from remaining_content import IDS, METADATA, NARRATIONS

ROOT = Path(__file__).resolve().parents[1]
try:
    import imageio_ffmpeg
    FF = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    FF = 'ffmpeg'


@lru_cache(maxsize=40)
def duration(path: str) -> float:
    s = subprocess.run([FF, '-hide_banner', '-i', path],
                       text=True, capture_output=True).stderr
    m = re.search(r'Duration: (\d+):(\d+):([\d.]+)', s)
    if not m:
        raise RuntimeError(f'No voice clip or bad MP3: {path}')
    return int(m[1])*3600 + int(m[2])*60 + float(m[3])


@lru_cache(maxsize=40)
def breaths(path: str) -> tuple[float, ...]:
    """Voice pauses are candidate subtitle changes; not word-level ASR."""
    stderr = subprocess.run([FF, '-hide_banner', '-i', path, '-af',
                             'silencedetect=noise=-38dB:d=0.16', '-f', 'null', '-'],
                            text=True, capture_output=True).stderr
    a = re.findall(r'silence_start: ([\d.]+)', stderr)
    b = re.findall(r'silence_end: ([\d.]+)', stderr)
    return tuple((float(x) + float(y)) / 2 for x, y in zip(a, b))


def caption_texts(text: str) -> list[str]:
    """Full verbatim captions in balanced phone-readable phrases (no orphan word)."""
    words = text.split()
    units, cur = [], []
    # Sentence endings are preferred boundaries. We may reflow a long sentence
    # below, but never leave 'है?' or 'नहीं।' alone for half a second.
    for word in words:
        cur.append(word)
        if word[-1:] in '।?!;':
            units.append(cur)
            cur = []
    if cur:
        units.append(cur)

    chunks = []
    for unit in units:
        unit_text = ' '.join(unit)
        if len(unit_text) <= 58:
            chunks.append(unit)
            continue
        n = max(2, (len(unit_text) + 52) // 53)
        # Choose word boundaries near equal character lengths (instead of a
        # greedy 53-char line with one stray two-letter word at its end).
        remainder = unit[:]
        for part in range(n - 1):
            target = len(' '.join(remainder)) / (n - part)
            choices = [i for i in range(1, len(remainder))
                       if 23 <= len(' '.join(remainder[:i])) <= 59]
            # Prefer a comma before the target when equally balanced.
            cut = min(choices, key=lambda i: (abs(len(' '.join(remainder[:i])) - target)
                                               - (2 if remainder[i-1].endswith(',') else 0)))
            chunks.append(remainder[:cut])
            remainder = remainder[cut:]
        chunks.append(remainder)
    # Merge any short sentence with a neighbour, or borrow a couple of words
    # from a longer preceding cue if merging would make the band too wide.
    i = 0
    while i < len(chunks):
        if len(' '.join(chunks[i])) >= 20 or len(chunks) == 1:
            i += 1
            continue
        if i and len(' '.join(chunks[i-1] + chunks[i])) <= 66:
            chunks[i-1] += chunks.pop(i)
            continue
        if i + 1 < len(chunks) and len(' '.join(chunks[i] + chunks[i+1])) <= 66:
            chunks[i] += chunks.pop(i+1)
            i += 1
            continue
        if i:
            while len(' '.join(chunks[i])) < 22 and len(chunks[i-1]) > 2:
                chunks[i].insert(0, chunks[i-1].pop())
        i += 1
    cues = [' '.join(c) for c in chunks]
    assert ' '.join(cues) == text, 'Captions must reproduce the narration verbatim'
    return cues


def timed_captions(text: str, path: str) -> list[tuple[float, float, str]]:
    """Estimate phrasing from word lengths, snap to nearby recorded pauses.

    Local cues are intentionally short so timing uncertainty inside a clip is
    under a second; each scene starts from zero, so error never accumulates
    across scenes. This is not a claim of forced/word-level alignment.
    """
    texts = caption_texts(text)
    dur = duration(path)
    total = sum(len(s) for s in texts)
    pauses = breaths(path)
    boundaries = [0.]
    chars = 0
    for i, t in enumerate(texts[:-1], 1):
        chars += len(t)
        expected = dur * chars / total
        candidates = [p for p in pauses if abs(p - expected) <= 0.70
                      and p >= boundaries[-1] + 0.85 and p < dur - 0.85]
        b = min(candidates, key=lambda p: abs(p-expected)) if candidates else expected
        b = max(boundaries[-1] + 0.72, min(b, dur - (len(texts)-i)*0.65))
        boundaries.append(round(b, 3))
    boundaries.append(dur)
    return [(round(a, 3), round(b, 3), t)
            for a, b, t in zip(boundaries, boundaries[1:], texts)]


def c(kicker: str, big: str, sub: str = '', big2: str = '', source: str = '') -> dict:
    return dict(kicker=kicker, big=big, big2=big2, sub=sub, source=source)


CARDS = {
    6: {
        'hook': [c('BABYLON · EPISODE 6', '₹50 लाख का घर', 'किराया या खरीद?'),
                 c('पहला सवाल', 'किराया ₹18,000', 'EMI पूरी लागत नहीं')],
        'rule': [c('किताब · पाँचवाँ इलाज', 'घर का फ़ायदा?', 'हर घर निवेश नहीं')],
        'science': [c('EMI का हिसाब', 'मूलधन + ब्याज', 'किराया और EMI अलग'),
                    c('RBI · HOME LOAN', 'फ्लोटिंग दर', 'किस्त या अवधि बदल सकती है')],
        'india': [c('उदाहरण · 8.5% · 20 साल', '₹34,713 EMI', '₹40 लाख कर्ज़ · अनुमान'),
                  c('इसी तरह का घर', '₹18,000 किराया', 'अंतर मुनाफ़ा नहीं')],
        'limits': [c('THE FINE PRINT', 'शहर बदल सकता है', 'घर तुरंत बेचना आसान नहीं'),
                   c('दूसरी कमी', 'आपात बचत', 'डाउन पेमेंट में शून्य न करो')],
        'fix1': [c('2026 VERSION', 'पूरी लागत लिखो', 'रजिस्ट्री · मरम्मत · EMI')],
        'fix2': [c('STRESS TEST', 'दर +2 अंक?', 'आय रुकने पर भी हिसाब टिके?')],
        'outro': [c('TAKEAWAY', 'घर: रहने की जगह', 'निवेश तभी, जब पूरा हिसाब ठीक'),
                  c('NEXT · EPISODE 7', 'बुढ़ापे की कमाई', 'Subscribe · Deep Explains')],
    },
    7: {
        'hook': [c('BABYLON · EPISODE 7', '₹30,000 आज', '25 साल बाद कितना खर्च?'),
                 c('6% · सिर्फ़ उदाहरण', '₹1.29 लाख?', 'भविष्यवाणी नहीं')],
        'rule': [c('किताब · छठा इलाज', 'भविष्य की आमदनी', 'अपने और परिवार के लिए')],
        'science': [c('दो जोखिम', 'महँगाई · लंबी उम्र', 'कितने साल खर्च चलेगा?')],
        'india': [c('उदाहरण · 6% · 25 साल', '₹1.29 लाख/माह', 'आज के ₹30,000 जैसा खर्च'),
                  c('अगर ₹5,000 हर महीना', '₹60,000 साल', 'बिना किसी रिटर्न के')],
        'limits': [c('THE FINE PRINT', 'सबकी स्थिति अलग', 'मेडिकल खर्च · फीस · टैक्स')],
        'fix1': [c('2026 VERSION', 'एक नंबर नहीं', 'अलग महँगाई दरें जाँचो')],
        'fix2': [c('परिवार की सुरक्षा', 'निर्भर कौन?', 'जोखिम कवर · काग़ज़ अलग')],
        'outro': [c('TAKEAWAY', 'आज तैयारी करो', 'कल की गारंटी नहीं'),
                  c('NEXT · EPISODE 8', 'खुद को बड़ा बनाओ', 'Subscribe · Deep Explains')],
    },
    8: {
        'hook': [c('BABYLON · EPISODE 8', '₹2,000 कोर्स', 'कमाई बढ़ेगी?')],
        'rule': [c('किताब · सातवाँ इलाज', 'हुनर बढ़ाओ', 'जादू नहीं, अभ्यास')],
        'science': [c('सर्टिफिकेट से आगे', 'काम का नमूना', 'सीखना और कमाना अलग')],
        'india': [c('उदाहरण · 40 घंटे', '₹6,000 मिले?', '6 माह × ₹1,000 अतिरिक्त'),
                  c('₹2,000 फीस घटाकर', '₹4,000 बचें?', 'समय, टैक्स, दूसरे खर्च बाकी')],
        'limits': [c('THE FINE PRINT', 'मौका · समय', 'हर कोर्स नौकरी नहीं देता')],
        'fix1': [c('2026 VERSION', 'पहले सबूत', 'काम का नमूना, फिर खर्च')],
        'fix2': [c('तीन कॉलम', 'समय · काम · कमाई', 'नतीजे दिखाओ, दावा नहीं')],
        'outro': [c('TAKEAWAY', 'हुनर काम में दिखे', 'पक्की कमाई का वादा नहीं'),
                  c('NEXT · FINALE', 'पाँच सुनहरे नियम', 'Subscribe · Deep Explains')],
    },
    9: {
        'hook': [c('BABYLON · FINALE', 'पाँच नियम', 'सात इलाज से अलग')],
        'rule': [c('ARKAD · NOMASIR', 'गलती से सीखा', 'किताब की काल्पनिक कहानी')],
        'science': [c('LAWS 1 · 2 · 3', 'बचत · काम · सलाह', 'पहले जाँच, फिर भरोसा'),
                    c('राय लेने से पहले', 'हित भी पूछो', 'मशहूर होना सबूत नहीं')],
        'india': [c('LAWS 4 · 5', 'समझो, फिर लगाओ', 'जल्दी मुनाफ़े से सावधान')],
        'limits': [c('भारत · उदाहरण', '₹3,000 अलग', '₹30,000 कमाई का 10%'),
                   c('बारह महीने · बिना रिटर्न', '₹36,000', 'पहले खर्च और कर्ज़ देखो')],
        'fix1': [c('THE FINE PRINT', '10% सबके लिए नहीं', 'फीस · टैक्स · ज़रूरी खर्च')],
        'fix2': [c('2026 VERSION', 'चार सवाल', 'जोखिम · फीस · निकासी')],
        'outro': [c('FINALE · TAKEAWAY', 'पैसा संभालो', 'फिर फैसले जाँचो'),
                  c('NEXT · NEW BOOK', 'अगली किताब?', 'आप बताइए · Subscribe')],
    },
}

# The image maps preserve a dark, clear left type zone with subject on right.
# Ep9 uses generic gold art for Nomasir, NOT the Ep5 Dabasir portrait.
IMAGE_INDEX = ('hook', 'rule', 'science', 'india', 'limits', 'fix1', 'fix2', 'outro')
IMAGE_CHOICE = {
    6: (0, 1, 2, 2, 1, 0, 2, 0),
    7: (0, 1, 2, 1, 2, 0, 2, 1),
    8: (0, 1, 2, 1, 2, 0, 2, 0),
    9: (0, 1, 0, 0, 1, 2, 1, 0),
}


def episode(n: int) -> dict:
    assert n in METADATA
    meta = METADATA[n]
    prev_title = METADATA[n - 1]['title'] if n > 6 else 'कर्ज़ से आज़ादी'
    scenes = []
    for idx, sid in enumerate(IDS):
        narr = NARRATIONS[n][sid]
        audio = ROOT / f'assets/audio/ep{n}/narr_{idx + 1:02d}_{sid}.mp3'
        caps = timed_captions(narr, str(audio))
        dur = duration(str(audio))
        cards = []
        for ci, entry in enumerate(CARDS[n][sid]):
            card = entry.copy()
            card['start'] = round(dur * 0.52 * ci, 2)
            card['end'] = round(dur * 0.52 * (ci + 1), 2) if ci + 1 < len(CARDS[n][sid]) else 99.
            cards.append(card)
        scenes.append(dict(id=sid, image=meta['images'][IMAGE_CHOICE[n][idx]],
                           motion=('zoom_in', 'pan_right', 'zoom_out', 'zoom_in',
                                   'pan_left', 'zoom_out', 'pan_right', 'zoom_in')[idx],
                           pad_in=0.80 if idx == 0 else 0.55,
                           pad_out=0.65 if idx < 7 else 0.80,
                           narration=narr, captions=caps, cards=cards))
    scenes.append(dict(id='endscreen', kind='endscreen', image=meta['images'][0],
                       motion='zoom_out', fixed_dur=12., pad_in=0., pad_out=0.,
                       narration='', captions=[], cards=[]))
    return dict(id=f'niyam-{n}', slug=f'babylon-niyam-{n}',
                title=f'Episode {n}: {meta["title"]}',
                series='The Richest Man in Babylon', audio_dir=f'ep{n}',
                prev_video=dict(kicker='पहले देखें', title=f'Episode {n - 1}: {prev_title}',
                                meta=f'Episode {n - 1} · ~4 min'),
                next_episode=dict(kicker=f'NEXT · EPISODE {n + 1}' if n < 9 else 'NEXT · NEW BOOK',
                                  title=meta['next'], meta='~4 min · Hindi' if n < 9 else 'बाद में तय होगा'),
                scenes=scenes)
