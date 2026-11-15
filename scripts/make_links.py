#!/usr/bin/env python3
"""
make_links.py — solves the "EPISODE_ONE_LINK" problem for good.

Why this exists
---------------
A YouTube video ID only exists *after* upload, so a description written today
cannot contain tomorrow's link. Instead of leaving `EPISODE_ONE_LINK` littered
across publish packs, every pack now ships with a `links.json`-driven render
step: fill in the IDs once, and this script rewrites every description.

Usage
-----
  # 1. after uploading, put the IDs in links.json (see links.example.json)
  cp links.example.json links.json && $EDITOR links.json

  # 2. regenerate the ready-to-paste blocks in every publish pack
  python3 scripts/make_links.py --write

  # 3. or print one upload description's link block (used by publish.py)
  python3 scripts/make_links.py --block 5

  # 4. or inspect the IDs/fallbacks
  python3 scripts/make_links.py

Resolution order for a video ID (first hit wins):
  1. links.json  ("ep1" … "ep9", "playlist")
  2. environment  EP1_ID, EP2_ID … / PLAYLIST_ID
  3. --ep<N> flags
Until an ID exists, the fallback is the channel page + the series playlist
URL — so a description is never broken, it just points at the channel.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINKS_FILE = os.path.join(ROOT, "links.json")

CHANNEL = "https://www.youtube.com/@DeepExplainsOfficial"
PLAYLIST_FALLBACK = "https://www.youtube.com/@DeepExplainsOfficial/playlists"

# Hindi titles for the series chain (used in every description)
TITLES = {
    1: "पहले खुद को दो",
    2: "ख़र्चे काबू में",
    3: "पैसा पैसा कमाए",
    4: "पैसा बचाओ, खो मत दो",
    5: "कर्ज़ से आज़ादी",
    6: "घर: खर्च या निवेश?",
    7: "बुढ़ापे की कमाई",
    8: "खुद को बड़ा बनाओ",
    9: "Five Laws of Gold",
}


def load_links() -> dict:
    if os.path.exists(LINKS_FILE):
        try:
            with open(LINKS_FILE, encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            sys.exit(f"links.json is not valid JSON: {e}")
    return {}


def resolve(n: int, data: dict, args) -> str:
    key = f"ep{n}"
    val = (args.__dict__.get(f"ep{n}") or data.get(key) or os.environ.get(f"EP{n}_ID") or "").strip()
    if not val:
        return ""
    if val.startswith("http"):
        return val
    return f"https://www.youtube.com/watch?v={val}"


def playlist(data: dict, args) -> str:
    val = (args.playlist or data.get("playlist") or os.environ.get("PLAYLIST_ID") or "").strip()
    if not val:
        return PLAYLIST_FALLBACK
    if val.startswith("http"):
        return val
    return f"https://www.youtube.com/playlist?list={val}"


def line_for(n: int, url: str, pl: str = PLAYLIST_FALLBACK) -> str:
    """One description bullet: do not imply an unconfigured series playlist exists."""
    if url:
        return f"▶ Episode {n} ({TITLES[n]}): {url}"
    label = ('सीरीज़ प्लेलिस्ट में' if pl != PLAYLIST_FALLBACK else
             'वीडियो लिंक मिलने तक चैनल के प्लेलिस्ट पेज पर')
    return f"▶ Episode {n} ({TITLES[n]}): {label} → {pl}"


def render_block(n: int, data: dict, args, upto: int | None = None) -> str:
    """Markdown block listing the earlier episodes, newest first."""
    urls = {i: resolve(i, data, args) for i in range(1, n)}
    pl = playlist(data, args)
    rows = [line_for(i, urls[i], pl) for i in sorted(urls, reverse=True)]
    return "\n".join(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true",
                    help="rewrite the ▶ blocks inside content/*.md publish packs")
    ap.add_argument("--block", type=int, choices=range(1, 10),
                    help="print just the link block for an episode's description")
    ap.add_argument("--playlist", default="")
    for i in range(1, 10):
        ap.add_argument(f"--ep{i}", default="")
    args = ap.parse_args()
    data = load_links()

    if args.block:
        print(render_block(args.block, data, args))
        return

    print("channel :", CHANNEL)
    print("playlist:", playlist(data, args))
    missing = []
    for i in range(1, 10):
        u = resolve(i, data, args)
        print(f"ep{i:<2}    :", u or f"(no configured video ID → falls back to playlist)")
        if not u:
            missing.append(i)
    if missing and args.write:
        print(f"\nnote: ep{missing} have no configured video IDs — descriptions will point at the "
              f"playlist/channel until you add and verify the IDs in links.json")

    if not args.write:
        print("\n-- dry run. run with --write to update content/*.md")
        return

    # ---- rewrite publish packs -------------------------------------------------
    packs = {
        2: "content/10-episode2-publish-pack.md",
        3: "content/11-episode3-publish-pack.md",
        4: "content/12-episode4-publish-pack.md",
        5: "content/14-episode5-publish-pack.md",
        6: "content/16-episode6-publish-pack.md",
        7: "content/18-episode7-publish-pack.md",
        8: "content/20-episode8-publish-pack.md",
        9: "content/22-episode9-publish-pack.md",
    }
    changed = 0
    for ep, path in packs.items():
        full = os.path.join(ROOT, path)
        if not os.path.exists(full):
            continue
        with open(full, encoding="utf-8") as f:
            txt = f.read()
        new = render_block(ep, data, args)
        # replace the contiguous run of "▶ Episode ..." lines
        pattern = re.compile(r"^▶ (?:Episode|पूरी सीरीज़).*(?:\n▶ (?:Episode|पूरी सीरीज़).*)*",
                             re.MULTILINE)
        if not pattern.search(txt):
            print(f"!! no ▶ block found in {path}")
            continue
        txt2 = pattern.sub(new, txt, count=1)
        if txt2 != txt:
            with open(full, "w", encoding="utf-8") as f:
                f.write(txt2)
            changed += 1
            print(f"updated {path}")
    print(f"\n{changed} pack(s) rewritten. Remaining placeholders:",
          placeholders_left())


def placeholders_left() -> int:
    n = 0
    for d in ("content",):
        for fn in os.listdir(os.path.join(ROOT, d)):
            if fn.endswith(".md"):
                with open(os.path.join(ROOT, d, fn), encoding="utf-8") as f:
                    n += len(re.findall(r"EPISODE_[A-Z]+_LINK", f.read()))
    return n


if __name__ == "__main__":
    main()
