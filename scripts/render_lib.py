"""
Shared drawing helpers for the Deep Explains video pipeline.

Everything is rendered with PIL at 1920x1080, then handed to ffmpeg.
Devnagari shaping is done by Pillow's libraqm once it is available; the
drawing code here never splits a conjunct, it measures the full string.

Palette / type choices are deliberately few: one gold, one cream, one ink.
"""
from __future__ import annotations

import os
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(ROOT, "assets", "fonts")

# ---- palette --------------------------------------------------------------
INK = (14, 11, 8)
INK_SOFT = (24, 19, 14)
CREAM = (246, 239, 227)
CREAM_DIM = (214, 201, 182)
GOLD = (216, 166, 74)
GOLD_DEEP = (168, 120, 42)
TEAL = (58, 128, 128)

# ---- fonts ----------------------------------------------------------------
_FONT_FILES = {
    "display": "Mukta-ExtraBold.ttf",
    "display_bold": "Mukta-Bold.ttf",
    "heading": "Hind-Bold.ttf",
    "semi": "Hind-SemiBold.ttf",
    "body": "Hind-Regular.ttf",
}


@lru_cache(maxsize=256)
def font(role: str, size: int) -> ImageFont.FreeTypeFont:
    path = os.path.join(FONT_DIR, _FONT_FILES[role])
    return ImageFont.truetype(path, size)


# ---- primitives -----------------------------------------------------------
def vertical_scrim(size, side="left", strength=235, power=1.6):
    """Soft dark gradient used behind type so text survives any photo."""
    w, h = size
    img = Image.new("L", (w, h), 0)
    px = img.load()
    for x in range(w):
        t = 1.0 - (x / max(1, w - 1))
        v = int(strength * (t ** power))
        for y in range(h):
            px[x, y] = v
    if side == "right":
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    elif side == "bottom":
        grad = Image.new("L", (1, h))
        for y in range(h):
            grad.putpixel((0, y), int(strength * ((y / max(1, h - 1)) ** power)))
        img = grad.resize((w, h))
    elif side == "full":
        img = Image.new("L", (w, h), strength)
    scrim = Image.new("RGBA", (w, h), INK + (255,))
    scrim.putalpha(img)
    return scrim


def vignette(img: Image.Image, amount=90):
    w, h = img.size
    mask = Image.new("L", (w // 4, h // 4), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse((-w // 8, -h // 8, w // 4 + w // 8, h // 4 + h // 8), fill=255)
    mask = mask.resize((w, h), Image.LANCZOS).filter(ImageFilter.GaussianBlur(120))
    dark = Image.new("RGBA", (w, h), INK + (255,))
    dark.putalpha(mask.point(lambda v: int((255 - v) * amount / 255)))
    return Image.alpha_composite(img.convert("RGBA"), dark)


def grain(size, strength=7, seed=3):
    import numpy as np
    rng = np.random.default_rng(seed)
    w, h = size
    noise = rng.normal(128, strength, (h // 2, w // 2)).clip(0, 255).astype("uint8")
    n = Image.fromarray(noise).resize((w, h), Image.BILINEAR)
    lay = Image.merge("RGBA", (n, n, n, Image.new("L", (w, h), 16)))
    return lay


def gradient_text(size, text, fnt, top_color, bottom_color):
    """Gold-foil text: gradient fill clipped to the glyph mask."""
    pad = 8
    bbox = fnt.getbbox(text)
    w, h = bbox[2] - bbox[0] + pad * 2, bbox[3] - bbox[1] + pad * 2
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).text((pad - bbox[0], pad - bbox[1]), text, font=fnt, fill=255)
    grad = Image.new("RGB", (w, h))
    gd = ImageDraw.Draw(grad)
    for y in range(h):
        t = y / max(1, h - 1)
        gd.line([(0, y), (w, y)], fill=tuple(
            int(top_color[i] + (bottom_color[i] - top_color[i]) * t) for i in range(3)))
    out = grad.convert("RGBA")
    out.putalpha(mask)
    return out


def wrap(text, fnt, max_width):
    words = text.split()
    lines, cur = [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if fnt.getlength(trial) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, xy, lines, fnt, fill, leading=1.16, anchor="la"):
    x, y = xy
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill, anchor=anchor)
        y += int(fnt.size * leading)
    return y


def gold_rule(draw, xy, w=112, thick=4, color=GOLD):
    x, y = xy
    draw.rectangle([x, y, x + w, y + thick], fill=color)


def corner_brackets(draw, box, color=(GOLD[0], GOLD[1], GOLD[2], 120), ln=34, thick=2):
    x0, y0, x1, y1 = box
    for (cx, cy, dx, dy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        draw.line([(cx, cy), (cx + dx * ln, cy)], fill=color, width=thick)
        draw.line([(cx, cy), (cx, cy + dy * ln)], fill=color, width=thick)


def shadow_text(draw, xy, text, fnt, fill, anchor="la", alpha=150, offset=(0, 5), blur_soft=True):
    """Soft drop shadow drawn directly (cheap) then the crisp glyphs."""
    sh = Image.new("RGBA", draw._image.size, (0, 0, 0, 0)) if hasattr(draw, "_image") else None
    draw.text((xy[0] + offset[0], xy[1] + offset[1]), text, font=fnt,
              fill=(0, 0, 0, alpha), anchor=anchor)
    draw.text(xy, text, font=fnt, fill=fill, anchor=anchor)


def kicker_block(draw, xy, text, size=30, color=GOLD, track=6, rule=True):
    """Small uppercase-ish label with manual letter spacing (Latin only)."""
    x, y = xy
    fnt = font("semi", size)
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=color)
        x += fnt.getlength(ch) + track
    if rule:
        gold_rule(draw, (xy[0], y + size + 18), w=64, thick=3)
    return x
