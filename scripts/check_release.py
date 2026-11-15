#!/usr/bin/env python3
"""Audit the nine LOCAL upload packages; never mistake this for YouTube upload.

Verifies actual MP4 streams/durations, caption timing, thumbnails and paste-ready
Studio sheets. Missing channel IDs/playlist/end-screen elements are listed as
external manual steps, not silently marked complete.

  python3 scripts/check_release.py
  python3 scripts/check_release.py --no-report   # CI / read-only checks
"""
from __future__ import annotations

import argparse
import math
import re
import subprocess
from pathlib import Path

from PIL import Image

from make_links import load_links, resolve
from publish import ROOT, PACK, SHORT_TITLES, ffmpeg_exe, fields_from_pack, probe_dur, scene_starts, thumb_path

BASE = Path(ROOT)
SRT_CUE = re.compile(r"(?m)^(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n")


class _LinksArgs:
    playlist = ""

    def __getattr__(self, _name: str) -> str:
        return ""


def seconds(stamp: str) -> float:
    h, m, rest = stamp.split(":")
    s, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def streams(path: Path) -> str:
    return subprocess.run([ffmpeg_exe(), "-hide_banner", "-i", str(path)],
                          capture_output=True, text=True).stderr


def check_episode(ep: int) -> tuple[dict, list[str]]:
    issues: list[str] = []
    video = BASE / f"out/deep-explains-babylon-niyam-{ep}.mp4"
    short = BASE / f"out/short-{ep}.mp4"
    srt = BASE / f"out/deep-explains-babylon-niyam-{ep}.hi.srt"
    sheet = BASE / f"out/upload-{ep}.md"
    paths = (video, short, srt, sheet, BASE / PACK[ep],
             *(BASE / thumb_path(ep, v) for v in 'ABC'))
    for p in paths:
        if not p.is_file() or p.stat().st_size == 0:
            issues.append(f"Episode {ep}: missing/empty {p.relative_to(BASE)}")
    row = dict(ep=ep, video=0., short=0., cues=0, timer="—", size_mb=0.)
    if issues:
        return row, issues
    row['size_mb'] = video.stat().st_size / 1_000_000

    for path, size, fps, kind in ((video, '1920x1080', 25, 'full video'),
                                  (short, '1080x1920', 30, 'Short')):
        dur = probe_dur(str(path))
        row['video' if path == video else 'short'] = dur
        if not ((180 <= dur <= 300) if path == video else (10 <= dur <= 60)):
            issues.append(f"Episode {ep}: invalid {kind} duration {dur:.2f}s")
        info = streams(path)
        if not re.search(r"Video: h264 .*\b" + size + r"\b", info):
            issues.append(f"Episode {ep}: {kind} lacks {size} H.264")
        if not re.search(rf"\b{fps} fps\b", info):
            issues.append(f"Episode {ep}: {kind} is not {fps} fps")
        if not re.search(r"Audio: aac .*48000 Hz, stereo", info):
            issues.append(f"Episode {ep}: {kind} lacks stereo 48 kHz AAC")

    for v in 'ABC':
        thumb = BASE / thumb_path(ep, v)
        try:
            with Image.open(thumb) as im:
                if im.size != (1280, 720) or im.format != 'JPEG':
                    issues.append(f"Episode {ep}: incorrect thumbnail {thumb.name}")
                im.verify()
        except Exception as exc:
            issues.append(f"Episode {ep}: unreadable thumbnail {v}: {exc}")

    srt_text = srt.read_text(encoding='utf-8')
    cues = SRT_CUE.findall(srt_text)
    row['cues'] = len(cues)
    if len(cues) < 20 or len(cues) != srt_text.count(' --> '):
        issues.append(f"Episode {ep}: malformed Hindi SRT cue count")
    prev_end = -1.
    for i, (number, start, end) in enumerate(cues, 1):
        a, b = seconds(start), seconds(end)
        if int(number) != i or not (prev_end - .01 <= a < b <= row['video'] - 12 + .5):
            issues.append(f"Episode {ep}: invalid/overlapping caption cue {i}")
            break
        prev_end = b

    try:
        starts = scene_starts(ep)
        if abs(row['video'] - starts[-1] - 12) > .30:
            issues.append(f"Episode {ep}: MP4 stale vs recorded narration and end-screen timeline")
    except (OSError, RuntimeError, ValueError) as exc:
        issues.append(str(exc))
        starts = []
    try:
        title, desc, _, _ = fields_from_pack(ep)
    except ValueError as exc:
        issues.append(str(exc))
        title, desc = '', ''
    if desc and starts:
        chapter_section = desc.split('⏱ Chapters', 1)[-1].split('\n\n', 1)[0]
        chapters = re.findall(r'(?m)^(\d{2}):(\d{2})\s+[^\n]+$', chapter_section)
        if len(chapters) != len(starts):
            issues.append(f"Episode {ep}: chapters {len(chapters)} != scenes {len(starts)}")
        else:
            for i, ((minutes, secs), start) in enumerate(zip(chapters, starts), 1):
                if abs(int(minutes) * 60 + int(secs) - start) > 1.1:
                    issues.append(f"Episode {ep}: chapter {i} differs from voice by >1.1s")
                    break
    sheet_text = sheet.read_text(encoding='utf-8')
    start_sec = math.ceil(starts[-1]) if starts else max(0, math.ceil(row['video'] - 12))
    row['timer'] = f"{start_sec // 60:02d}:{start_sec % 60:02d}"
    for name, required in (("title", f"```\n{title}\n```" if title else 'MISSING TITLE'),
                           ("full-video path", str(video.relative_to(BASE))),
                           ("Short path", str(short.relative_to(BASE))),
                           ("caption path", str(srt.relative_to(BASE))),
                           ("primary thumbnail", thumb_path(ep)),
                           ("Studio timer", f"Studio timer: **{row['timer']}**"),
                           ("Short title", SHORT_TITLES[ep]),
                           ("upload disclaimer", 'no upload performed by this workflow')):
        if required not in sheet_text:
            issues.append(f"Episode {ep}: upload sheet missing {name}")
    if 'EPISODE_ONE_LINK' in sheet_text:
        issues.append(f"Episode {ep}: placeholder video URL in upload sheet")
    return row, issues


def audit() -> tuple[list[dict], list[str]]:
    rows, issues = [], []
    for ep in PACK:
        row, errors = check_episode(ep)
        rows.append(row)
        issues.extend(errors)
    # A wrong sum was previously present in the finished Episode 2 narration.
    # Never let a subsequent thumbnail/doc/video rebuild revive the old claim.
    math_files = (BASE / 'video/episode02.py',
                  BASE / 'out/deep-explains-babylon-niyam-2.hi.srt',
                  BASE / 'video/short2.py', BASE / PACK[2])
    if all(p.is_file() for p in math_files):
        texts = [p.read_text(encoding='utf-8') for p in math_files]
        if any(bad in ' '.join(texts) for bad in ('₹72,000', 'बहत्तर हज़ार')) or not all(
            '₹78,000' in text for text in texts
        ):
            issues.append('Episode 2: spoken/printed ₹78,000 arithmetic regression')
    else:
        issues.append('Episode 2: cannot verify arithmetic; source/SRT/Short/publish pack is missing')
    # These older claims were baked into both audio and artwork; source/metadata
    # checks prevent reintroducing them, alongside the fresh media timeline test.
    fact_files = (BASE / 'video/episode02.py', BASE / PACK[2],
                  BASE / 'scripts/make_thumbnail.py',
                  BASE / 'out/deep-explains-babylon-niyam-2.hi.srt',
                  BASE / 'out/upload-2.md')
    if all(p.is_file() for p in fact_files):
        sources = [p.read_text(encoding='utf-8') for p in fact_files]
        if any(bad in '\n'.join(sources) for bad in
               ('70% खर्च', 'सत्तर प्रतिशत खर्च', 'Sloan 2001', 'Sloan Management Review')):
            issues.append('Episode 2: unsourced 70%/wrong journal resurfaced in release sources')
        if 'रिटायरमेंट प्लान' not in sources[0] or 'Marketing Letters' not in sources[0] + sources[1]:
            issues.append('Episode 2: research scope/source citation regression')
    else:
        issues.append('Episode 2: cannot verify research corrections; sources/upload sheet missing')
    return rows, issues


def report(rows: list[dict], issues: list[str]) -> str:
    data, args = load_links(), _LinksArgs()
    known = sum(bool(resolve(ep, data, args)) for ep in PACK)
    intro = ('# Release readiness — The Richest Man in Babylon (Episodes 1–9)\n\n'
             '**Local technical status:** ' + ('9 upload packages validated; owner editorial/rights review remains.' if not issues else
                                               f'{len(issues)} local issue(s) need fixing before upload.') +
             ' **YouTube status:** Unverified; this local audit has no channel access. These are local artifacts, not publication evidence.\n\n'
             '| Episode | Full video (s) | MP4 (MB) | Short (s) | Hindi SRT | Primary thumbnail | Studio start* |\n'
             '|---|---:|---:|---:|---:|---|---:|\n')
    lines = [intro]
    for r in rows:
        ep = r['ep']
        lines.append(f"| {ep} | {r['video']:.2f} | {r['size_mb']:.1f} | {r['short']:.2f} | "
                     f"{r['cues']} cues | `{thumb_path(ep)}` | **{r['timer']}** |\n")
    lines.append('\n*Start at the first whole second **after the voice-derived canvas cut**; final MP4 duration may differ by a few frames. Baked artwork is not interactive.*\n')
    lines.append('\n**Editorial QA corrections — Episode 2:** The illustrative ₹500 + ₹4,000 + ₹2,000 '
                 '= ₹6,500/month = ₹78,000/year of **spending**, not promised savings. '
                 'The spoken example, Short, captions, thumbnail B and upload copy use the corrected sum. '
                 'The re-recorded hook no longer asserts an unsourced “70% unnecessary” figure; thumbnail A/title ask a question instead. '
                 'The re-recorded evidence scene attributes Madrian & Shea (2001) to retirement-plan enrolment, '
                 'not daily spending, and cites Prelec & Simester (2001) in *Marketing Letters* for the limited card/cash finding. '
                 'These checks cannot certify every editorial claim or confirm channel clearance.\n')
    if issues:
        lines.append('\n## Local defects (fix before upload)\n\n')
        lines.extend(f'- [ ] {issue}\n' for issue in issues)
    lines.append(f'\n## Still requires channel owner / YouTube Studio\n\n'
                 f'- [ ] Review media and intended-use rights personally: font notices are in `assets/fonts/`, while voice/image provenance and channel clearance still need owner confirmation. See `content/23-asset-provenance.md`.\n'
                 f'- [ ] Create the **The Richest Man in Babylon — Hindi** playlist and upload each full video in order (or schedule after review); set title/description/tags, language and appropriate audience settings from `out/upload-N.md`.\n'
                 f'- [ ] Before transfer, run `python3 scripts/make_release_manifest.py --check` to confirm all 54 media files match the frozen handoff; re-run after copying, since SHA-256 cannot verify publication.\n'
                 f'- [ ] Upload each video’s `.hi.srt` in Hindi, choose one of its three JPG thumbnails and inspect the processed public/private preview.\n'
                 f'- [ ] Add actual Studio **video + subscribe end-screen elements** on the 12-second baked canvas, not just the artwork. Follow `content/07-end-screen.md`; link episodes only once published.\n'
                 f'- [ ] Upload each `out/short-N.mp4` separately. Its title, safety notes, description and long-video link guidance are in the same upload sheet.\n'
                 f'- [ ] After each upload, put the real video/playlist IDs in local ignored `links.json` (template: `links.example.json`), then run `python3 scripts/publish.py --all` to replace fallback links before pasting metadata.\n'
                 f'- [ ] Confirm visibility, pinned comments, playlist order, working links and clickable end screens in **Studio**; no script can attest to those without channel access.\n\n'
                 f'Known video IDs in local config: **{known}/9** (presence alone does not prove publication).\n'
                 f'\nRecheck locally: `python3 scripts/check_release.py`, `python3 scripts/make_release_manifest.py --check` and `python3 -m unittest discover -s tests -q`.\n')
    return ''.join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--no-report', action='store_true', help='read-only audit; do not write a report')
    opts = parser.parse_args()
    rows, issues = audit()
    if not opts.no_report:
        out = BASE / 'out/release-readiness.md'
        out.write_text(report(rows, issues), encoding='utf-8')
        print('wrote', out)
    for r in rows:
        print(f"ep{r['ep']}: video {r['video']:.2f}s, Short {r['short']:.2f}s, "
              f"SRT {r['cues']}, Studio {r['timer']}")
    for issue in issues:
        print('FAIL:', issue)
    if issues:
        raise SystemExit(1)
    print('LOCAL PASS: 9 packages. Channel status unverified; publication remains a Studio task.')


if __name__ == '__main__':
    main()
