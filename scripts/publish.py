#!/usr/bin/env python3
"""
publish.py — one command that prints everything you paste into YouTube Studio.

No API keys, no OAuth, nothing to install: it reads the publish pack + the
rendered files and writes a single upload-ready sheet.

  python3 scripts/publish.py 3

Output: out/upload-3.md  (title, description with real links, tags, chapters,
thumbnail pick, caption file, end-screen card text + timer)
"""
from __future__ import annotations

import math
import os
import re
import subprocess
import sys

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
SLUG = {n: f"babylon-niyam-{n}" for n in range(1, 10)}


def ffmpeg_exe() -> str:
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def probe_dur(path: str) -> float:
    """Seconds of an mp4, via ffmpeg's Duration header (no ffprobe needed)."""
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


def main():
    ep = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    pack = os.path.join(ROOT, PACK[ep])
    text = read(pack)

    title = block_after(text, "**Primary:**").strip()
    desc = block_after(text, "## 2. Description")
    if not desc:
        desc = block_after(text, "## 3. Description")
    tags = block_after(text, "## 3. Tags") or block_after(text, "## 4. Tags")
    tags = ", ".join(t.strip() for t in re.split(r"[,\n]", tags) if t.strip())
    pinned = block_after(text, "Pinned comment")
    if not pinned:
        pinned = block_after(text, "## 4. Pinned comment")

    # Replace the pack's Episode bullets with current URLs (or playlist fallback).
    # Keep them *beside the chapters*, before sources/disclaimer/hashtags, not
    # tacked onto the bottom where viewers won't see them.
    link_block = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts", "make_links.py"),
         "--block", str(ep)], capture_output=True, text=True, check=True).stdout
    real = "\n".join(l for l in link_block.splitlines() if l.startswith("▶"))
    if real:
        desc = re.sub(r"^▶ .*\n?", "", desc, flags=re.M)
        desc = re.sub(r"\n{3,}", "\n\n", desc)
        marker = "📚 Sources"
        if marker in desc:
            desc = desc.replace(marker, real + "\n\n" + marker, 1)
        else:
            desc = desc.rstrip() + "\n\n" + real + "\n"

    mp4 = f"out/deep-explains-{SLUG[ep]}.mp4"
    dur = probe_dur(os.path.join(ROOT, mp4))
    # YouTube's editor takes whole seconds. Round UP so clickable cards don't
    # cover the last spoken caption when the 12-second canvas starts at .8s.
    remaining = max(0, math.ceil(dur - 12)) if dur else 0
    timer = f"{remaining // 60:02d}:{remaining % 60:02d}" if dur else "?"

    lines = [
        f"# Upload sheet — Episode {ep}",
        "",
        f"**File:** `{mp4}`" + (f"  ·  {int(dur // 60)}:{dur % 60:05.2f}" if dur else ""),
        "",
        "## Title (copy)",
        "```", title, "```",
        "",
        "## Description (copy)",
        "```", desc, "```",
        "",
        "## Tags (copy)",
        "```", tags, "```",
        "",
        "## Pinned comment (copy)",
        "```", pinned, "```",
        "",
        "## Studio settings",
        f"- Captions: `out/deep-explains-{SLUG[ep]}.hi.srt` → Hindi",
        f"- Thumbnail: `out/thumbnail-niyam{ep}-A-1280x720.jpg` (A/B: test B)",
        f"- End screen timer: **{timer}** (last 12s, rounded up to a whole second)",
        "- Playlist: The Richest Man in Babylon — Hindi",
        "- Visibility: Public, 7–9 PM IST",
        "- Not made for kids",
        "",
    ]
    out = os.path.join(ROOT, "out", f"upload-{ep}.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("wrote", out)


if __name__ == "__main__":
    main()
