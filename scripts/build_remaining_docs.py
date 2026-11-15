#!/usr/bin/env python3
"""Build Episodes 6–9's readable scripts + upload publish packs from audio.

Run after each episode's final MP4/Short exists:
    python3 scripts/build_remaining_docs.py 6
    python3 scripts/publish.py 6
No YouTube uploads, fake video IDs, or claims of clickable baked end screens.
"""
from __future__ import annotations

import argparse
import math
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'video'))
sys.path.insert(0, str(ROOT / 'scripts'))
from remaining_content import IDS, METADATA, NARRATIONS  # noqa: E402
from remaining_storyboards import episode, duration  # noqa: E402
from make_links import render_block, load_links  # noqa: E402
from publish import probe_dur  # noqa: E402

TITLES = {
    6: ('₹18,000 किराया या ₹34,713 EMI? | Babylon Ep 6',
        'घर खरीदना समझदारी है? | Babylon Ep 6',
        'किराया देना पैसा फेंकना है? | Babylon Ep 6'),
    7: ('आज के ₹30,000, 25 साल बाद कितने? | Babylon Ep 7',
        'बुढ़ापे की कमाई की तैयारी कैसे? | Ep 7',
        'परिवार की सुरक्षा: बचत या बीमा? | Ep 7'),
    8: ('₹2,000 का कोर्स कमाई बढ़ाएगा? | Babylon Ep 8',
        'हुनर पर खर्च कब निवेश बनता है? | Ep 8',
        'सर्टिफिकेट से सैलरी बढ़ती है? | Ep 8'),
    9: ('पाँच सुनहरे नियम आज भी काम करते हैं? | Ep 9',
        'सात इलाज और पाँच नियम अलग कैसे? | Ep 9',
        '₹3,000 बचाने के बाद क्या जाँचना है? | Ep 9'),
}
THUMB_WORDS = {
    6: ('किराया ₹18,000? / EMI ₹34,713', 'घर खरीदें? / या किराया?',
        'EMI ज़्यादा? / पूरी लागत?'),
    7: ('₹30,000 आज / ₹1.29 लाख?', 'बुढ़ापे की कमाई / कितनी?',
        'महँगाई कितनी? / 25 साल?'),
    8: ('₹2,000 कोर्स? / कमाई पक्की?', 'नया हुनर? / काम कहाँ?',
        'सर्टिफिकेट मिला / कमाई नहीं?'),
    9: ('पाँच नियम? / आज भी?', '₹3,000 बचत / कहाँ जाए?',
        'सात इलाज? / पाँच नियम?'),
}
SUMMARY = {
    6: ("मान लो ₹50 लाख का घर, ₹10 लाख डाउन पेमेंट, ₹40 लाख लोन और ऐसा ही घर ₹18,000 किराये पर। "
        "8.5% सालाना और 20 साल मानने पर EMI लगभग ₹34,713, ब्याज कुल ~₹43.31 लाख। "
        "किस्त और किराये का अंतर मुनाफा नहीं: मूलधन, ब्याज, रजिस्ट्री, रखरखाव, बदलाव की आज़ादी भी गिनें। "
        "ये पुणे की बाजार दर या किसी बैंक का कोट नहीं।"),
    7: ("आज जरूरी खर्च ₹30,000/माह है तो मान ली गई 6% सालाना महँगाई पर 25 साल बाद "
        "उतने ही सामान का गणित लगभग ₹1.29 लाख/माह दिखाता है। यह अनुमानित गणित है, "
        "भविष्यवाणी, आवश्यक रिटायरमेंट कॉर्पस या किसी उत्पाद का रिटर्न नहीं। "
        "बचत और आय पर निर्भर परिवार की सुरक्षा के अलग काम समझें।"),
    8: ("₹2,000 का कोर्स और 40 घंटे का अभ्यास: अगर 6 महीनों तक ₹1,000/माह नया काम मिले, "
        "तो ₹6,000 आय से ₹2,000 सीधा खर्च घटाकर ₹4,000; समय, टैक्स और दूसरे खर्च अभी बाकी। "
        "काम न मिले तो नया पैसा ₹0। कोर्स, सर्टिफिकेट और नौकरी एक ही नतीजे के नाम नहीं।"),
    9: ("अर्काड के बेटे नोमासीर वाली काल्पनिक कहानी में पाँच सुनहरे नियम, सात इलाज से अलग हैं। "
        "बचाना, समझकर काम पर लगाना, जानकार से राय, न समझे हुए सौदे से बचना, असंभव मुनाफे से सावधान रहना। "
        "₹30,000/माह की मान ली गई आय का 10% ₹3,000; 12 महीने में ₹36,000 बिना रिटर्न। "
        "हर परिवार को 10% बचाना संभव नहीं और कोई उत्पाद सुझाया नहीं गया है।"),
}
SOURCE_NOTES = {
    6: [
        'George S. Clason, *The Richest Man in Babylon*, Chapter 3, fifth cure (fictional homeownership lesson): https://en.wikisource.org/wiki/The_Richest_Man_In_Babylon/Chapter_3',
        'RBI, housing-loan FAQ: EMI consists of principal and interest; floating-rate changes can affect payments/tenure: https://www.rbi.org.in/commonman/english/scripts/FAQs.aspx?Id=701',
        'RBI, Key Facts Statement for loans, April 2024 (APR, charges and amortisation schedule disclosure): https://rbidocs.rbi.org.in/rdocs/notification/PDFs/CIRCULARKFS1504242AE2500BAF494C2A82442B0B642705C1.PDF',
    ],
    7: [
        'George S. Clason, *The Richest Man in Babylon*, Chapter 3, sixth cure (future income, not a modern scheme): https://en.wikisource.org/wiki/The_Richest_Man_In_Babylon/Chapter_3',
        '₹30,000 × 1.06^25 ≈ ₹1,28,756/month; × 12 ≈ ₹15.45 lakh/year. 6% is an *assumption*, not a sourced/current inflation statistic.',
    ],
    8: [
        'George S. Clason, *The Richest Man in Babylon*, Chapter 3, seventh cure (ability to earn): https://en.wikisource.org/wiki/The_Richest_Man_In_Babylon/Chapter_3',
        'Illustration: ₹1,000 × 6 − ₹2,000 = ₹4,000 before time, fees, other costs and tax; zero additional work means zero new income.',
    ],
    9: [
        'George S. Clason, *The Richest Man in Babylon*, Chapter 5, Nomasir and the separate Five Laws of Gold (paraphrased, not quoted): https://en.wikisource.org/wiki/The_Richest_Man_In_Babylon/Chapter_5',
        'Illustration: ₹30,000 × 10% = ₹3,000/month; 12 × ₹3,000 = ₹36,000. No assumed return or promised outcome.',
    ],
}
SECTIONS = {
    6: [('Hook · पहले 10 सेकंड', ('hook',)),
        ('अर्काड और किताब का पाँचवाँ इलाज', ('rule', 'science')),
        ('भारत का ₹ उदाहरण', ('india',)),
        ('कहाँ अधूरा?', ('limits',)),
        ('2026 की बेहतर जाँच', ('fix1', 'fix2')),
        ('एक लाइन, अगली कड़ी और subscribe', ('outro',))],
    7: [('Hook · पहले 10 सेकंड', ('hook',)),
        ('अर्काड और किताब का छठा इलाज', ('rule', 'science')),
        ('भारत का ₹ उदाहरण', ('india',)),
        ('कहाँ अधूरा?', ('limits',)),
        ('2026 में परिवार के हिसाब से', ('fix1', 'fix2')),
        ('एक लाइन, अगली कड़ी और subscribe', ('outro',))],
    8: [('Hook · पहले 10 सेकंड', ('hook',)),
        ('अर्काड और किताब का सातवाँ इलाज', ('rule', 'science')),
        ('भारत का ₹ उदाहरण', ('india',)),
        ('कहाँ अधूरा?', ('limits',)),
        ('2026 का छोटा प्रयोग', ('fix1', 'fix2')),
        ('एक लाइन, फिनाले और subscribe', ('outro',))],
    9: [('Hook · पहले 10 सेकंड', ('hook',)),
        ('नोमासीर की कहानी · सभी पाँच नियम', ('rule', 'science', 'india')),
        ('भारत का ₹ उदाहरण', ('limits',)),
        ('पाँच नियम कहाँ अधूरे?', ('fix1',)),
        ('2026 वाला चार-सवाल टेस्ट', ('fix2',)),
        ('एक लाइन, अगली किताब और subscribe', ('outro',))],
}
CHAPTERS = {
    6: ('किराया या घर?', 'किताब: घर का नियम', 'EMI, मूलधन और ब्याज',
        '₹50 लाख / ₹18,000 का उदाहरण', 'चार सीमाएँ', '2026: पूरी लागत',
        'दर/आय का झटका', 'Takeaway + अगली कड़ी'),
    7: ('आज ₹30,000, कल कितना?', 'किताब: भविष्य की आमदनी',
        'महँगाई और लंबी उम्र', '₹1.29 लाख का अनुमान', 'नियम की चार सीमाएँ',
        '2026: खर्च की तैयारी', 'परिवार/जोखिम का हिसाब', 'Takeaway + अगली कड़ी'),
    8: ('₹2,000 का कोर्स?', 'किताब: कमाने की क्षमता', 'कौशल बनाम सर्टिफिकेट',
        '₹6,000 आय / ₹4,000 शेष', 'नियम की चार बाधाएँ', '2026: छोटा प्रयोग',
        'समय · काम · कमाई', 'Takeaway + फिनाले'),
    9: ('पाँच नियम, सात इलाज अलग', 'नोमासीर की कहानी', 'नियम 1–3',
        'नियम 4–5', 'भारत में ₹3,000 उदाहरण', 'नियमों की दो सीमाएँ',
        '2026: चार सवाल', 'Finale + अगली किताब'),
}
TAGS = {
    6: 'richest man in babylon hindi, ghar kharide ya rent, rent vs buy india, EMI vs rent, home loan math hindi, babylon fifth cure, personal finance hindi, deep explains, episode 6',
    7: 'richest man in babylon hindi, retirement planning hindi, future income, inflation hindi, family protection india, babylon sixth cure, financial literacy hindi, deep explains, episode 7',
    8: 'richest man in babylon hindi, earning skills hindi, upskilling roi india, course vs income, babylon seventh cure, financial literacy hindi, deep explains, episode 8',
    9: 'richest man in babylon hindi, five laws of gold hindi, nomasir, seven cures vs five laws, 10 percent saving example, avoid scams hindi, financial literacy india, deep explains, finale',
}
PINNED = {
    6: '₹50 लाख का घर/₹18,000 किराया और 8.5% लोन केवल उदाहरण हैं, पुणे या किसी बैंक की दर नहीं। आपके लिए घर का फैसला किन खर्चों पर निर्भर करता है? निजी रकम या पता न लिखें।',
    7: '₹30,000 × 1.06^25 ≈ ₹1.29 लाख/माह एक काल्पनिक महँगाई गणित है, भविष्यवाणी नहीं। आपके परिवार की तैयारी में किस बात का हिसाब छूटता है? निजी वित्तीय जानकारी न लिखें।',
    8: '₹2,000 कोर्स + 40 घंटे अभ्यास; ₹1,000/माह नया काम सिर्फ़ उदाहरण है, गारंटी नहीं। कौशल चुनते समय आप काम का नमूना कैसे जाँचते हैं?',
    9: '₹30,000 कमाई का 10% = ₹3,000/माह; 12 महीने में ₹36,000 बिना रिटर्न। यह सभी पर लागू लक्ष्य नहीं। पाँच नियमों में आपको सबसे उपयोगी सवाल कौन-सा लगा?',
}


def stamp(s: float) -> str:
    return f'{int(s // 60):02d}:{int(s % 60):02d}'


def link_block(n: int) -> str:
    class Opt:
        playlist = ''
        def __getattr__(self, name):
            return ''
    return render_block(n, load_links(), Opt())


def generate(n: int, script_only: bool = False) -> None:
    # A script can be prepared before TTS; publication metadata must wait for
    # finished audio, a real MP4 and a real Short so its chapter times are true.
    ep = None if script_only else episode(n)
    words = sum(len(NARRATIONS[n][sid].split()) for sid in IDS)
    assert 550 <= words <= 650, (n, words)
    assert all('?' in t and len(t) < 60 for t in TITLES[n])
    script_id, pack_id = (15 + 2*(n-6), 16 + 2*(n-6))
    script_path = ROOT / f'content/{script_id:02d}-episode{n}-script.md'
    pack_path = ROOT / f'content/{pack_id:02d}-episode{n}-publish-pack.md'
    sections = '\n\n'.join(f'## {i}. {name}\n\n' + '\n\n'.join(NARRATIONS[n][sid] for sid in ids)
                           for i, (name, ids) in enumerate(SECTIONS[n], 1))
    source_lines = '\n'.join(f'{i}. {t}' for i, t in enumerate(SOURCE_NOTES[n], 1))
    maths = {
        6: '₹40,00,000 × (0.085/12) × (1+0.085/12)^240 / ((1+0.085/12)^240 − 1) ≈ ₹34,713/माह; ×240 − ₹40,00,000 ≈ ₹43.31 लाख ब्याज। यह स्थिर-दर मॉडल है; शुल्क, टैक्स, रखरखाव, किराये में बढ़ोतरी और घर की पुनर्विक्रय कीमत अलग से समझनी होंगी।',
        7: '₹30,000 × 1.06^25 ≈ ₹1,28,756/माह ≈ ₹15.45 लाख/साल; ₹5,000 × 12 = ₹60,000 बिना रिटर्न। यह खर्च का गणित है, आवश्यक रिटायरमेंट कॉर्पस नहीं।',
        8: '₹1,000 × 6 = ₹6,000 (केवल अगर काम मिला); ₹6,000 − ₹2,000 = ₹4,000, अभ्यास के 40 घंटे और टैक्स/अन्य खर्च से पहले।',
        9: '₹30,000 × 0.10 = ₹3,000/माह; ×12 = ₹36,000 बिना रिटर्न। 10% किताब का उदाहरण है, आवश्यक व्यक्तिगत लक्ष्य नहीं।',
    }[n]
    script_path.write_text(
        f'# Episode {n} · {METADATA[n]["title"]} — 6 हिस्सों में पूरी स्क्रिप्ट\n\n'
        f'**{words} शब्द** · ~4 मिनट · Devanagari Hinglish · Deep Explains\n\n'
        '> किताब का अपना पुनर्कथन है; कोई पंक्ति उद्धृत नहीं। '
        'यह सीरीज़ का एपिसोड नंबर है, किताब का नंबर तभी है जब स्पष्ट रूप से कहा जाए।\n'
        f'> Voice, cards और timed captions: `video/remaining_content.py` + `video/episode0{n}.py`.\n\n'
        + sections + '\n\n---\n\n### Sources और ₹ गणित\n\n' + source_lines +
        '\n\n' + maths + '\n\nयह शैक्षिक उदाहरण है, व्यक्तिगत निवेश/बीमा/कर्ज़/घर खरीदने की सलाह नहीं। कोई विशिष्ट स्टॉक, फ़ंड, उत्पाद या स्कीम नहीं सुझाई गई।\n',
        encoding='utf-8')
    if script_only:
        print(f'wrote script only: {script_path.relative_to(ROOT)} ({words} words)')
        return

    mp4_rel = f'out/deep-explains-babylon-niyam-{n}.mp4'
    mp4_len = probe_dur(str(ROOT / mp4_rel))
    if mp4_len <= 0:
        raise FileNotFoundError('Render the actual main video before writing its publish pack: ' + mp4_rel)
    short_rel = f'out/short-{n}.mp4'
    short_len = probe_dur(str(ROOT / short_rel))
    if short_len <= 0:
        raise FileNotFoundError('Render the actual Short before writing its publish pack: ' + short_rel)
    start = 0.
    chapters = []
    for sc in ep['scenes']:
        label = (CHAPTERS[n][len(chapters)] if sc['id'] != 'endscreen'
                 else 'End-screen canvas (Studio में cards लगाने होंगे)')
        chapters.append(f'{stamp(start)} {label}')
        start += sc.get('fixed_dur', 0.) if sc['id'] == 'endscreen' else (
            sc['pad_in'] + duration(str(ROOT / 'assets/audio' / f'ep{n}' /
                                    f'narr_{len(chapters):02d}_{sc["id"]}.mp3')) + sc['pad_out'])
    end_start = start - 12.
    # Most video containers round a few frames; use the MP4 duration for the
    # integer Studio timer, never promise the baked artwork is clickable.
    timer_sec = math.ceil(mp4_len - 12.)
    timer = stamp(timer_sec)
    titles = '\n'.join(f'{i}. `{t}` ({len(t)} chars)' for i, t in enumerate(TITLES[n], 1))
    thumbs = '\n'.join(f'- {chr(65+i)}: `{t}` · `out/thumbnail-niyam{n}-{chr(65+i)}-1280x720.jpg`'
                       for i, t in enumerate(THUMB_WORDS[n]))
    desc = (f'{SUMMARY[n]}\n\nThe Richest Man in Babylon की मूल कथा को अपने शब्दों में। '
            f'यह सीरीज़ का Episode {n} है; किताब के इलाज और Five Laws अलग अध्याय हैं।\n\n'
            'इस वीडियो में: कहानी, भारतीय ₹ उदाहरण, किताब की कम-से-कम दो सीमाएँ, 2026 में क्या जाँचें, और अगला वीडियो।\n\n'
            '⏱ Chapters\n' + '\n'.join(chapters) + '\n\n' + link_block(n) + '\n\n'
            '📚 Sources\n' + '\n'.join('• ' + t for t in SOURCE_NOTES[n]) + '\n\n'
            f'हिसाब की शर्तें: {maths}\n\n'
            'Disclaimer: यह शैक्षिक जानकारी है, व्यक्तिगत वित्तीय/कानूनी सलाह नहीं; '
            'कोई खास स्टॉक, फ़ंड, उत्पाद या स्कीम सुझाई नहीं गई। अपनी स्थिति और लिखित शर्तें जाँचें।\n\n'
            'हर हफ़्ते एक किताब, आसान हिंदी में। Subscribe करें।\n\n'
            f'#RichestManInBabylon #FinancialLiteracyHindi #DeepExplains')
    clip_idea = {
        6: 'Home-loan गणित वाला दृश्य: ₹50 लाख घर, ₹10 लाख डाउन, ₹40 लाख लोन (8.5%/20 साल केवल मानकर) → EMI ₹34,713 बनाम ₹18,000 किराया; फर्क मुनाफा नहीं, शुल्क/मरम्मत भी देखो।',
        7: 'आज ₹30,000 मासिक खर्च; 25 साल तक 6% मानकर लगभग ₹1.29 लाख/माह? भविष्यवाणी नहीं; अपने और परिवार के लिए अलग तैयारी सोचो।',
        8: '₹2,000 का कोर्स लिया; अगले महीने कमाई बढ़ी? सर्टिफिकेट से ग्राहक/सैलरी तय नहीं; सीखने का पैसा, समय और काम का नमूना अलग गिनो।',
        9: '₹30,000 की मान ली गई कमाई का 10% = ₹3,000/माह, 12 महीने ₹36,000 बिना रिटर्न; अगर 10% संभव न हो तो व्यक्तिगत खर्च पहले देखो।',
    }[n]
    pack_path.write_text(
        f'# Publish pack — Episode {n} · {METADATA[n]["title"]}\n\n'
        f'**Channel:** Deep Explains · **Status:** locally rendered, not uploaded · '
        f'**{stamp(mp4_len)}** ({mp4_len:.2f}s) · 1920×1080/25 fps · '
        f'12s baked end screen starts **{stamp(end_start)}** ({end_start:.2f}s).\n\n'
        f'| File | Purpose |\n|---|---|\n| `{mp4_rel}` | final full episode |\n'
        f'| `out/deep-explains-babylon-niyam-{n}.hi.srt` | exact spoken Hindi captions |\n'
        f'| `out/thumbnail-niyam{n}-A-1280x720.jpg` | primary thumbnail; B/C variants also supplied |\n'
        f'| `{short_rel}` | vertical Short ({short_len:.1f}s; reuses the episode voice) |\n'
        f'| `{script_path.relative_to(ROOT)}` | {words}-word six-part readable script |\n\n'
        '## 1. Question-style titles (all <60 characters)\n\n**Primary:**\n```\n' + TITLES[n][0] +
        '\n```\n\n**Three choices:**\n' + titles + '\n\n'
        '### Fixed thumbnail template · 3–4 words\n\n'
        'Gold Devanagari on the left; subject on the right; English episode/rule kicker and gold badge.\n\n'
        + thumbs + '\n\n---\n\n## 2. Description (paste into Studio)\n\n```\n' + desc + '\n```\n\n---\n\n'
        '## 3. Tags\n\n```\n' + TAGS[n] + '\n```\n\n---\n\n'
        '## 4. Pinned comment\n\n```\n' + PINNED[n] + '\n```\n\n---\n\n'
        f'## 5. Short (~30-second idea, actually {short_len:.1f}s)\n\n'
        f'**File:** `{short_rel}` · 1080×1920 / 30 fps. '
        'Visual beats cut to narration cues; last card contains context, not a fake promise.\n\n'
        + clip_idea + '\n\n---\n\n'
        '## 6. Release / end-screen map\n\n'
        f'- External SRT: `out/deep-explains-babylon-niyam-{n}.hi.srt` → Hindi; burnt captions already visible.\n'
        f'- Studio end-screen timer: **{timer}** (ceil of last 12 seconds); canvas alone is **not clickable**.\n'
        f'- Left box → Episode {n-1}; right box → ' + (f'Episode {n+1}' if n < 9 else
            'Best for viewer / next book when actually available') + '; circle → channel subscribe, *only if Studio is connected*.\n'
        '- Playlist: The Richest Man in Babylon — Hindi; category Education; audience not made for kids.\n'
        '- Publish window to test, not a promise: 7–9 PM IST. Do not claim channel upload until it happens.\n'
        '- The links above currently fall back to the public channel playlist page unless real IDs are supplied; no invented URLs.\n',
        encoding='utf-8')
    print(f'wrote {script_path.relative_to(ROOT)} and {pack_path.relative_to(ROOT)}: '
          f'{words} words, full {mp4_len:.2f}s, Short {short_len:.2f}s, end screen {timer}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('episode', type=int, choices=range(6, 10))
    parser.add_argument('--script-only', action='store_true',
                        help='write the six-part script before narration; no publish pack')
    args = parser.parse_args()
    generate(args.episode, args.script_only)
