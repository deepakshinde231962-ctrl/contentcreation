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


VARIANTS_EP2 = {
    # A — pain + specificity: the "70% kharche faltu" angle
    "A": dict(src="assets/img/11_budget.png", headline="70% खर्च", badge="फालतू?", 
              kicker="NIYAM 2 · ख़र्चे काबू में", zoom=1.10, max_lines=1,
              focus=(0.52, 0.50), target=(0.74, 0.45)),
    # B — daily-life frame (subscriptions / UPI)
    "B": dict(src="assets/img/10_subscriptions.png", headline="पैसा कहाँ गया?", badge="₹72,000",
              kicker="3 आदतें · 1 साल", zoom=1.14, max_lines=1,
              focus=(0.50, 0.45), target=(0.72, 0.42)),
    # C — curiosity: the promise
    "C": dict(src="assets/img/14_notebook.png", headline="खर्च = तय", badge="किया हुआ?",
              kicker="NIYAM 2 · 2026 वर्ज़न", zoom=1.08, max_lines=1,
              focus=(0.55, 0.50), target=(0.73, 0.45)),
}

VARIANTS_EP3 = {
    # A — the time-cost angle (strongest specific claim)
    "A": dict(src="assets/img/22_old_clock.png", headline="10 साल देर", badge="= लाखों?",
              kicker="NIYAM 3 · पैसा पैसा कमाए", zoom=1.10, max_lines=1,
              focus=(0.55, 0.50), target=(0.74, 0.45)),
    # B — compounding visual, curiosity
    "B": dict(src="assets/img/21_time_chart.png", headline="₹5,000", badge="= ₹94 लाख?",
              kicker="हर महीने · 35 साल से", zoom=1.06, max_lines=1,
              focus=(0.50, 0.52), target=(0.72, 0.46)),
    # C — risk / loss frame (the "fine print" hook)
    "C": dict(src="assets/img/23_risk.png", headline="'गारंटीड'", badge="धोखा?",
              kicker="NIYAM 3 + 4 · बेबीलोन", zoom=1.08, max_lines=1,
              focus=(0.52, 0.45), target=(0.72, 0.42)),
}

VARIANTS_EP4 = {
    # A — the loss frame (strongest fear + specificity)
    "A": dict(src="assets/img/24_scam_shield.png", headline="₹25,000", badge="एक कॉल में?",
              kicker="NIYAM 4 · पैसा बचाओ", zoom=1.12, max_lines=1,
              focus=(0.42, 0.50), target=(0.72, 0.45)),
    # B — the "guaranteed" red flag
    "B": dict(src="assets/img/25_fraud_call.png", headline="'गारंटीड'", badge="4% महीना?",
              kicker="साल का 48% · ₹80,000 का वादा", zoom=1.08, max_lines=1,
              focus=(0.58, 0.50), target=(0.72, 0.44)),
    # C — the data frame (derivatives)
    "C": dict(src="assets/img/26_emergency_vault.png", headline="90% लोग", badge="खोते हैं?",
              kicker="सेबी · डेरिवेटिव डेटा", zoom=1.10, max_lines=1,
              focus=(0.55, 0.50), target=(0.73, 0.45)),
}

VARIANTS_EP5 = {
    # A — the video's first-month arithmetic (explicitly framed as an example).
    "A": dict(src="assets/img/31_debt_ledger.png", headline="₹3,000", badge="₹900 ही घटे?",
              kicker="NIYAM 5 · ₹60,000 बिल · उदाहरण", zoom=1.10, max_lines=1,
              focus=(0.65, 0.50), target=(0.80, 0.45)),
    # B — Dabasir's fictional story, not a claim of a historical clay tablet.
    "B": dict(src="assets/img/30_dabasir.png", headline="दबासीर", badge="कर्ज़ कैसे चुकाया?",
              kicker="NIYAM 5 · THE RICHEST MAN IN BABYLON", zoom=1.10, flip=True,
              max_lines=1, focus=(0.38, 0.48), target=(0.78, 0.45)),
    # C — seven payments only under the video’s stated simplified assumptions.
    "C": dict(src="assets/img/33_freedom_dawn.png", headline="7 महीने", badge="कर्ज़ ख़त्म?",
              kicker="NIYAM 5 · ₹60,000 · ₹10,000/माह · उदाहरण", zoom=1.08, max_lines=1,
              focus=(0.55, 0.52), target=(0.74, 0.45)),
}

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
    args = _s.argv[1:]
    prefix = ""
    if "--episode" in args:
        i = args.index("--episode")
        ep = args[i + 1]
        del args[i:i + 2]
        if "02" in ep:
            prefix, _ = "niyam2-", None
            globals()["VARIANTS"] = VARIANTS_EP2
        elif "03" in ep:
            prefix = "niyam3-"
            globals()["VARIANTS"] = VARIANTS_EP3
        elif "04" in ep:
            prefix = "niyam4-"
            globals()["VARIANTS"] = VARIANTS_EP4
        elif "05" in ep:
            prefix = "niyam5-"
            globals()["VARIANTS"] = VARIANTS_EP5
        else:
            prefix = ""
    which = [a for a in args if a in VARIANTS] or list(VARIANTS)
    for key in which:
        v = dict(VARIANTS[key])
        dst = os.path.join(OUT, f"thumbnail-{prefix}{key}-1280x720.jpg")
        make(os.path.join(ROOT, v.pop("src")), v.pop("headline"), v.pop("badge"),
             v.pop("kicker"), dst, **v)
