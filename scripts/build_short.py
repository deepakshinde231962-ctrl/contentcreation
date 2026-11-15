#!/usr/bin/env python3
"""
build_short.py — renders vertical 9:16 Shorts from video/short*.py definitions.

Same design language as the long-form episode (gold type, film grain, scrims)
but tuned for a phone: huge type, centre-safe zone, beat change every 2-6 s.

Run:
  python scripts/build_short.py            # -> out/short-1.mp4 (1080x1920)
"""
from __future__ import annotations

import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "video"))

import render_lib as R  # noqa: E402
import importlib
import importlib.util
import argparse
import os as _os

_ap = argparse.ArgumentParser()
_ap.add_argument("--short", default="video/short1.py")
_ap.add_argument("--out", default="")
_args = _ap.parse_args()
_short_path = _args.short if _os.path.isabs(_args.short) else _os.path.join(ROOT, _args.short)
spec = importlib.util.spec_from_file_location("short_mod", _short_path)
_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_mod)
SHORT = _mod.SHORT
BEATS_AT = (getattr(_mod, "SHORT_BEATS_AT", None)
            or getattr(_mod, "beats_at", None)
            or SHORT.get("beats_at"))

FF = __import__("build_video").FF
WORK = os.path.join(ROOT, "out", "_work")
W, H = SHORT["width"], SHORT["height"]
FPS = SHORT["fps"]
SAFE_TOP, SAFE_BOTTOM = 220, 240  # Shorts UI: title/likes bottom, channel top


def plate(path: str) -> Image.Image:
    img = Image.open(path).convert("RGB")
    sw, sh = img.size
    scale = max(W / sw, H / sh) * 1.12
    img = img.resize((int(sw * scale), int(sh * scale)), Image.LANCZOS)
    left = (img.width - W) // 2
    top = int(img.height * 0.42) - H // 2
    top = max(0, min(img.height - H, top))
    img = img.crop((left, top, left + W, top + H))
    img = R.vignette(img, amount=95).convert("RGBA")
    # vertical scrim: dark top & bottom, text lives in the middle
    g = Image.new("L", (H, W), 0)
    d = ImageDraw.Draw(g)
    d.rectangle([0, 0, W, H], fill=70)
    g = g.resize((W, H))
    shade = Image.new("RGBA", (W, H), R.INK + (255,))
    shade.putalpha(g)
    img = Image.alpha_composite(img, shade)
    img = Image.alpha_composite(img, R.vertical_scrim((W, H), side="bottom", strength=120, power=2.0))
    return img


def text_overlay(beat: dict) -> Image.Image:
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im, "RGBA")
    cx = W // 2

    kicker = beat.get("kicker") or ""
    if kicker:
        f = R.font("semi", 40)
        w = f.getlength(kicker) + 64
        d.rounded_rectangle([cx - w / 2, 560, cx + w / 2, 640], radius=8,
                            fill=(216, 166, 74, 235))
        d.text((cx, 600), kicker, font=f, fill=(24, 16, 6, 255), anchor="mm")

    y = 720
    f1 = R.font("display", 150)
    big = beat.get("big", "")
    while f1.size > 64 and f1.getlength(big) > W - 150:
        f1 = R.font("display", f1.size - 8)
    if big:
        g = R.gradient_text((0, 0), big, f1, (255, 249, 234), (228, 172, 78))
        # hard shadow for readability over photos
        alpha = g.split()[3].filter(ImageFilter.GaussianBlur(10))
        dark = Image.new("RGBA", g.size, (8, 5, 2, 255))
        dark.putalpha(alpha.point(lambda v: int(v * 0.75)))
        im.alpha_composite(dark, (cx - g.width // 2, y - 6))
        im.alpha_composite(g, (cx - g.width // 2, y - 12))
        y += int(f1.size * 1.02)

    big2 = beat.get("big2") or ""
    if big2:
        f2 = R.font("display", int(f1.size * 0.78))
        while f2.size > 54 and f2.getlength(big2) > W - 150:
            f2 = R.font("display", f2.size - 6)
        g = R.gradient_text((0, 0), big2, f2, (255, 249, 234), (228, 172, 78))
        alpha = g.split()[3].filter(ImageFilter.GaussianBlur(10))
        dark = Image.new("RGBA", g.size, (8, 5, 2, 255))
        dark.putalpha(alpha.point(lambda v: int(v * 0.75)))
        im.alpha_composite(dark, (cx - g.width // 2, y - 4))
        im.alpha_composite(g, (cx - g.width // 2, y - 10))
        y += int(f2.size * 1.05)

    sub = beat.get("sub") or ""
    if sub:
        fs = R.font("body", 54)
        d.text((cx, y + 24), sub, font=fs, fill=R.CREAM[:3] + (240,), anchor="ma",
               stroke_width=4, stroke_fill=(8, 6, 4, 200))

    # top wordmark + progress ticks (keeps the eye moving, all inside safe zones)
    d.text((cx, SAFE_TOP - 60), "DEEP EXPLAINS", font=R.font("semi", 34),
           fill=R.CREAM[:3] + (190,), anchor="mm")
    n = len(SHORT["beats"])
    y_ticks = H - SAFE_BOTTOM - 10
    for i in range(n):
        x0 = cx - (n * 58) / 2 + i * 58
        d.rounded_rectangle([x0, y_ticks, x0 + 46, y_ticks + 8], radius=4,
                            fill=R.GOLD[:3] + (215,))
    return im


def main():
    os.makedirs(WORK, exist_ok=True)
    audio = os.path.join(ROOT, SHORT["audio"])
    from build_video import probe
    adur = probe(audio)
    total = adur + 1.2

    plates = {}
    for b in SHORT["beats"]:
        p = b["image"]
        if p not in plates:
            dst = os.path.join(WORK, "short_plate_" + os.path.basename(p).replace(".png", ".jpg"))
            if not os.path.exists(dst):
                plate(os.path.join(ROOT, p)).convert("RGB").save(dst, quality=95)
            plates[p] = dst

    ovs = []
    for i, b in enumerate(SHORT["beats"]):
        dst = os.path.join(WORK, f"short_ov_{i}.png")
        text_overlay(b).save(dst)
        ovs.append(dst)

    # build each beat as its own clip (length follows the spoken narration),
    # then concat. The last beat is padded with a 0.8s hold so the CTA lands
    # after the voice ends instead of being cut off.
    BEATS = BEATS_AT  # narration-synced beat boundaries
    clips = []
    for i, b in enumerate(SHORT["beats"]):
        start = BEATS[i]
        end = BEATS[i + 1] if i + 1 < len(BEATS) else adur + 1.2
        dur = end - start
        frames = int(round(dur * FPS))
        out = os.path.join(WORK, f"short_beat_{i}.mp4")
        expr = ("z='min(1.002+0.0022*on,1.16)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                if i % 2 == 0 else
                "z='max(1.16-0.0022*on,1.001)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'")
        subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y",
                        "-loop", "1", "-i", plates[b["image"]],
                        "-i", ovs[i],
                        "-filter_complex",
                        f"[0:v]scale={int(W*1.35)}:-2,zoompan={expr}:d={frames}:"
                        f"s={W}x{H}:fps={FPS},scale=in_range=full:out_range=tv,format=yuv420p[bg];[bg][1:v]overlay=0:0:format=auto,format=yuv420p[v]",
                        "-map", "[v]", "-t", f"{dur:.3f}", "-r", str(FPS),
                        "-c:v", "libx264", "-preset", "medium", "-crf", "19", out], check=True)
        clips.append(out)

    lst = os.path.join(WORK, "short_concat.txt")
    with open(lst, "w") as f:
        for c in clips:
            f.write(f"file '{c}'\n")
    joined = os.path.join(WORK, "short_joined.mp4")
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0",
                    "-i", lst, "-c", "copy", joined], check=True)

    final = os.path.join(ROOT, _args.out or f"out/short-{SHORT['id'][-1]}.mp4")
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y", "-i", joined,
                    "-i", audio,
                    "-filter_complex",
                    "[1:a]aresample=48000,highpass=f=85,acompressor=threshold=-19dB:ratio=2.6:"
                    "attack=8:release=180:makeup=2,adelay=1200|1200[n];"
                    "[n]loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000,"
                    "aformat=sample_fmts=fltp:channel_layouts=stereo[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-preset", "medium",
                    "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", final], check=True)
    print("WROTE", final, f"{total:.1f}s")


if __name__ == "__main__":
    main()
