"""All nine upload files, corrected Episode 2 maths and honest Studio sheets."""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from check_release import audit  # noqa: E402
from publish import PACK, SHORT_TITLES, fields_from_pack, probe_dur, thumb_path  # noqa: E402


class ReleaseReadinessTests(unittest.TestCase):
    def test_all_nine_local_media_packages_pass(self):
        rows, issues = audit()
        self.assertEqual(issues, [], '\n'.join(issues))
        self.assertEqual(len(rows), 9)
        for ep, row in enumerate(rows, 1):
            with self.subTest(ep=ep):
                self.assertEqual(row['ep'], ep)
                self.assertGreater(row['video'], row['short'])
                self.assertGreater(row['cues'], 20)
                self.assertRegex(row['timer'], r'^\d\d:\d\d$')

    def test_publish_sheets_have_primary_titles_and_short_upload_copy(self):
        for ep in PACK:
            with self.subTest(ep=ep):
                title, desc, tags, pinned = fields_from_pack(ep)
                sheet = (ROOT / f'out/upload-{ep}.md').read_text(encoding='utf-8')
                self.assertIn(f'```\n{title}\n```', sheet)
                self.assertIn('## Short — separate Studio upload', sheet)
                self.assertIn(SHORT_TITLES[ep], sheet)
                self.assertIn(thumb_path(ep), sheet)
                self.assertIn('no upload performed by this workflow', sheet)
                for item in ('📚 Sources', 'Disclaimer:'):
                    self.assertIn(item, desc)
                self.assertTrue(tags and pinned)

    def test_episode2_expenses_are_spending_not_promised_savings(self):
        spec = importlib.util.spec_from_file_location('episode2_source', ROOT / 'video/episode02.py')
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        india = next(s for s in mod.EPISODE['scenes'] if s['id'] == 'india')
        self.assertEqual((500 + 4000 + 2000) * 12, 78000)
        self.assertIn('अठहत्तर हज़ार', india['narration'])
        self.assertIn('₹6,500/माह', str(india['cards']))
        self.assertIn('₹78,000', str(india['cards']))
        self.assertNotIn('₹72,000', str(india['cards']))
        self.assertEqual([c['big'] for c in india['cards']],
                         ['3 जगह', '₹6,000', '₹48,000', '₹2,000', '₹78,000'])
        self.assertIn('बचत का वादा नहीं', india['cards'][-1]['sub'])
        import build_video as B
        starts = [a for _, a, _ in B.caption_timeline(india, 24.)]
        for card_index, cue_index in ((2, 2), (3, 3), (4, 4)):
            self.assertAlmostEqual(india['cards'][card_index]['start'],
                                   starts[cue_index], delta=.01)
        srt = (ROOT / 'out/deep-explains-babylon-niyam-2.hi.srt').read_text(encoding='utf-8')
        short_source = (ROOT / 'video/short2.py').read_text(encoding='utf-8')
        self.assertIn('₹78,000', srt)
        self.assertIn('₹78,000', short_source)
        self.assertNotIn('₹72,000', srt + short_source)
        self.assertAlmostEqual(probe_dur(str(ROOT / 'assets/audio/ep2/narr_04_india.mp3')),
                               24., delta=.02)
        self.assertAlmostEqual(probe_dur(str(ROOT / 'assets/audio/ep2/short2.mp3')),
                               18., delta=.02)
        sheet = (ROOT / 'out/upload-2.md').read_text(encoding='utf-8')
        self.assertIn('यह पूरी रकम बचाने का वादा नहीं', sheet)
        ep3_spec = importlib.util.spec_from_file_location('episode3_source', ROOT / 'video/episode03.py')
        ep3 = importlib.util.module_from_spec(ep3_spec)
        ep3_spec.loader.exec_module(ep3)
        rounded = round(probe_dur(str(ROOT / 'out/deep-explains-babylon-niyam-2.mp4')))
        self.assertEqual(ep3.EPISODE['prev_video']['meta'],
                         f'Episode 2 · {rounded // 60}:{rounded % 60:02d}')

    def test_episode2_does_not_present_unsourced_70_percent_or_misattributed_research(self):
        spec = importlib.util.spec_from_file_location('episode2_factcheck', ROOT / 'video/episode02.py')
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        hook, science = (next(s for s in mod.EPISODE['scenes'] if s['id'] == key)
                         for key in ('hook', 'science'))
        self.assertIn('कौन-सा खर्च सच में ज़रूरी था?', hook['narration'])
        self.assertIn('रिटायरमेंट प्लान', science['narration'])
        self.assertIn('यह रोज़ के खर्च पर स्टडी नहीं थी', science['narration'])
        self.assertIn('नक़द की तुलना में', science['narration'])
        self.assertIn('Marketing Letters 2001', str(science['cards']))
        pack = (ROOT / 'content/10-episode2-publish-pack.md').read_text(encoding='utf-8')
        sheet = (ROOT / 'out/upload-2.md').read_text(encoding='utf-8')
        thumbnail_source = (ROOT / 'scripts/make_thumbnail.py').read_text(encoding='utf-8')
        srt = (ROOT / 'out/deep-explains-babylon-niyam-2.hi.srt').read_text(encoding='utf-8')
        for source in (str(hook), str(science), pack, sheet, thumbnail_source, srt):
            self.assertNotIn('70% खर्च', source)
            self.assertNotIn('सत्तर प्रतिशत खर्च', source)
            self.assertNotIn('Sloan 2001', source)
        self.assertIn('Marketing Letters 12(1)', pack)
        self.assertIn('हर खर्च', sheet)
        self.assertAlmostEqual(probe_dur(str(ROOT / 'assets/audio/ep2/narr_01_hook.mp3')),
                               20.08, delta=.02)
        self.assertAlmostEqual(probe_dur(str(ROOT / 'assets/audio/ep2/narr_03_science.mp3')),
                               29.08, delta=.02)

    def test_other_early_examples_are_models_not_promises(self):
        self.assertEqual(40_000 * .10 * 12, 48_000)  # Episode 1
        rate = .12 / 12  # Episode 3: assumed return, not a forecast
        fv = lambda years: 5_000 * ((1 + rate) ** (years * 12) - 1) / rate
        self.assertAlmostEqual(fv(35) / 10_000_000, 3.2, delta=.1)
        self.assertAlmostEqual(fv(25) / 100_000, 94, delta=1)
        self.assertAlmostEqual(fv(20) / 100_000, 49, delta=1)
        self.assertEqual(12 * 4, 48)  # Episode 4: nominal % from monthly pitch
        self.assertAlmostEqual(50_000 * 1.04**12, 80_000, delta=150)
        self.assertIn('यह personalised investment advice नहीं',
                      (ROOT / 'content/12-episode4-publish-pack.md').read_text())

    def test_fallback_links_do_not_imply_series_playlist_or_video_exists(self):
        from make_links import PLAYLIST_FALLBACK, line_for
        row = line_for(2, '')
        self.assertIn('वीडियो लिंक मिलने तक चैनल के प्लेलिस्ट पेज पर', row)
        self.assertIn(PLAYLIST_FALLBACK, row)
        self.assertNotIn('सीरीज़ प्लेलिस्ट में', row)

    def test_render_scratch_is_episode_scoped(self):
        import build_video as B
        B.load_episode(str(ROOT / 'video/episode02.py'))
        work2 = B.WORK
        B.load_episode(str(ROOT / 'video/episode09.py'))
        work9 = B.WORK
        self.assertNotEqual(work2, work9)
        self.assertTrue(work2.endswith('/babylon-niyam-2'))
        self.assertTrue(work9.endswith('/babylon-niyam-9'))
        self.assertEqual(Path(B.MUSIC).parent, Path(work9))


if __name__ == '__main__':
    unittest.main()
