# Release readiness — The Richest Man in Babylon (Episodes 1–9)

**Local technical status:** 9 upload packages validated; owner editorial/rights review remains. **YouTube status:** Unverified; this local audit has no channel access. These are local artifacts, not publication evidence.

| Episode | Full video (s) | MP4 (MB) | Short (s) | Hindi SRT | Primary thumbnail | Studio start* |
|---|---:|---:|---:|---:|---|---:|
| 1 | 236.28 | 67.1 | 21.07 | 52 cues | `out/thumbnail-A-1280x720.jpg` | **03:45** |
| 2 | 218.44 | 30.0 | 19.20 | 45 cues | `out/thumbnail-niyam2-A-1280x720.jpg` | **03:27** |
| 3 | 220.88 | 29.5 | 17.70 | 45 cues | `out/thumbnail-niyam3-A-1280x720.jpg` | **03:29** |
| 4 | 218.84 | 64.0 | 17.93 | 34 cues | `out/thumbnail-niyam4-A-1280x720.jpg` | **03:27** |
| 5 | 239.96 | 68.2 | 25.60 | 40 cues | `out/thumbnail-niyam5-A-1280x720.jpg` | **03:48** |
| 6 | 226.40 | 26.3 | 29.27 | 65 cues | `out/thumbnail-niyam6-A-1280x720.jpg` | **03:35** |
| 7 | 235.88 | 25.3 | 26.50 | 74 cues | `out/thumbnail-niyam7-A-1280x720.jpg` | **03:44** |
| 8 | 223.40 | 23.5 | 26.30 | 69 cues | `out/thumbnail-niyam8-A-1280x720.jpg` | **03:32** |
| 9 | 238.96 | 34.5 | 28.73 | 73 cues | `out/thumbnail-niyam9-A-1280x720.jpg` | **03:47** |

*Start at the first whole second **after the voice-derived canvas cut**; final MP4 duration may differ by a few frames. Baked artwork is not interactive.*

**Editorial QA corrections — Episode 2:** The illustrative ₹500 + ₹4,000 + ₹2,000 = ₹6,500/month = ₹78,000/year of **spending**, not promised savings. The spoken example, Short, captions, thumbnail B and upload copy use the corrected sum. The re-recorded hook no longer asserts an unsourced “70% unnecessary” figure; thumbnail A/title ask a question instead. The re-recorded evidence scene attributes Madrian & Shea (2001) to retirement-plan enrolment, not daily spending, and cites Prelec & Simester (2001) in *Marketing Letters* for the limited card/cash finding. These checks cannot certify every editorial claim or confirm channel clearance.

## Still requires channel owner / YouTube Studio

- [ ] Confirm intended commercial use/licences for narration, generated art, fonts and audio; review videos and upload metadata personally.
- [ ] Create the **The Richest Man in Babylon — Hindi** playlist and upload each full video in order (or schedule after review); set title/description/tags, language and appropriate audience settings from `out/upload-N.md`.
- [ ] Upload each video’s `.hi.srt` in Hindi, choose one of its three JPG thumbnails and inspect the processed public/private preview.
- [ ] Add actual Studio **video + subscribe end-screen elements** on the 12-second baked canvas, not just the artwork. Follow `content/07-end-screen.md`; link episodes only once published.
- [ ] Upload each `out/short-N.mp4` separately. Its title, safety notes, description and long-video link guidance are in the same upload sheet.
- [ ] After each upload, put the real video/playlist IDs in local ignored `links.json` (template: `links.example.json`), then run `python3 scripts/publish.py --all` to replace fallback links before pasting metadata.
- [ ] Confirm visibility, pinned comments, playlist order, working links and clickable end screens in **Studio**; no script can attest to those without channel access.

Known video IDs in local config: **0/9** (presence alone does not prove publication).

Recheck locally: `python3 scripts/check_release.py` and `python3 -m unittest discover -s tests -q`.
