#!/usr/bin/env python3
"""
make_thumbnail.py — 1280x720 YouTube thumbnail in the fixed "Deep Explains"
series template (gold type, left-aligned, subject on the right).

Run: python scripts/make_thumbnail.py
Out: out/thumbnail-1280x720.jpg  (+ .png for editing)
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_lib as R

ROOT = R.ROOT
W, H = 1280, 720
OUT = os.path.join(ROOT, "out")


def make(src, headline, badge, kicker, dst, flip=False, zoom=1.02,
         focus=(0.5, 0.5), target=(0.5, 0.5), max_lines=2):
    img = Image.open(src).convert("RGB")
    sw, sh = img.size
    scale = max(W / sw, H / sh) * zoom
    img = img.resize((int(sw * scale), int(sh * scale)), Image.LANCZOS)
    # keep the subject's face (focus) pinned to the target point on the frame
    left = int(img.width * focus[0] - W * target[0])
    top = int(img.height * focus[1] - H * target[1])
    left = max(0, min(img.width - W, left))
    top = max(0, min(img.height - H, top))
    img = img.crop((left, top, left + W, top + H))
    if flip:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)

    img = R.vignette(img, amount=120).convert("RGBA")
    # scrim strong on the left third
    scrim = R.vertical_scrim((W, H), side="left", strength=252, power=2.6)
    img = Image.alpha_composite(img, scrim)
    img = Image.alpha_composite(img, R.vertical_scrim((W, H), side="bottom", strength=150, power=2.6))

    d = ImageDraw.Draw(img, "RGBA")

    # kicker
    x = 64
    R.kicker_block(d, (x, 62), kicker, size=21, track=4, rule=True)

    # headline: fits ~700px wide, 2 lines
    f = R.font("display", 190 if max_lines == 1 else 150)
    while f.size > 60:
        lines = R.wrap(headline, f, 720)
        if len(lines) <= max_lines and max(f.getlength(l) for l in lines) <= 720:
            break
        f = R.font("display", f.size - 4)

    block_h = len(lines) * int(f.size * 1.02) + (92 if badge else 0)
    y = 372 - block_h // 2
    for line in lines:
        g = R.gradient_text((0, 0), line, f, (255, 248, 232), (226, 168, 74))
        # hard shadow for small-size legibility
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sh.alpha_composite(g, (x + 3, y + 6))
        sh = Image.new("RGBA", sh.size, (0, 0, 0, 0)).point(lambda v: v) if False else sh
        alpha = sh.split()[3].filter(ImageFilter.GaussianBlur(3))
        dark = Image.new("RGBA", sh.size, (8, 5, 2, 255))
        dark.putalpha(alpha.point(lambda v: int(v * 0.85)))
        img.alpha_composite(dark)
        img.alpha_composite(g, (x - 4, y - 4))
        y += int(f.size * 1.02)

    # badge
    if badge:
        fb = R.font("display", 52)
        bw = fb.getlength(badge) + 62
        by = y + 18
        box = Image.new("RGBA", (int(bw), 92), (0, 0, 0, 0))
        bd = ImageDraw.Draw(box)
        bd.rounded_rectangle([0, 0, bw - 2, 88], radius=10, fill=(216, 166, 74, 255))
        bd.text((bw / 2, 44), badge, font=fb, fill=(22, 15, 6, 255), anchor="mm")
        img.alpha_composite(box, (x, by))

    img = Image.alpha_composite(img, R.grain((W, H), strength=6))
    img.convert("RGB").save(dst, quality=92)
    img.save(dst.replace(".jpg", ".png"))
    print("wrote", dst)


VARIANTS = {
    # A — authority: series identity, warm audience
    "A": dict(src="assets/img/02_arkad.png", headline="पहले खुद को दो", badge="10%",
              kicker="THE RICHEST MAN IN BABYLON · 1926", zoom=1.02, max_lines=1,
              focus=(0.60, 0.30), target=(0.79, 0.40)),
    # B — pain: salary disappearing, strongest for cold audiences
    "B": dict(src="assets/img/04_india.png", headline="सैलरी गई", badge="कहाँ?",
              kicker="₹40,000 · तीसरा हफ़्ता", zoom=1.16, max_lines=1,
              focus=(0.52, 0.40), target=(0.72, 0.40)),
    # C — curiosity gap: matches the video's "kami" promise
    "C": dict(src="assets/img/03_gold.png", headline="10% नियम", badge="फेल?",
              kicker="90 साल पुराना · 2026 टेस्ट", zoom=1.05, max_lines=1,
              focus=(0.5, 0.5), target=(0.70, 0.45)),
}

if __name__ == "__main__":
    import sys as _s
    os.makedirs(OUT, exist_ok=True)
    which = [a for a in _s.argv[1:] if a in VARIANTS] or list(VARIANTS)
    for key in which:
        v = dict(VARIANTS[key])
        dst = os.path.join(OUT, f"thumbnail-{key}-1280x720.jpg")
        make(os.path.join(ROOT, v.pop("src")), v.pop("headline"), v.pop("badge"),
             v.pop("kicker"), dst, **v)
