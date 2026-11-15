#!/usr/bin/env python3
"""
build_video.py — renders the whole "Richest Man in Babylon" episode.

Pipeline
  1. probe each narration clip (ffmpeg)         -> scene durations
  2. PIL: pre-composite photo + scrim + grade   -> assets/img/comp_*.png
  3. PIL: draw kinetic typography per card      -> out/_frames/... (PNG seq)
  4. ffmpeg: Ken Burns motion + card overlays   -> out/_scenes/*.mp4
  5. ffmpeg: concat + music bed + loudness      -> out/deep-explains-babylon-final.mp4

Why PIL for type: PIL/libraqm shapes Devanagari correctly (matras, conjuncts,
nukta). ffmpeg drawtext does not guarantee it. ffmpeg only moves pixels.

Usage
  python scripts/build_video.py            # full render
  python scripts/build_video.py --stills   # only write key frames (fast QA)
  python scripts/build_video.py --only hook,rule
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "video"))
from storyboard import (SCENES as _EP1_SCENES, BRAND, HANDLE, SERIES,  # noqa: E402
                        NEXT_EPISODE, PREV_VIDEO, FPS, WIDTH, HEIGHT)
import render_lib as R  # noqa: E402

# Episode selection: --episode video/episode02.py (or EPISODE_FILE env var).
# Episode 1 stays the default so old commands keep working.
SCENES = _EP1_SCENES
EPISODE_SLUG = "babylon-niyam-1"
EPISODE_TITLE = "Niyam 1: पहले खुद को दो"

ROOT = R.ROOT
OUT = os.path.join(ROOT, "out")
AUDIO = os.path.join(ROOT, "assets", "audio")
AUDIO_EP = AUDIO  # switched per episode
WORK_ROOT = os.path.join(OUT, "_work")
# One scratch directory per episode. Otherwise --remux could silently reuse
# another episode's joined.mp4 and QA stills could mix unrelated cards.
WORK = os.path.join(WORK_ROOT, EPISODE_SLUG)
# Each render synthesises a bed matching its own length. Keep the ephemeral
# result in ignored scratch rather than overwriting the tracked legacy bed.
MUSIC = os.path.join(WORK, "bed.mp3")


def ffmpeg_exe() -> str:
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


FF = ffmpeg_exe()
# Ep6–9 can opt into faster scratch renders and a small upload-ready H.264
# final without changing earlier episodes' default output settings.
BUILD_PRESET = os.environ.get("DEEP_BUILD_PRESET", "medium")
COMPACT = os.environ.get("DEEP_COMPACT", "") == "1"


def run(cmd: list[str], quiet=True):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        sys.stderr.write(" ".join(cmd)[:400] + "\n" + (p.stderr or "")[-3000:])
        raise RuntimeError("ffmpeg failed")
    return p.stderr


def probe(path: str) -> float:
    """Real duration in seconds.

    Reads ffmpeg's Duration header first. The naive "first time= line" version
    under-reports ended/muxed files badly (it cost the 12 s end screen once),
    so Duration is authoritative and time= is only a fallback.
    """
    out = run([FF, "-hide_banner", "-i", path, "-f", "null", "-"])
    for line in out.splitlines():
        if "Duration:" in line:
            hms = line.split("Duration:")[1].split(",")[0].strip()
            h, m, sec = hms.split(":")
            total = int(h) * 3600 + int(m) * 60 + float(sec)
            if total > 0:
                return total
    times = [l.split("time=")[1].split()[0] for l in out.splitlines()
             if "time=" in l and "Duration" not in l]
    if times:
        h, m, sec = times[-1].split(":")
        return int(h) * 3600 + int(m) * 60 + float(sec)
    raise RuntimeError(f"could not probe duration of {path}")


# ---------------------------------------------------------------------------
# 2. plate: photo -> graded 1920x1080 base
# ---------------------------------------------------------------------------
def build_plate(src: str, dst: str, scrim="left", grade=0.30, dark=0.0, blur=0.0):
    img = Image.open(src).convert("RGB")
    # cover-crop
    sw, sh = img.size
    scale = max(WIDTH / sw, HEIGHT / sh) * 1.06
    img = img.resize((int(sw * scale), int(sh * scale)), Image.LANCZOS)
    left = (img.width - WIDTH) // 2
    top = (img.height - HEIGHT) // 2
    img = img.crop((left, top, left + WIDTH, top + HEIGHT))
    if blur:
        img = img.filter(ImageFilter.GaussianBlur(blur))
    img = R.vignette(img, amount=110).convert("RGB")

    # cinematic grade: pull saturation a touch, warm the highlights, lift teal shadows
    a = np.asarray(img).astype(np.float32) / 255.0
    lum = a @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    a = np.clip(lum[..., None] + (a - lum[..., None]) * 0.86, 0, 1)
    shadow = np.clip(1.0 - lum, 0, 1)[..., None] ** 2
    a = a + shadow * np.array([-0.02, 0.012, 0.035], dtype=np.float32)
    a[..., 0] *= 1.015
    a[..., 2] *= 0.985
    img = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))

    base = img.convert("RGBA")
    if scrim != "none":
        base = Image.alpha_composite(base, R.vertical_scrim((WIDTH, HEIGHT), side=scrim, strength=225))
    base = Image.alpha_composite(base, R.vertical_scrim((WIDTH, HEIGHT), side="bottom", strength=170, power=2.4))
    base = Image.alpha_composite(base, R.grain((WIDTH, HEIGHT)))
    if dark:
        flat = Image.new("RGBA", (WIDTH, HEIGHT), R.INK + (255,))
        flat.putalpha(int(255 * dark))
        base = Image.alpha_composite(base, flat)
    base.convert("RGB").save(dst, quality=95)
    return dst


# ---------------------------------------------------------------------------
# 3. typography cards
# ---------------------------------------------------------------------------
def card_layer(plate: Image.Image, card: dict, scene_idx: int) -> Image.Image:
    """Transparent RGBA overlay holding ONLY the typography.

    The photo is applied later by ffmpeg (so Ken Burns motion stays visible
    under the words). Shadows are drawn on their own blurred layer so they
    never read as grey blocks on the photo.
    """
    im = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(im, "RGBA")
    left = 148
    bottom_limit = 690          # caption band owns y >= 690

    d.text((left, 58), f"{scene_idx + 1:02d} / {len(SCENES):02d}", font=R.font("semi", 24),
           fill=R.GOLD[:3] + (185,))
    d.text((WIDTH - 148, 60), BRAND, font=R.font("semi", 26), fill=R.CREAM[:3] + (165,), anchor="ra")
    d.line([(left, 104), (WIDTH - 148, 104)], fill=R.CREAM[:3] + (34,), width=1)

    kicker = card.get("kicker", "")
    big = card.get("big", "")
    big2 = card.get("big2", "")
    sub = card.get("sub", "")
    source = card.get("source", "")

    y = 250
    if kicker:
        R.kicker_block(d, (left, y), kicker, size=30)
        y += 92

    # choose a size that fits width AND leaves room for sub lines
    f_big = R.font("display", 126)
    def fits(f):
        lines = R.wrap(big, f, 1150) + (R.wrap(big2, f, 1150) if big2 else [])
        return max((f.getlength(l) for l in lines), default=0) <= 1150
    while f_big.size > 58 and not fits(f_big):
        f_big = R.font("display", f_big.size - 6)

    for line in R.wrap(big, f_big, 1150):
        g = R.gradient_text((0, 0), line, f_big, (253, 243, 222), (231, 178, 88))
        im.alpha_composite(g, (left - 6, y - 6))
        y += int(f_big.size * 1.06)
    if big2:
        f2 = R.font("display", int(f_big.size * 0.90))
        for line in R.wrap(big2, f2, 1150):
            g = R.gradient_text((0, 0), line, f2, (253, 243, 222), (231, 178, 88))
            im.alpha_composite(g, (left - 6, y - 6))
            y += int(f2.size * 1.06)

    if sub:
        y += 14
        f_sub = R.font("body", 44)
        for line in R.wrap(sub, f_sub, 1080):
            d.text((left, y), line, font=f_sub, fill=R.CREAM[:3] + (238,))
            y += 62
    if source:
        f_src = R.font("body", 30)
        for line in R.wrap(source, f_src, 1000):
            d.text((left, y), line, font=f_src, fill=R.CREAM_DIM[:3] + (205,))
            y += 42

    if y > bottom_limit:
        print(f"  ! card overflow in scene {scene_idx + 1} ({card.get('kicker')}) bottom={y}")

    # shadow pass: blur the alpha, offset, darken
    alpha = im.split()[3]
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sh.putalpha(alpha.point(lambda v: int(v * 0.72)))
    sh = sh.filter(ImageFilter.GaussianBlur(9))
    shadow = Image.new("RGBA", im.size, (6, 4, 2, 255))
    shadow.putalpha(sh.split()[3])
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.alpha_composite(shadow, (0, 7))
    out.alpha_composite(im)
    return out



# ---------------------------------------------------------------------------
# end screen: exact placeholder zones for YouTube's own elements
#   • subscribe circle   -> centre x 1490, y 470, r 120   (2380,940 diameter 240)
#   • video card left    -> (560, 700, 1160, 990)
#   • video card right   -> (1840, 700, 2440, 990)
#     (coords in the 2560-wide editor are halved for 1080p: see docs)
# ---------------------------------------------------------------------------
SUB_CIRCLE = (1490, 470, 120)            # cx, cy, r
CARD_L = (222, 690, 830, 985)            # x0, y0, x1, y1
CARD_R = (1090, 690, 1698, 985)


def endscreen_layer(scene_idx: int) -> Image.Image:
    im = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(im, "RGBA")

    # left headline block
    x = 148
    d.text((x, 196), SERIES.upper(), font=R.font("semi", 26), fill=R.GOLD[:3] + (230,))
    d.rectangle([x, 240, x + 64, 244], fill=R.GOLD[:3] + (255,))
    d.text((x, 286), "आगे क्या देखें?", font=R.font("display", 84), fill=R.CREAM[:3] + (250,))
    d.text((x, 402), "दो वीडियो, एक ही सीरीज़ — नीचे से चुनिए",
           font=R.font("body", 38), fill=R.CREAM_DIM[:3] + (235,))

    # subscribe circle placeholder
    cx, cy, r = SUB_CIRCLE
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=R.GOLD[:3] + (110,), width=4)
    d.text((cx, cy - r - 46), "SUBSCRIBE", font=R.font("semi", 28),
           fill=R.GOLD[:3] + (215,), anchor="mm")
    d.text((cx, cy + r + 34), "यहाँ YouTube का subscribe button रखें",
           font=R.font("body", 24), fill=R.CREAM_DIM[:3] + (170,), anchor="mm")

    # two card placeholders
    for (box, data) in ((CARD_L, PREV_VIDEO), (CARD_R, NEXT_EPISODE)):
        x0, y0, x1, y1 = box
        d.rounded_rectangle([x0, y0, x1, y1], radius=14, outline=R.GOLD[:3] + (85,), width=3,
                            fill=(10, 8, 6, 120))
        d.text((x0 + 34, y0 + 30), data["kicker"], font=R.font("semi", 24),
               fill=R.GOLD[:3] + (225,))
        f = R.font("heading", 40)
        lines = R.wrap(data["title"], f, x1 - x0 - 68)
        yy = y0 + 78
        for ln in lines[:2]:
            d.text((x0 + 34, yy), ln, font=f, fill=R.CREAM[:3] + (245,))
            yy += 54
        d.text((x0 + 34, y1 - 56), data["meta"], font=R.font("body", 26),
               fill=R.CREAM_DIM[:3] + (200,))

    # bottom strip
    d.line([(148, 1030), (WIDTH - 148, 1030)], fill=R.CREAM[:3] + (30,), width=1)
    d.text((148, 1044), "हर हफ़्ते एक किताब, आसान हिंदी में", font=R.font("body", 26),
           fill=R.CREAM_DIM[:3] + (185,))
    d.text((WIDTH - 148, 1044), HANDLE, font=R.font("semi", 26), fill=R.GOLD[:3] + (200,), anchor="ra")
    return im


# ---------------------------------------------------------------------------
# subtitles: burn-time steady captions (Devanagari already shaped by PIL)
# ---------------------------------------------------------------------------
def caption_band(plate: Image.Image, text_lines: list[str], active: int | None = None) -> Image.Image:
    """Transparent overlay: dark band + caption. The `active` line is lit in warm
    gold, the other dimmed — captions get a karaoke rhythm instead of sitting
    there unchanged for five seconds."""
    im = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    band_h = 250
    top = HEIGHT - band_h
    grad = Image.new("L", (1, band_h), 0)
    for y in range(band_h):
        grad.putpixel((0, y), int(240 * min(1.0, (y / band_h) ** 1.4)))
    band = Image.new("RGBA", (WIDTH, band_h), (9, 7, 5, 255))
    band.putalpha(grad.resize((WIDTH, band_h)))
    im.alpha_composite(band, (0, top))

    d = ImageDraw.Draw(im, "RGBA")
    f = R.font("heading", 58)
    while f.size > 36 and max(f.getlength(l) for l in text_lines) > WIDTH - 380:
        f = R.font("heading", f.size - 2)
    y = top + (74 if len(text_lines) == 1 else 62)
    for i, line in enumerate(text_lines):
        is_active = (active is None) or (i == active)
        fill = (255, 240, 205, 255) if is_active else (206, 194, 176, 205)
        size = f if is_active else R.font("heading", int(f.size * 0.92))
        d.text((WIDTH // 2, y), line, font=size, fill=fill, anchor="ma",
               stroke_width=5, stroke_fill=(8, 6, 4, 220))
        y += int(f.size * (1.34 if len(text_lines) == 2 else 1.0))
    return im


def caption_timeline(sc: dict, ndur: float) -> list[tuple[str, float, float]]:
    """Captions for one scene as (text, start, end) in scene-local seconds.

    Two formats supported:
      captions=[...]                      -> evenly spread across the narration
      captions=[(start, end, "..."), ...] -> explicit sentence-level timing
    In both cases the *last* cue is clamped to the narration length, so a caption
    never floats past the voice into the end of the scene.
    """
    raw = sc.get("captions") or []
    if not raw:
        return []
    if isinstance(raw[0], (tuple, list)) and len(raw[0]) == 3:
        out = [(str(t[2]), float(t[0]), float(t[1])) for t in raw]
    else:
        step = ndur / len(raw)
        out = [(str(t), i * step, (i + 1) * step) for i, t in enumerate(raw)]
    fixed = []
    for text, a, b in out:
        a = max(0.0, min(a, ndur - 0.15))
        b = max(a + 0.4, min(b, ndur))
        fixed.append((text, a, b))
    return fixed


def is_timed(sc: dict) -> bool:
    """True when the scene gives explicit sentence timing for its captions."""
    raw = sc.get("captions") or []
    return bool(raw) and isinstance(raw[0], (tuple, list)) and len(raw[0]) == 3


def chunk_captions(timeline: list[tuple[str, float, float]], max_lines=2):
    """Group the (text, start, end) cues into 1-2 line display chunks that share
    one on-screen window (the second line lights up mid-chunk)."""
    chunks = []
    n = len(timeline)
    for i in range(0, n, max_lines):
        group = timeline[i:i + max_lines]
        # A trailing single caption (odd count) shares its window with the pair
        # before it, so the last line doesn't flash for a sliver of the scene.
        if len(group) == 1 and chunks and max_lines == 2 \
                and len(chunks[-1]["lines"]) < 2:
            chunks[-1] = dict(lines=chunks[-1]["lines"] + [group[0][0]],
                              start=chunks[-1]["start"], end=group[0][2],
                              lines_at=chunks[-1]["lines_at"] + [group[0][1]])
            continue
        chunks.append(dict(lines=[g[0] for g in group],
                           start=group[0][1], end=group[-1][2],
                           lines_at=[g[1] for g in group]))
    return chunks


def fit_caption_chunks(captions: list[str], max_lines=2):
    """Greedy: pack caption strings into at most two display lines."""
    chunks, cur = [], []
    for c in captions:
        cur.append(c)
        if len(cur) == max_lines:
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    return chunks


# ---------------------------------------------------------------------------
# 4. scene render
# ---------------------------------------------------------------------------

def detect_cuts(audio_path: str, min_seg=3.2, max_cuts=4) -> list[float]:
    """Sentence pauses in the narration, so the picture can cut to a new framing
    exactly when the voice breathes (a real editor's punch-in)."""
    out = run([FF, "-hide_banner", "-i", audio_path, "-af",
               "silencedetect=noise=-35dB:d=0.28", "-f", "null", "-"])
    starts = [float(l.split("silence_start:")[1].strip())
              for l in out.splitlines() if "silence_start:" in l]
    ends = [float(l.split("silence_end:")[1].split("|")[0].strip())
            for l in out.splitlines() if "silence_end:" in l]
    cues = [(a + b) / 2 for a, b in zip(starts[1:], ends) if a > 0.6]
    picked = []
    for c in cues:
        if not picked or c - picked[-1] >= min_seg:
            picked.append(c)
    return picked[:max_cuts]


def punch_segments(dur: float, cuts: list[float]) -> list[tuple[float, float]]:
    """Cut points -> (start, end) segments; anything under 2.2 s merges back into
    the previous segment so the edit never turns choppy."""
    bounds = [0.0] + sorted({max(1.6, min(dur - 1.6, round(c, 2))) for c in cuts}) + [dur]
    segs = []
    for a, b in zip(bounds, bounds[1:]):
        if b - a < 1e-3:
            continue
        if segs and (b - a) < 2.2:
            segs[-1] = (segs[-1][0], b)
        else:
            segs.append((a, b))
    return segs


def motion_expr(motion: str, frames: int):
    if motion == "zoom_in":
        return "z='min(1.0015+0.0016*on,1.16)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
    if motion == "zoom_out":
        return "z='max(1.16-0.0016*on,1.001)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
    if motion == "pan_left":
        return "z=1.14:x='(iw-iw/zoom)*(1-on/{n})':y='ih/2-(ih/zoom/2)'".format(n=frames)
    if motion == "pan_right":
        return "z=1.14:x='(iw-iw/zoom)*(on/{n})':y='ih/2-(ih/zoom/2)'".format(n=frames)
    return "z=1.02:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"


def render_scene(idx: int, sc: dict) -> str:
    sid = sc["id"]
    if sc.get("kind") == "endscreen":
        ndur = sc.get("fixed_dur", 12.0)
        dur = ndur
    else:
        narr = os.path.join(AUDIO, f"narr_{idx + 1:02d}_{sid}.mp3")
        ndur = probe(narr)
        dur = sc["pad_in"] + ndur + sc["pad_out"]
    frames = int(round(dur * FPS))

    plate_path = os.path.join(WORK, f"plate_{idx + 1:02d}_{sid}.png")
    if sc.get("kind") == "endscreen":
        build_plate(os.path.join(ROOT, sc["image"]), plate_path, scrim="none",
                    dark=0.66, blur=3.0)
    else:
        build_plate(os.path.join(ROOT, sc["image"]), plate_path, scrim="left")
    plate = Image.open(plate_path).convert("RGBA")

    # --- pre-render every distinct overlay state to PNG ---
    overlays = []  # (start_sec, end_sec, png)
    if sc.get("kind") == "endscreen":
        png = os.path.join(WORK, "endscreen.png")
        endscreen_layer(idx).save(png)
        overlays.append((0.0, dur + 1.0, png))
        caps = []
    else:
        caps = chunk_captions(caption_timeline(sc, ndur),
                             max_lines=1 if is_timed(sc) else 2)
    for ci, ch in enumerate(caps):
        for li, line in enumerate(ch["lines"]):
            start = sc["pad_in"] + (ch["lines_at"][li] if ch["lines_at"] else ch["start"])
            end = sc["pad_in"] + (ch["lines_at"][li + 1]
                                  if li + 1 < len(ch["lines_at"]) else ch["end"])
            png = os.path.join(WORK, f"cap_{idx + 1:02d}_{ci:02d}_{li}.png")
            caption_band(plate, ch["lines"], active=li).save(png)
            overlays.append((start, end + 0.001, png))

    for ci, card in enumerate(sc["cards"]):
        start = sc["pad_in"] + card["start"]
        end = sc["pad_in"] + min(card["end"], ndur + 0.001)
        png = os.path.join(WORK, f"card_{idx + 1:02d}_{ci:02d}.png")
        card_layer(plate, card, idx).save(png)
        overlays.append((start, end, png))

    # --- base motion: one clip per punch-in segment, then concat -------------
    # Alternating framing (wide / 30% tighter + a touch brighter) reads as real
    # editing instead of one long slide over a still.
    base_mp4 = os.path.join(WORK, f"base_{idx + 1:02d}_{sid}.mp4")
    if sc.get("kind") == "endscreen":
        segs = [(0.0, dur)]
    else:
        cuts = detect_cuts(os.path.join(AUDIO, f"narr_{idx + 1:02d}_{sid}.mp3"))
        segs = punch_segments(dur, [c + sc["pad_in"] for c in cuts])

    if len(segs) == 1:
        run([FF, "-hide_banner", "-loglevel", "error", "-y", "-loop", "1", "-i", plate_path,
             "-t", f"{dur:.3f}", "-vf",
             f"scale=2688:-2,zoompan={motion_expr(sc['motion'], frames)}:d={frames}:"
             f"s={WIDTH}x{HEIGHT}:fps={FPS},format=yuv420p",
             "-c:v", "libx264", "-preset", BUILD_PRESET, "-crf", "20", base_mp4])
    else:
        seg_files = []
        for si, (a, b) in enumerate(segs):
            n = max(2, int(round((b - a) * FPS)))
            tighter = (si % 2 == 1)
            z0 = 1.30 if tighter else 1.0
            z1 = z0 + 0.05
            expr = (f"z='{z0}+({z1 - z0:.4f})*on/{n}':"
                    f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'")
            out_seg = os.path.join(WORK, f"seg_{idx + 1:02d}_{si}.mp4")
            run([FF, "-hide_banner", "-loglevel", "error", "-y", "-loop", "1", "-i", plate_path,
                 "-t", f"{b - a:.3f}", "-vf",
                 f"scale=3100:-2,zoompan={expr}:d={n}:s={WIDTH}x{HEIGHT}:fps={FPS},"
                 f"eq=brightness={0.035 if tighter else -0.012}:"
                 f"saturation={1.06 if tighter else 0.98},format=yuv420p",
                 "-c:v", "libx264", "-preset", BUILD_PRESET, "-crf", "20", out_seg])
            seg_files.append(out_seg)
        seg_list = os.path.join(WORK, f"seglist_{idx + 1:02d}.txt")
        with open(seg_list, "w") as f:
            for sf in seg_files:
                f.write(f"file '{sf}'\n")
        run([FF, "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0",
             "-i", seg_list, "-c", "copy", base_mp4])

    # --- overlay pass ---
    args = [FF, "-hide_banner", "-loglevel", "error", "-y", "-i", base_mp4]
    for _, _, png in overlays:
        args += ["-i", png]
    chain = []
    last = "0:v"
    for i, (start, end, _) in enumerate(overlays, start=1):
        outl = f"v{i}"
        chain.append(
            f"[{last}][{i}:v]overlay=0:0:enable='between(t,{start:.3f},{end:.3f})'[{outl}]")
        last = outl
    chain.append(f"[{last}]format=yuv420p[v]")
    scn_mp4 = os.path.join(WORK, f"scene_{idx + 1:02d}_{sid}.mp4")
    args += ["-filter_complex", ";".join(chain), "-map", "[v]",
             "-c:v", "libx264", "-preset", BUILD_PRESET, "-crf", "19", "-pix_fmt", "yuv420p", scn_mp4]
    run(args)
    return scn_mp4, ndur, scn_mp4


# ---------------------------------------------------------------------------
# 5. music bed  (synthesised locally, no downloads; confirm usage rights separately)
# ---------------------------------------------------------------------------
def synth_music_safe(duration: float, dst: str):
    """synth_music but piping PCM through ffmpeg stdin."""
    sr = 44100
    n = int(duration * sr)
    t = np.arange(n) / sr
    out = np.zeros(n, dtype=np.float32)
    key = 110.0
    bpm = 64.0
    roots = [key, key * 0.8, key * 1.2, key * 0.9]
    bar = 60.0 / bpm * 4
    for k, f0 in enumerate(roots):
        seg = (t >= k * bar) & (t < (k + 1) * bar + 0.6)
        if not seg.any():
            continue
        cnt = int(seg.sum())
        env = np.ones(cnt, dtype=np.float32)
        fade = min(int(0.5 * sr), cnt // 2)
        env[:fade] = np.linspace(0, 1, fade)
        env[-fade:] = np.linspace(1, 0, fade)
        tt = t[seg] - t[seg][0]
        pad = (np.sin(2 * np.pi * f0 * tt) * 0.5 +
               np.sin(2 * np.pi * f0 * 1.5 * tt) * 0.22 +
               np.sin(2 * np.pi * f0 * 2.0 * tt) * 0.10 +
               np.sin(2 * np.pi * f0 * 0.5 * tt) * 0.18)
        out[seg] += (pad * env * 0.20).astype(np.float32)

    rng = np.random.default_rng(7)
    notes = [1.0, 1.5, 1.2, 2.0, 1.5, 1.0, 1.8, 1.2]
    step = 60.0 / bpm
    pos, k = 0.0, 0
    seg_n = int(1.6 * sr)
    tt = np.arange(seg_n) / sr
    env = np.exp(-tt * 2.6).astype(np.float32)
    while pos < duration:
        f = key * notes[k % len(notes)] * 2
        tone = (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * f * 2 * tt)).astype(np.float32)
        amp = 0.15 * (0.75 + 0.25 * rng.random())
        start = int(pos * sr)
        m = max(0, min(seg_n, n - start))
        out[start:start + m] += tone[:m] * env[:m] * amp
        pos += step * 2
        k += 1

    pos = 0.0
    seg_n = int(0.5 * sr)
    tt = np.arange(seg_n) / sr
    env = np.exp(-tt * 9).astype(np.float32)
    thump = (np.sin(2 * np.pi * 52 * tt) * 0.55).astype(np.float32)
    while pos < duration:
        start = int(pos * sr)
        m = max(0, min(seg_n, n - start))
        out[start:start + m] += thump[:m] * env[:m] * 0.15
        pos += 60.0 / bpm * 2

    # soft frame-drum tick every 4 beats: gives the bed a pulse without fighting
    # speech
    seg_n = int(0.18 * sr)
    tt = np.arange(seg_n) / sr
    env = np.exp(-tt * 22).astype(np.float32)
    tick = (np.sin(2 * np.pi * 1180 * tt) * 0.35 +
            np.sin(2 * np.pi * 1730 * tt) * 0.15).astype(np.float32)
    pos = 0.0
    while pos < duration:
        start = int(pos * sr)
        m = max(0, min(seg_n, n - start))
        out[start:start + m] += tick[:m] * env[:m] * 0.10
        pos += 60.0 / bpm * 4

    # slow riser into the final 12 s (the end-screen hand-off)
    riser_len = 3.0
    rs = int(riser_len * sr)
    if rs < n:
        tt = np.arange(rs) / sr
        sweep = np.sin(2 * np.pi * (180 + 520 * tt / riser_len) * tt) * (tt / riser_len) ** 2
        out[n - rs:] += (sweep * 0.09).astype(np.float32)

    # one-pole low-pass via lfilter-free recursion (vectorised approximation)
    b = 0.10
    lp = np.empty_like(out)
    from scipy import signal  # optional
    lp = signal.lfilter([b], [1, -(1 - b)], out).astype(np.float32)

    left = lp
    right = np.roll(lp, int(0.011 * sr)) * 0.96
    stereo = np.stack([left, right], axis=1)
    peak = float(np.max(np.abs(stereo))) or 1.0
    stereo = stereo / peak * 0.60
    fade = int(2.0 * sr)
    stereo[:fade] *= np.linspace(0, 1, fade)[:, None]
    stereo[-fade:] *= np.linspace(1, 0, fade)[:, None]
    pcm = (np.clip(stereo, -1, 1) * 32767).astype(np.int16).tobytes()
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    p = subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y", "-f", "s16le", "-ar",
                        "44100", "-ac", "2", "-i", "pipe:0", "-c:a", "libmp3lame", "-b:a", "192k", dst],
                       input=pcm, capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.decode()[-2000:])
    return dst


def load_episode(path: str):
    """Load an episode module and point the renderer at its audio/art."""
    global SCENES, SERIES, NEXT_EPISODE, PREV_VIDEO, AUDIO, EPISODE_SLUG, EPISODE_TITLE, WORK, MUSIC
    import importlib.util
    spec = importlib.util.spec_from_file_location("episode_mod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    ep = mod.EPISODE
    SCENES = ep["scenes"]
    SERIES = ep.get("series", SERIES)
    NEXT_EPISODE = ep.get("next_episode", NEXT_EPISODE)
    PREV_VIDEO = ep.get("prev_video", PREV_VIDEO)
    EPISODE_SLUG = ep.get("slug", EPISODE_SLUG)
    EPISODE_TITLE = ep.get("title", EPISODE_TITLE)
    WORK = os.path.join(WORK_ROOT, EPISODE_SLUG)
    MUSIC = os.path.join(WORK, "bed.mp3")
    AUDIO = os.path.join(ROOT, "assets", "audio", ep.get("audio_dir", "ep2")) \
        if ep.get("audio_dir", "ep2") else os.path.join(ROOT, "assets", "audio")
    print(f"episode: {EPISODE_TITLE}  ({len(SCENES)} scenes, audio: {os.path.relpath(AUDIO, ROOT)})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", action="store_true", help="render QA stills only")
    ap.add_argument("--only", default="", help="comma separated scene ids")
    ap.add_argument("--out", default="")
    ap.add_argument("--episode", default="", help="episode module, e.g. video/episode02.py")
    ap.add_argument("--remux", action="store_true",
                    help="reuse out/_work/joined.mp4 and only rebuild the audio mix")
    args = ap.parse_args()

    if args.episode:
        load_episode(os.path.join(ROOT, args.episode) if not os.path.isabs(args.episode)
                     else args.episode)
    out_rel = args.out or f"out/deep-explains-{EPISODE_SLUG}.mp4"

    os.makedirs(WORK, exist_ok=True)
    only = {s for s in args.only.split(",") if s}

    if args.stills:
        stills_dir = os.path.join(OUT, "stills", EPISODE_SLUG)
        os.makedirs(stills_dir, exist_ok=True)
        for idx, sc in enumerate(SCENES):
            if only and sc["id"] not in only:
                continue
            # --only refreshes the selected scene; don't leave older captions
            # from this episode in the QA folder after re-recording its voice.
            for old in glob.glob(os.path.join(stills_dir, f"{idx + 1:02d}_*.jpg")):
                os.remove(old)
            plate_path = os.path.join(WORK, f"plate_{idx + 1:02d}_{sc['id']}.png")
            build_plate(os.path.join(ROOT, sc["image"]), plate_path,
                        scrim="none" if sc.get("kind") == "endscreen" else "left",
                        dark=0.66 if sc.get("kind") == "endscreen" else 0.0,
                        blur=3.0 if sc.get("kind") == "endscreen" else 0.0)
            plate = Image.open(plate_path).convert("RGBA")
            if sc.get("kind") == "endscreen":
                Image.alpha_composite(plate, endscreen_layer(idx)).convert("RGB").save(
                    os.path.join(stills_dir, f"{idx + 1:02d}_endscreen.jpg"), quality=88)
                print("still ok endscreen")
                continue
            for ci, card in enumerate(sc["cards"]):
                overlay = card_layer(plate, card, idx)
                narr_st = os.path.join(AUDIO, f"narr_{idx + 1:02d}_{sc['id']}.mp3")
                nd_st = probe(narr_st) if os.path.exists(narr_st) else 6.0
                for k, chunk in enumerate(chunk_captions(
                        caption_timeline(sc, nd_st),
                        max_lines=1 if is_timed(sc) else 2)):
                    img2 = Image.alpha_composite(overlay, caption_band(plate, chunk["lines"]))
                    Image.alpha_composite(plate, img2).convert("RGB").save(
                        os.path.join(stills_dir, f"{idx + 1:02d}_{sc['id']}_c{ci}_cap{k}.jpg"),
                        quality=88)
            print("still ok", sc["id"])
        return

    joined = os.path.join(WORK, "joined.mp4")
    if args.remux:
        if not os.path.exists(joined):
            sys.exit("no joined.mp4 to remux — run a full build first")
        return mix_final(joined, out_rel)

    rendered, total = [], 0.0
    for idx, sc in enumerate(SCENES):
        if only and sc["id"] not in only:
            continue
        path, ndur, _ = render_scene(idx, sc)
        rendered.append(path)
        total += ndur if sc.get("kind") == "endscreen" else sc["pad_in"] + ndur + sc["pad_out"]
        print(f"scene {idx + 1}/{len(SCENES)} {sc['id']:10s} {ndur:6.2f}s")
    if only:
        return

    # concat
    lst = os.path.join(WORK, "concat.txt")
    with open(lst, "w") as f:
        for p in rendered:
            f.write(f"file '{p}'\n")
    run([FF, "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst,
         "-c", "copy", joined])
    return mix_final(joined, out_rel)


def mix_final(joined: str, out_rel: str) -> str:
    """Narration timeline + synthesised bed -> broadcast-ish stereo mix."""
    delays, t0, total_dur = [], 0.0, 0.0
    for idx, sc in enumerate(SCENES):
        if sc.get("kind") == "endscreen":
            t0 += sc.get("fixed_dur", 18.0)
            continue
        narr = os.path.join(AUDIO, f"narr_{idx + 1:02d}_{sc['id']}.mp3")
        delays.append((narr, t0 + sc["pad_in"]))
        t0 += sc["pad_in"] + probe(narr) + sc["pad_out"]
    total_dur = t0

    bed = synth_music_safe(total_dur + 2.0, MUSIC)

    cmd = [FF, "-hide_banner", "-loglevel", "error", "-y", "-i", joined]
    for narr, _ in delays:
        cmd += ["-i", narr]
    cmd += ["-stream_loop", "-1", "-i", bed]

    chains, n = [], len(delays)
    for i, (_, start) in enumerate(delays):
        ms = int(round(start * 1000))
        # narration polish: rumble out, presence lift, gentle levelling
        chains.append(
            f"[{i + 1}:a]aresample=48000,highpass=f=85,lowpass=f=15000,"
            f"equalizer=f=190:t=q:w=1.0:g=1.6,equalizer=f=3200:t=q:w=1.2:g=1.4,"
            f"acompressor=threshold=-19dB:ratio=2.6:attack=8:release=180:makeup=2,"
            f"volume=1.0,adelay={ms}|{ms}[n{i}]")
    chains.append("".join(f"[n{i}]" for i in range(n)) +
                  f"amix=inputs={n}:normalize=0:dropout_transition=0,"
                  f"asplit=2[voice][key]")
    chains.append(f"[{n + 1}:a]volume=0.55,atrim=0:{total_dur + 0.5:.2f},highpass=f=40,"
                  f"lowpass=f=5200,asplit=2[bedraw][bedfloor]")
    # ducked copy follows the voice; the floor copy is never gated, so music
    # keeps playing through pauses and behind the end screen
    chains.append("[bedraw][key]sidechaincompress=threshold=0.010:ratio=6:"
                  "attack=25:release=380:makeup=1[bedduck]")
    chains.append("[bedduck][bedfloor]amix=inputs=2:normalize=0:dropout_transition=0,"
                  "volume=0.55[bed]")
    chains.append("[voice][bed]amix=inputs=2:normalize=0:dropout_transition=0,"
                  "loudnorm=I=-14:TP=-1.5:LRA=11,"
                  "aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,"
                  "alimiter=limit=0.94[aout]")

    final = os.path.join(ROOT, out_rel)
    os.makedirs(os.path.dirname(final), exist_ok=True)
    # The earlier episodes copied the intermediate video bitstream, which is
    # ~66 MB for four minutes. A compact final H.264 encode stays at 1080p and
    # makes shipping four additional finished episodes practical in Git.
    video_args = (["-c:v", "libx264", "-preset", "medium", "-crf", "26",
                   "-pix_fmt", "yuv420p"] if COMPACT else ["-c:v", "copy"])
    run(cmd + ["-filter_complex", ";".join(chains), "-map", "0:v", "-map", "[aout]"]
        + video_args + ["-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                        "-t", f"{total_dur:.3f}",
                        "-movflags", "+faststart", final])
    print("WROTE", final, f"{total_dur:.1f}s")
    return final


if __name__ == "__main__":
    main()
