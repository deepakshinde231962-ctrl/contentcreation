"""Regression checks for the episode 5 fact-sensitive narration and edit."""
from __future__ import annotations

from decimal import Decimal
import importlib.util
from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("episode05", ROOT / "video/episode05.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
SCENES = module.EPISODE["scenes"]


class Episode05Tests(unittest.TestCase):
    def test_original_plan_not_inverted(self):
        rule = next(s for s in SCENES if s["id"] == "rule")
        text = rule["narration"]
        # Book, chapter 9: 10% saved, 20% paid to creditors, 70% spent.
        self.assertRegex(text, r"दस प्रतिशत बचत, बीस प्रतिशत कर्ज़.*सत्तर प्रतिशत घर")
        self.assertIn("काल्पनिक", text)
        self.assertIn("सीरिया", text)
        self.assertNotIn("फ़ारस का", text)

    def test_model_reproduces_narrated_numbers(self):
        principal = Decimal("60000")
        monthly = Decimal("0.035")  # illustrative nominal monthly rate
        interest = principal * monthly
        self.assertEqual(interest, Decimal("2100"))
        self.assertEqual(principal + interest - Decimal("3000"), Decimal("59100"))
        balance = principal
        paid_interest = Decimal("0")
        payments = 0
        while balance > 0:
            this_interest = balance * monthly
            balance += this_interest
            balance -= min(balance, Decimal("10000"))
            paid_interest += this_interest
            payments += 1
            self.assertLess(payments, 30)
        self.assertEqual(payments, 7)
        self.assertEqual(round(paid_interest), Decimal("8543"))
        india = next(s for s in SCENES if s["id"] == "india")
        self.assertIn("सातवें महीने", india["narration"])
        self.assertIn("₹8,543", " ".join(str(c) for c in india["cards"]))
        self.assertIn("कोई नया खर्च, फीस या टैक्स नहीं", india["narration"])

    def test_six_parts_appropriate_length_and_no_tofu_glyphs(self):
        words = sum(len(s["narration"].split()) for s in SCENES)
        self.assertGreaterEqual(words, 550)
        self.assertLessEqual(words, 650)
        self.assertEqual(len(SCENES), 10)
        self.assertEqual(SCENES[-1]["fixed_dur"], 12.0)
        for s in SCENES[:-1]:
            for cap in s["captions"]:
                self.assertNotRegex(cap[2], r"[→≠≈]")
            for card in s["cards"]:
                self.assertNotRegex(str(card), r"[→≠≈]")

    def test_captions_match_audio_and_card_cuts(self):
        import imageio_ffmpeg
        ff = imageio_ffmpeg.get_ffmpeg_exe()
        for i, s in enumerate(SCENES[:-1], 1):
            f = ROOT / f"assets/audio/ep5/narr_{i:02d}_{s['id']}.mp3"
            self.assertTrue(f.is_file(), str(f))
            p = subprocess.run([ff, "-hide_banner", "-i", str(f)],
                               capture_output=True, text=True)
            m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", p.stderr)
            self.assertIsNotNone(m, str(f))
            dur = int(m[1])*3600 + int(m[2])*60 + float(m[3])
            caps = s["captions"]
            self.assertAlmostEqual(caps[0][0], 0, delta=.01)
            self.assertAlmostEqual(caps[-1][1], dur, delta=.12)
            for a, b in zip(caps, caps[1:]):
                self.assertAlmostEqual(a[1], b[0], delta=.02)
                self.assertGreater(a[1], a[0])
            self.assertTrue(all(any(abs(card["start"]-cap[0]) < .02
                                    for cap in caps) for card in s["cards"]))
            self.assertTrue(all(card["end"] >= card["start"]
                                for card in s["cards"]))

    def test_script_doc_is_exactly_spoken_script(self):
        doc = (ROOT / "content/13-episode5-script.md").read_text(encoding="utf-8")
        self.assertIn("**610 शब्द**", doc)
        for s in SCENES[:-1]:
            self.assertIn(s["narration"], doc, s["id"])

    def test_short_cuts_account_for_narration_delay(self):
        short_spec = importlib.util.spec_from_file_location("short5", ROOT / "video/short5.py")
        short_mod = importlib.util.module_from_spec(short_spec)
        short_spec.loader.exec_module(short_mod)
        obj = short_mod.SHORT
        self.assertEqual(len(obj["beats_at"]), len(obj["beats"]) + 1)
        self.assertEqual(obj["beats_at"][0], 0)
        self.assertTrue(all(a < b for a, b in zip(obj["beats_at"], obj["beats_at"][1:])))
        self.assertAlmostEqual(obj["beats_at"][-1], 24.36 + 1.2, delta=.10)
        self.assertGreater(obj["beats_at"][1], 2.76 + 1.2 - .05)

    def test_publish_links_are_actual_fallbacks_not_placeholders(self):
        out = subprocess.run(["python3", str(ROOT / "scripts/make_links.py"),
                              "--block", "5"], capture_output=True, text=True,
                             check=True).stdout
        self.assertEqual(len(out.strip().splitlines()), 4)
        self.assertIn("Episode 4", out)
        self.assertIn("https://www.youtube.com/", out)
        self.assertNotIn("EPISODE_FOUR_LINK", out)


if __name__ == "__main__":
    unittest.main()
