#!/usr/bin/env python3
"""Create checked, paste-ready Studio sheets for every finished episode.

No OAuth, uploads, real YouTube IDs or interactive end screens are implied.
After an actual upload, put its ID in ignored links.json and rerun this script
so descriptions and Short-to-long links can use the real URL.

  python3 scripts/publish.py 2
  python3 scripts/publish.py --all
"""
from __future__ import annotations

import argparse
import importlib.util
import math
import os
import re
import subprocess
import sys

from make_links import PLAYLIST_FALLBACK, load_links, playlist, render_block, resolve

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACK = {1: "content/08-publish-pack.md",
        2: "content/10-episode2-publish-pack.md",
        3: "content/11-episode3-publish-pack.md",
        4: "content/12-episode4-publish-pack.md",
        5: "content/14-episode5-publish-pack.md",
        6: "content/16-episode6-publish-pack.md",
        7: "content/18-episode7-publish-pack.md",
        8: "content/20-episode8-publish-pack.md",
        9: "content/22-episode9-publish-pack.md"}
SLUG = {n: f"babylon-niyam-{n}" for n in PACK}

# Short copy reflects the spoken/visible example; hypothetical maths is not
# framed as a promise. Keep episode 2's ₹6,500 × 12 check in the regression test.
SHORT_TITLES = {
    1: "₹40,000 सैलरी, ₹48,000 बचत कैसे? #Shorts",
    2: "तीन खर्च साल में ₹78,000? | Babylon Ep 2 #Shorts",
    3: "₹5,000 महीना: 10 साल की देरी का असर? #Shorts",
    4: "'गारंटीड 4% महीना' — सच या धोखा? #Shorts",
    5: "₹3,000 दिए, कार्ड का कर्ज़ ₹900 ही घटा? #Shorts",
    6: "₹18,000 किराया या ₹34,713 EMI? #Shorts",
    7: "₹30,000 का खर्च 25 साल बाद कितना? #Shorts",
    8: "₹2,000 का कोर्स कमाई बढ़ाएगा? #Shorts",
    9: "₹3,000 महीना अलग: 12 महीने में कितना? #Shorts",
}
SHORT_NOTES = {
    1: "₹40,000/माह की मान ली गई आय से ₹4,000/माह अलग रखने पर 12 महीनों में ₹48,000, बिना रिटर्न। हर किसी के लिए 10% संभव नहीं।",
    2: "मान लो: ₹500 सब्सक्रिप्शन + ₹4,000 बाहर खाना + ₹2,000 ऑटो = ₹6,500/माह; × 12 = ₹78,000 साल का खर्च। यह पूरी रकम बचाने का वादा नहीं; पहले अपना हिसाब देखो।",
    3: "₹5,000/माह और 12% सालाना सिर्फ़ गणित का उदाहरण हैं, किसी निवेश का वादा या पक्का रिटर्न नहीं। समय के साथ लागत और जोखिम भी जाँचो।",
    4: "'हर महीने 4% गारंटीड' जैसे वादे पर जल्दबाज़ी मत करो। ₹50,000 से लगभग ₹80,000 दिखाना सिर्फ़ चक्रवृद्धि गणित है, सुरक्षित या असली ऑफ़र नहीं।",
    5: "₹60,000 कार्ड बकाया और 3.5% मासिक दर सिर्फ़ मानकर: पहले महीने ₹2,100 ब्याज, ₹3,000 भुगतान में ₹900 मूलधन। असली कार्ड पर शुल्क, टैक्स और तारीख़ बदलेंगे।",
    6: "₹40 लाख लोन, 8.5% सालाना और 20 साल केवल अनुमान: EMI करीब ₹34,713। ₹18,000 किराये और EMI का अंतर मुनाफा नहीं; दूसरी लागतें भी हैं।",
    7: "₹30,000 आज के मासिक खर्च पर 25 साल तक 6% सालाना महँगाई केवल मानकर लगभग ₹1.29 लाख/माह। यह भविष्यवाणी या किसी उत्पाद का रिटर्न नहीं।",
    8: "₹2,000 के कोर्स के साथ 40 घंटे अभ्यास: काम मिलने पर ही अतिरिक्त आमदनी संभव है। सर्टिफिकेट से नौकरी या कमाई की गारंटी नहीं।",
    9: "₹30,000 की मान ली गई आय का 10% = ₹3,000/माह; 12 महीनों में ₹36,000 बिना रिटर्न। यह सभी के लिए ज़रूरी लक्ष्य नहीं; खर्च, कर्ज़ और जोखिम जाँचो।",
}


class _LinkArgs:
    playlist = ""

    def __getattr__(self, _name: str) -> str:
        return ""


def ffmpeg_exe() -> str:
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return "ffmpeg"


def probe_dur(path: str) -> float:
    """Seconds of a media file from ffmpeg's Duration header (no ffprobe)."""
    if not os.path.exists(path):
        return 0.0
    out = subprocess.run([ffmpeg_exe(), "-hide_banner", "-i", path],
                         capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", out)
    if not m:
        return 0.0
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))


def read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def block_after(text: str, marker: str) -> str:
    """First fenced block after a marker, or ''."""
    i = text.find(marker)
    if i < 0:
        return ""
    m = re.search(r"```\n(.*?)```", text[i:], re.S)
    return m.group(1).rstrip() if m else ""


def thumb_path(ep: int, variant: str = "A") -> str:
    prefix = "thumbnail-" if ep == 1 else f"thumbnail-niyam{ep}-"
    return f"out/{prefix}{variant}-1280x720.jpg"


def scene_starts(ep: int) -> list[float]:
    """Start times from the *recorded* voice clips (not rounded MP4 duration)."""
    sys.path.insert(0, os.path.join(ROOT, 'video'))
    if ep == 1:
        from storyboard import SCENES
        scenes, audio_dir = SCENES, os.path.join(ROOT, 'assets/audio')
    else:
        spec = importlib.util.spec_from_file_location(f'publish_episode_{ep}',
                                                      os.path.join(ROOT, f'video/episode{ep:02d}.py'))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        scenes, audio_dir = mod.EPISODE['scenes'], os.path.join(ROOT, f'assets/audio/ep{ep}')
    t, starts = 0., []
    for i, scene in enumerate(scenes, 1):
        starts.append(t)
        if scene.get('kind') == 'endscreen':
            if scene['fixed_dur'] != 12:
                raise ValueError(f'Episode {ep}: end-screen canvas must last 12s')
            break
        clip = os.path.join(audio_dir, f'narr_{i:02d}_{scene["id"]}.mp3')
        length = probe_dur(clip)
        if not length:
            raise FileNotFoundError(f'Episode {ep}: missing/invalid narration {clip}')
        t += scene['pad_in'] + length + scene['pad_out']
    if not scenes or scenes[-1].get('kind') != 'endscreen':
        raise ValueError(f'Episode {ep}: missing end-screen scene')
    return starts


def fields_from_pack(ep: int) -> tuple[str, str, str, str]:
    text = read(os.path.join(ROOT, PACK[ep]))
    # Episode 1 says "Primary (recommended)"; the other eight say "Primary".
    primary = re.search(r"\*\*Primary(?: \([^\n]*\))?:\*\*", text)
    title = block_after(text, primary[0]).strip() if primary else ""
    desc = block_after(text, "## 2. Description") or block_after(text, "## 3. Description")
    tags = block_after(text, "## 3. Tags") or block_after(text, "## 4. Tags")
    tags = ", ".join(t.strip() for t in re.split(r"[,\n]", tags) if t.strip())
    pinned = block_after(text, "Pinned comment")
    for name, value in (("title", title), ("description", desc), ("tags", tags),
                        ("pinned comment", pinned)):
        if not value:
            raise ValueError(f"Episode {ep}: missing {name} in {PACK[ep]}")
    if len(title) > 100 or len(desc) > 5000 or len(tags) > 500:
        raise ValueError(f"Episode {ep}: Studio character limit exceeded")
    return title, desc, tags, pinned


def build(ep: int) -> str:
    if ep not in PACK:
        raise ValueError(f"Unknown episode {ep}; choose 1–9")
    mp4 = f"out/deep-explains-{SLUG[ep]}.mp4"
    short = f"out/short-{ep}.mp4"
    srt = f"out/deep-explains-{SLUG[ep]}.hi.srt"
    for rel in (mp4, short, srt, *(thumb_path(ep, v) for v in "ABC")):
        if not os.path.isfile(os.path.join(ROOT, rel)):
            raise FileNotFoundError(f"Episode {ep} is not release-ready: {rel}")
    dur = probe_dur(os.path.join(ROOT, mp4))
    short_dur = probe_dur(os.path.join(ROOT, short))
    if dur < 13 or short_dur < 1 or " --> " not in read(os.path.join(ROOT, srt)):
        raise ValueError(f"Episode {ep}: missing/invalid media or Hindi captions")
    canvas_start = scene_starts(ep)[-1]
    if abs(dur - canvas_start - 12) > .30:
        raise ValueError(f"Episode {ep}: MP4 is stale against narration; rerender before publishing")

    title, desc, tags, pinned = fields_from_pack(ep)
    links, args = load_links(), _LinkArgs()
    real = render_block(ep, links, args)
    if real:
        # Update only series links, leaving any real earlier-channel links in
        # Episodes 1 and 2 untouched. Current links.json is local/ignored.
        desc = re.sub(r"^▶ Episode \d+ .*\n?", "", desc, flags=re.M)
        desc = re.sub(r"\n{3,}", "\n\n", desc)
        marker = "📚 Sources"
        desc = (desc.replace(marker, real + "\n\n" + marker, 1) if marker in desc
                else desc.rstrip() + "\n\n" + real + "\n")
    if len(desc) > 5000:
        raise ValueError(f"Episode {ep}: description exceeds Studio's 5000 chars")

    # The cards are only a baked canvas; Studio must position actual elements.
    timer_sec = math.ceil(canvas_start)
    timer = f"{timer_sec // 60:02d}:{timer_sec % 60:02d}"
    own_url = resolve(ep, links, args)
    pl = playlist(links, args)
    fallback_label = ('सीरीज़ की प्लेलिस्ट' if pl != PLAYLIST_FALLBACK else
                      'चैनल का प्लेलिस्ट पेज (सीरीज़ लिंक नहीं)')
    short_link = (f"पूरा Episode {ep}: {own_url}" if own_url else
                  f"पूरा Episode {ep} upload होने पर video link जोड़ें। अभी {fallback_label}: {pl}")
    short_desc = SHORT_NOTES[ep] + "\n\n" + short_link + "\n\n#Shorts #DeepExplains #FinancialLiteracyHindi"
    left = f"Episode {ep - 1}" if ep > 1 else "existing 30-Day Money Reset Plan (verify in Studio)"
    right = f"Episode {ep + 1} (when published)" if ep < 9 else "Best for viewer / next book when available"
    lines = [
        f"# Upload sheet — Episode {ep}",
        "",
        "**Status:** Locally prepared; no upload performed by this workflow. Verify channel status in Studio. Baked end-screen boxes are not clickable.",
        "",
        f"**File:** `{mp4}`  ·  {int(dur // 60)}:{dur % 60:05.2f}",
        "",
        "## Title (copy)", "```", title, "```", "",
        "## Description (copy)", "```", desc, "```", "",
        "## Tags (copy)", "```", tags, "```", "",
        "## Pinned comment (copy)", "```", pinned, "```", "",
        "## Studio settings — full video",
        f"- Captions: `{srt}` → Hindi",
        f"- Thumbnail: `{thumb_path(ep)}` (B/C alternatives available)",
        f"- End-screen canvas starts at {int(canvas_start//60):02d}:{canvas_start%60:05.2f}; Studio timer: **{timer}** (rounded up; 12s canvas)",
        f"- Left video → {left}; right video → {right}; circle → Subscribe. Add each in Studio only after the linked video exists.",
        "- Playlist: The Richest Man in Babylon — Hindi (create and order 1–9 in Studio)",
        "- Set language Hindi, category Education and the appropriate audience setting in Studio; preview before choosing visibility/schedule.",
        "",
        "## Short — separate Studio upload",
        f"- File: `{short}`  ·  {short_dur:.2f}s  ·  1080×1920",
        f"- Title: `{SHORT_TITLES[ep]}`",
        "- Description (copy):", "```", short_desc, "```",
        "- Add the real full-video URL after uploading it, then add Short to the series playlist if appropriate.",
        "- Choose a readable in-video frame as the Short cover if your Studio interface offers it. Do not upload the full-video thumbnail as a Short cover by default.",
        "",
    ]
    out = os.path.join(ROOT, "out", f"upload-{ep}.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("episode", nargs="?", type=int, choices=range(1, 10),
                        help="episode to prepare (default: 3)")
    parser.add_argument("--all", action="store_true", help="prepare all nine")
    args = parser.parse_args()
    if args.all and args.episode is not None:
        parser.error("choose an episode or --all, not both")
    for ep in range(1, 10) if args.all else (args.episode or 3,):
        print("wrote", build(ep))


if __name__ == "__main__":
    main()
