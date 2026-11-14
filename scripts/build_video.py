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
import json
import math
import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "video"))
from storyboard import SCENES, BRAND, SERIES, FPS, WIDTH, HEIGHT  # noqa: E402
import render_lib as R  # noqa: E402

ROOT = R.ROOT
OUT = os.path.join(ROOT, "out")
AUDIO = os.path.join(ROOT, "assets", "audio")
MUSIC = os.path.join(ROOT, "assets", "music", "bed.mp3")
WORK = os.path.join(OUT, "_work")


def ffmpeg_exe() -> str:
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


FF = ffmpeg_exe()


def run(cmd: list[str], quiet=True):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        sys.stderr.write(" ".join(cmd)[:400] + "\n" + (p.stderr or "")[-3000:])
        raise RuntimeError("ffmpeg failed")
    return p.stderr


def probe(path: str) -> float:
    out = run([FF, "-hide_banner", "-i", path, "-f", "null", "-"])
    for line in out.splitlines():
        if "time=" in line and "Duration" not in line:
            stamp = line.split("time=")[1].split()[0]
            h, m, s = stamp.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    dur = [l for l in out.splitlines() if "Duration:" in l][0]
    hms = dur.split("Duration:")[1].split(",")[0].strip()
    h, m, s = hms.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


# ---------------------------------------------------------------------------
# 2. plate: photo -> graded 1920x1080 base
# ---------------------------------------------------------------------------
def build_plate(src: str, dst: str, scrim="left", grade=0.30):
    img = Image.open(src).convert("RGB")
    # cover-crop
    sw, sh = img.size
    scale = max(WIDTH / sw, HEIGHT / sh) * 1.06
    img = img.resize((int(sw * scale), int(sh * scale)), Image.LANCZOS)
    left = (img.width - WIDTH) // 2
    top = (img.height - HEIGHT) // 2
    img = img.crop((left, top, left + WIDTH, top + HEIGHT))
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
# subtitles: burn-time steady captions (Devanagari already shaped by PIL)
# ---------------------------------------------------------------------------
def caption_band(plate: Image.Image, text_lines: list[str]) -> Image.Image:
    """Transparent overlay: dark band + burned-in caption (RGBA)."""
    im = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    band_h = 250
    top = HEIGHT - band_h
    grad = Image.new("L", (1, band_h), 0)
    for y in range(band_h):
        grad.putpixel((0, y), int(238 * min(1.0, (y / band_h) ** 1.4)))
    band = Image.new("RGBA", (WIDTH, band_h), (9, 7, 5, 255))
    band.putalpha(grad.resize((WIDTH, band_h)))
    im.alpha_composite(band, (0, top))

    d = ImageDraw.Draw(im, "RGBA")
    f = R.font("heading", 56)
    while f.size > 36 and max(f.getlength(l) for l in text_lines) > WIDTH - 380:
        f = R.font("heading", f.size - 2)
    y = top + 78
    for line in text_lines:
        d.text((WIDTH // 2, y), line, font=f, fill=(252, 247, 238, 255), anchor="ma",
               stroke_width=5, stroke_fill=(8, 6, 4, 220))
        y += int(f.size * 1.30)
    return im


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
    narr = os.path.join(AUDIO, f"narr_{idx + 1:02d}_{sid}.mp3")
    ndur = probe(narr)
    dur = sc["pad_in"] + ndur + sc["pad_out"]
    frames = int(round(dur * FPS))

    plate_path = os.path.join(WORK, f"plate_{idx + 1:02d}_{sid}.png")
    build_plate(os.path.join(ROOT, sc["image"]), plate_path, scrim="left")
    plate = Image.open(plate_path).convert("RGBA")

    # --- pre-render every distinct overlay state to PNG ---
    caps = fit_caption_chunks(sc["captions"])
    cap_dur = (ndur) / len(caps)
    overlays = []  # (start_sec, end_sec, png)
    for ci, chunk in enumerate(caps):
        start = sc["pad_in"] + ci * cap_dur
        end = start + cap_dur
        png = os.path.join(WORK, f"cap_{idx + 1:02d}_{ci:02d}.png")
        caption_band(plate, chunk).save(png)
        overlays.append((start, end, png))

    for ci, card in enumerate(sc["cards"]):
        start = sc["pad_in"] + card["start"]
        end = sc["pad_in"] + min(card["end"], ndur + 0.001)
        png = os.path.join(WORK, f"card_{idx + 1:02d}_{ci:02d}.png")
        card_layer(plate, card, idx).save(png)
        overlays.append((start, end, png))

    # --- base motion pass ---
    base_mp4 = os.path.join(WORK, f"base_{idx + 1:02d}_{sid}.mp4")
    run([FF, "-hide_banner", "-loglevel", "error", "-y", "-loop", "1", "-i", plate_path,
         "-t", f"{dur:.3f}", "-vf",
         f"scale=2688:-2,zoompan={motion_expr(sc['motion'], frames)}:d={frames}:s={WIDTH}x{HEIGHT}:fps={FPS},"
         f"format=yuv420p", "-c:v", "libx264", "-preset", "medium", "-crf", "20", base_mp4])

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
             "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", scn_mp4]
    run(args)
    return scn_mp4, ndur, scn_mp4


# ---------------------------------------------------------------------------
# 5. music bed  (synthesised locally: no licensing issues, no downloads)
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", action="store_true", help="render QA stills only")
    ap.add_argument("--only", default="", help="comma separated scene ids")
    ap.add_argument("--out", default="out/deep-explains-babylon-niyam-1.mp4")
    ap.add_argument("--remux", action="store_true",
                    help="reuse out/_work/joined.mp4 and only rebuild the audio mix")
    args = ap.parse_args()

    os.makedirs(WORK, exist_ok=True)
    only = {s for s in args.only.split(",") if s}

    if args.stills:
        os.makedirs(os.path.join(OUT, "stills"), exist_ok=True)
        for idx, sc in enumerate(SCENES):
            if only and sc["id"] not in only:
                continue
            plate_path = os.path.join(WORK, f"plate_{idx + 1:02d}_{sc['id']}.png")
            build_plate(os.path.join(ROOT, sc["image"]), plate_path)
            plate = Image.open(plate_path).convert("RGBA")
            for ci, card in enumerate(sc["cards"]):
                overlay = card_layer(plate, card, idx)
                for k, chunk in enumerate(fit_caption_chunks(sc["captions"])):
                    img2 = Image.alpha_composite(overlay, caption_band(plate, chunk))
                    Image.alpha_composite(plate, img2).convert("RGB").save(
                        os.path.join(OUT, "stills", f"{idx + 1:02d}_{sc['id']}_c{ci}_cap{k}.jpg"),
                        quality=88)
            print("still ok", sc["id"])
        return

    joined = os.path.join(WORK, "joined.mp4")
    if args.remux:
        if not os.path.exists(joined):
            sys.exit("no joined.mp4 to remux — run a full build first")
        return mix_final(joined, args.out)

    rendered, total = [], 0.0
    for idx, sc in enumerate(SCENES):
        if only and sc["id"] not in only:
            continue
        path, ndur, _ = render_scene(idx, sc)
        rendered.append(path)
        total += sc["pad_in"] + ndur + sc["pad_out"]
        print(f"scene {idx + 1}/{len(SCENES)} {sc['id']:9s} {ndur:6.2f}s")
    if only:
        return

    # concat
    lst = os.path.join(WORK, "concat.txt")
    with open(lst, "w") as f:
        for p in rendered:
            f.write(f"file '{p}'\n")
    run([FF, "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst,
         "-c", "copy", joined])
    return mix_final(joined, args.out)


def mix_final(joined: str, out_rel: str) -> str:
    """Narration timeline + synthesised bed -> broadcast-ish stereo mix."""
    delays, t0, total_dur = [], 0.0, 0.0
    for idx, sc in enumerate(SCENES):
        narr = os.path.join(AUDIO, f"narr_{idx + 1:02d}_{sc['id']}.mp3")
        delays.append((narr, t0 + sc["pad_in"]))
        t0 += sc["pad_in"] + probe(narr) + sc["pad_out"]
    total_dur = t0

    bed = synth_music_safe(total_dur + 1.0, MUSIC)

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
                  f"amix=inputs={n}:normalize=0:dropout_transition=0[narr]")
    chains.append(f"[{n + 1}:a]volume=0.13,atrim=0:{total_dur:.2f},"
                  f"highpass=f=40[bed]")
    chains.append("[narr][bed]amix=inputs=2:normalize=0:dropout_transition=0,"
                  "loudnorm=I=-14:TP=-1.5:LRA=9,"
                  "aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,"
                  "alimiter=limit=0.94[aout]")

    final = os.path.join(ROOT, out_rel)
    os.makedirs(os.path.dirname(final), exist_ok=True)
    run(cmd + ["-filter_complex", ";".join(chains), "-map", "0:v", "-map", "[aout]",
               "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
               "-movflags", "+faststart", "-shortest", final])
    print("WROTE", final, f"{total_dur:.1f}s")
    return final


if __name__ == "__main__":
    main()
