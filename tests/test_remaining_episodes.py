"""Accuracy, editorial safety and actual upload-file checks for episodes 6–8.

Episode 9's source text and book mapping are checked here; its media tests
will be included when its separate finale narration and render are delivered.
"""
from __future__ import annotations

import importlib.util
import math
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'video'))
sys.path.insert(0, str(ROOT / 'scripts'))
from remaining_content import IDS, NARRATIONS, METADATA  # noqa: E402
from remaining_storyboards import caption_texts  # noqa: E402
from build_remaining_docs import TITLES, THUMB_WORDS  # noqa: E402
from publish import probe_dur, ffmpeg_exe  # noqa: E402

# An incremental build can validate just the completed episode via
# DEEP_TEST_FINISHED=6; the default checks every finished episode in this batch.
FINISHED = tuple(map(int, os.environ.get('DEEP_TEST_FINISHED', '6,7,8').split(',')))


class RemainingEpisodesTests(unittest.TestCase):
    def test_scripts_are_original_length_and_six_parts(self):
        for n in (6, 7, 8, 9):
            with self.subTest(ep=n):
                d = NARRATIONS[n]
                self.assertEqual(tuple(d), IDS)
                self.assertTrue(550 <= sum(len(s.split()) for s in d.values()) <= 650)
                self.assertIn('एक लाइन में:', d['outro'])
                self.assertIn('सब्सक्राइब', d['outro'])
                self.assertIn('दो हज़ार छब्बीस', d['fix1'] if n < 9 else d['fix2'])
                self.assertTrue(all(' '.join(caption_texts(t)) == t for t in d.values()))
                self.assertTrue(all('?' in t and len(t) < 60 for t in TITLES[n]))
                self.assertEqual(len(THUMB_WORDS[n]), 3)
                self.assertTrue(METADATA[n]['source'].startswith('https://en.wikisource.org/'))

    def test_book_sections_are_not_confused_with_series_numbers(self):
        self.assertIn('पाँचवाँ', NARRATIONS[6]['rule'])
        self.assertIn('छठा', NARRATIONS[7]['rule'])
        self.assertIn('सातवाँ', NARRATIONS[8]['rule'])
        ep9 = ' '.join(NARRATIONS[9].values())
        self.assertIn('नोमासीर', ep9)
        self.assertIn('काल्पनिक', ep9)
        self.assertIn('पांच सुनहरे नियम और सात इलाज', ep9)
        self.assertIn('पहला नियम', ep9)
        self.assertIn('दूसरा:', ep9)
        self.assertIn('तीसरा:', ep9)
        self.assertIn('चौथा नियम', ep9)
        self.assertIn('पांचवाँ:', ep9)
        for n in range(6, 10):
            self.assertNotIn('रातों रात अमीर हो सकते', ' '.join(NARRATIONS[n].values()))

    def test_examples_reproduce_narration_without_fake_statistics(self):
        p = 4_000_000
        r = .085 / 12
        months = 240
        emi = p * r / (1 - (1 + r)**(-months))
        self.assertAlmostEqual(emi, 34713, delta=1)
        self.assertAlmostEqual((emi*months-p)/100_000, 43.31, delta=.03)
        self.assertIn('साढ़े आठ प्रतिशत', NARRATIONS[6]['india'])
        self.assertIn('बीस साल', NARRATIONS[6]['india'])
        self.assertIn('पुणे की असली बाजार दर नहीं', NARRATIONS[6]['hook'])
        self.assertIn('अंतर को मुनाफा मत कहो', NARRATIONS[6]['india'])
        self.assertAlmostEqual(30_000*1.06**25, 128756, delta=2)
        self.assertIn('भविष्यवाणी नहीं', NARRATIONS[7]['hook'])
        self.assertIn('बिना किसी रिटर्न के', NARRATIONS[7]['india'])
        self.assertEqual(6*1000-2000, 4000)
        self.assertIn('समय, टैक्स और दूसरे खर्च', NARRATIONS[8]['india'])
        self.assertIn('आमदनी शून्य', NARRATIONS[8]['india'])
        self.assertEqual(30000*.1*12, 36000)
        self.assertIn('बिना किसी रिटर्न के', NARRATIONS[9]['limits'])
        for n in (6, 7, 8, 9):
            self.assertTrue(any(term in NARRATIONS[n]['limits']+NARRATIONS[n]['fix1']
                                for term in ('चार जगह', 'दो बड़ी सीमाएँ')))

    def test_exact_spoken_scripts_and_publish_choice_count(self):
        for n in FINISHED:
            with self.subTest(ep=n):
                script = ROOT / f'content/{15+2*(n-6):02d}-episode{n}-script.md'
                pack = ROOT / f'content/{16+2*(n-6):02d}-episode{n}-publish-pack.md'
                self.assertTrue(script.exists(), str(script))
                self.assertTrue(pack.exists(), str(pack))
                s, p = script.read_text(), pack.read_text()
                for sid in IDS:
                    self.assertIn(NARRATIONS[n][sid], s, (n, sid))
                self.assertEqual(len(re.findall(r'^\d\. `', p, flags=re.M)), 3)
                self.assertIn('📚 Sources', p)
                self.assertNotIn('EPISODE_ONE_LINK', p)
                self.assertIn('not uploaded', p)
                self.assertIn('not clickable', p)

    def test_audio_caption_short_files_and_end_screen(self):
        from PIL import Image
        ff = ffmpeg_exe()
        for n in FINISHED:
            with self.subTest(ep=n):
                module = __import__(f'episode0{n}')
                ep = module.EPISODE
                self.assertEqual(len(ep['scenes']), 9)
                self.assertEqual(ep['scenes'][-1]['fixed_dur'], 12.)
                cues = []
                at = 0.
                for i, sc in enumerate(ep['scenes'][:-1], 1):
                    f = ROOT / f'assets/audio/ep{n}/narr_{i:02d}_{sc["id"]}.mp3'
                    self.assertTrue(f.is_file(), str(f))
                    d = probe_dur(str(f))
                    captions = sc['captions']
                    self.assertEqual(' '.join(x[2] for x in captions), sc['narration'])
                    self.assertAlmostEqual(captions[0][0], 0, delta=.01)
                    self.assertAlmostEqual(captions[-1][1], d, delta=.10)
                    for a, b in zip(captions, captions[1:]):
                        self.assertAlmostEqual(a[1], b[0], delta=.01)
                        self.assertGreater(a[1]-a[0], .5)
                    self.assertTrue(all(card['start'] < card['end']
                                        and not re.search('[→≠≈]', str(card))
                                        for card in sc['cards']))
                    cues.extend(captions)
                    at += sc['pad_in'] + d + sc['pad_out']
                mp4 = ROOT / f'out/deep-explains-babylon-niyam-{n}.mp4'
                short = ROOT / f'out/short-{n}.mp4'
                srt = ROOT / f'out/deep-explains-babylon-niyam-{n}.hi.srt'
                self.assertTrue(mp4.is_file(), str(mp4))
                self.assertTrue(short.is_file(), str(short))
                self.assertTrue(srt.is_file(), str(srt))
                self.assertEqual(srt.read_text().count(' --> '), len(cues))
                self.assertTrue(205 < probe_dur(str(mp4)) < 260)
                self.assertAlmostEqual(probe_dur(str(mp4)), at + 12, delta=.45)
                self.assertTrue(20 < probe_dur(str(short)) < 35)
                for label, p, dims in (('main', mp4, '1920x1080'),
                                       ('Short', short, '1080x1920')):
                    err = subprocess.run([ff, '-hide_banner', '-i', str(p)],
                                         text=True, capture_output=True).stderr
                    self.assertIn(dims, err, (n, label))
                    self.assertIn('h264', err.lower(), (n, label))
                    self.assertIn('48000 Hz', err, (n, label))
                for v in ('A', 'B', 'C'):
                    im = ROOT / f'out/thumbnail-niyam{n}-{v}-1280x720.jpg'
                    with Image.open(im) as thumb:
                        self.assertEqual(thumb.size, (1280, 720))

    def test_shorts_beats_follow_actual_spoken_cues(self):
        for n in FINISHED:
            with self.subTest(ep=n):
                spec = __import__(f'short{n}').SHORT
                beats = spec['beats_at']
                self.assertEqual(len(beats), len(spec['beats']) + 1)
                self.assertEqual(beats[0], 0.)
                self.assertTrue(all(a < b for a, b in zip(beats, beats[1:])))
                self.assertAlmostEqual(beats[-1],
                    probe_dur(str(ROOT / spec['audio'])) + 1.2, delta=.05)


if __name__ == '__main__':
    unittest.main()
