#!/usr/bin/env python3
"""Turn Hindi voice recordings into scene-level narration masters.

The TTS service allows up to 1,500 characters per recording. For Episodes
6–8 and Ep9's first half we recorded four scenes per half with spoken
'अगला दृश्य।' separators. Each pair
below is the measured silence BEFORE and AFTER that separator (ffmpeg
silencedetect=-38dB:d=.18). Remove the separator, leave a tiny breath, and
slow the source by 10% for a natural ~4-minute edit. Never retime a completed
video without rebuilding its captions/Short as well.

Inputs: ignored out/_work/epN-half{1,2}.mp3 (temporary recordings).
Ep9's last four scenes instead use individual ep9-scene05.mp3 ... scene08.mp3
because its second long recording exceeded the voice service's per-turn limit.
Outputs: tracked assets/audio/epN/narr_01_hook.mp3 ... narr_08_outro.mp3
Usage: python3 scripts/split_remaining_audio.py 6
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'video'))
from remaining_content import IDS  # noqa: E402

try:
    import imageio_ffmpeg
    FF = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    FF = 'ffmpeg'

# start of pre-marker silence, end of post-marker silence; seconds in raw clip.
# Inspect with: ffmpeg -i file.mp3 -af silencedetect=noise=-38dB:d=0.18 -f null -
# DO NOT cut at the immediately preceding pause if the TTS inserts a tiny
# hesitation inside 'अगला दृश्य।' (observed in 7/1 and 8/1).
MARKERS = {
    (6, 1): ((23.09, 24.50), (47.26, 48.68), (71.67, 73.07)),
    (6, 2): ((25.47, 26.95), (50.28, 51.79), (73.90, 75.26)),
    (7, 1): ((22.66, 24.33), (48.76, 50.35), (73.91, 75.45)),
    (7, 2): ((26.02, 27.84), (53.72, 55.58), (78.08, 79.80)),
    (8, 1): ((22.47, 24.09), (47.34, 48.93), (72.11, 73.66)),
    (8, 2): ((25.63, 27.19), (48.45, 49.69), (71.92, 73.59)),
    (9, 1): ((23.58, 25.12), (49.89, 51.35), (73.94, 75.38)),
}
SPEED = 0.90
BREATH = 0.12


def duration(path: Path) -> float:
    stderr = subprocess.run([FF, '-hide_banner', '-i', str(path)],
                            text=True, capture_output=True).stderr
    m = re.search(r'Duration: (\d+):(\d+):([\d.]+)', stderr)
    if not m:
        raise RuntimeError(f'Cannot probe {path}: {stderr[-500:]}')
    return int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])


def split(ep: int, halves: tuple[int, ...] = (1, 2)) -> None:
    dest = ROOT / 'assets' / 'audio' / f'ep{ep}'
    dest.mkdir(parents=True, exist_ok=True)
    for half in halves:
        if ep == 9 and half == 2:
            # Four independently recorded scenes avoid a 1,500-character TTS
            # rejection and need no spoken markers removed.
            for scene_num in range(5, 9):
                sid = IDS[scene_num - 1]
                src = ROOT / 'out' / '_work' / f'ep9-scene{scene_num:02d}.mp3'
                if not src.exists():
                    raise FileNotFoundError(f'Missing separately recorded narration: {src}')
                out = dest / f'narr_{scene_num:02d}_{sid}.mp3'
                slow_dur = duration(src) / SPEED
                filt = (f'atempo={SPEED},afade=t=in:st=0:d=0.04,'
                        f'afade=t=out:st={max(0., slow_dur-0.05):.3f}:d=0.05')
                subprocess.run([FF, '-hide_banner', '-loglevel', 'error', '-y',
                                '-i', str(src), '-vn', '-af', filt,
                                '-ac', '2', '-ar', '48000', '-c:a', 'libmp3lame',
                                '-b:a', '160k', str(out)], check=True)
                actual = duration(out)
                if not 10 < actual < 43:
                    raise ValueError(f'Unexpected scene duration: {out} = {actual:.2f}s')
                print(f'ep9 {sid:8s} {actual:5.2f}s  {out.relative_to(ROOT)}', flush=True)
            continue
        original = ROOT / 'out' / '_work' / f'ep{ep}-half{half}.mp3'
        if not original.exists():
            raise FileNotFoundError(f'Missing source recording: {original}')
        markers = MARKERS[(ep, half)]
        if len(markers) != 3:
            raise ValueError(f'Measured separator cuts missing: ep{ep} half{half}')
        total = duration(original)
        for i, (left, right) in enumerate(markers):
            assert 0 < left < right < total and right - left > 0.75, (ep, half, i)
            if i:
                assert markers[i-1][1] + 6 < left, (ep, half, i)
        spans = [(0.0, markers[0][0] + BREATH)]
        spans += [(markers[i][1] - BREATH, markers[i+1][0] + BREATH)
                  for i in range(2)]
        spans += [(markers[-1][1] - BREATH, total)]
        for j, (start, end) in enumerate(spans):
            sid = IDS[(half - 1) * 4 + j]
            out = dest / f'narr_{(half-1)*4+j+1:02d}_{sid}.mp3'
            # trim the complete sentence, remove the spoken edit marker and
            # preserve a short breath on each side. atempo preserves pitch.
            slow_dur = (end - start) / SPEED
            filt = (f'atrim=start={start:.3f}:end={end:.3f},asetpts=PTS-STARTPTS,'
                    f'atempo={SPEED},afade=t=in:st=0:d=0.04,'
                    f'afade=t=out:st={max(0., slow_dur-0.05):.3f}:d=0.05')
            subprocess.run([FF, '-hide_banner', '-loglevel', 'error', '-y',
                            '-i', str(original), '-vn', '-af', filt,
                            '-ac', '2', '-ar', '48000', '-c:a', 'libmp3lame',
                            '-b:a', '160k', str(out)], check=True)
            actual = duration(out)
            if not 10 < actual < 43:
                raise ValueError(f'Unexpected scene duration: {out} = {actual:.2f}s')
            print(f'ep{ep} {sid:8s} {actual:5.2f}s  {out.relative_to(ROOT)}', flush=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('episode', type=int, choices=range(6, 10))
    ap.add_argument('--half', type=int, choices=(1, 2),
                    help='process just one finished half if the second is pending')
    opts = ap.parse_args()
    split(opts.episode, (opts.half,) if opts.half else (1, 2))
