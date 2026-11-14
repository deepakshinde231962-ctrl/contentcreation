#!/usr/bin/env python3
"""
make_captions.py — YouTube caption track (.srt) from the same storyboard that
builds the video, so captions can never drift out of sync with the render.

Timing source of truth: the narration clips in assets/audio (each scene's real
duration) + the storyboard's pad_in/pad_out. Exactly the same maths the video
build uses.

Run: python scripts/make_captions.py
Out: out/deep-explains-babylon-niyam-1.hi.srt
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/video")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import argparse
import build_video as B  # noqa: E402
from storyboard import SCENES as _EP1  # noqa: E402

_ap = argparse.ArgumentParser()
_ap.add_argument("--episode", default="")
_ap.add_argument("--out", default="")
_a = _ap.parse_args()
SCENES = _EP1
if _a.episode:
    B.load_episode(os.path.join(B.ROOT, _a.episode))
    SCENES = B.SCENES

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def ts(sec: float) -> str:
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    ms = int(round((sec - int(sec)) * 1000))
    if ms == 1000:
        s, ms = s + 1, 0
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main():
    path = os.path.join(ROOT, _a.out) if _a.out else os.path.join(
        ROOT, f"out/{B.EPISODE_SLUG}.hi.srt" if _a.episode else "out/deep-explains-babylon-niyam-1.hi.srt")
    t0 = 0.0
    i = 0
    blocks = []
    for idx, sc in enumerate(SCENES):
        if sc.get("kind") == "endscreen":
            continue
        narr = os.path.join(B.AUDIO, f"narr_{idx + 1:02d}_{sc['id']}.mp3")
        ndur = B.probe(narr)
        start = t0 + sc["pad_in"]
        caps = sc["captions"]
        step = ndur / len(caps)
        for k, c in enumerate(caps):
            i += 1
            a = start + k * step
            b = start + (k + 1) * step
            # keep a tiny gap so two cues never touch
            blocks.append(f"{i}\n{ts(a)} --> {ts(max(a + 0.4, b - 0.06))}\n{c}\n")
        t0 += sc["pad_in"] + ndur + sc["pad_out"]

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(blocks))
    print("wrote", path, f"({i} cues, video {t0 + SCENES[-1].get('fixed_dur', 0):.1f}s)")


if __name__ == "__main__":
    main()
