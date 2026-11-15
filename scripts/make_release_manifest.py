#!/usr/bin/env python3
"""Freeze and verify the 54 local upload media files (no YouTube I/O).

After re-rendering or replacing media, run the local audit first, then:
  python3 scripts/make_release_manifest.py --write
  python3 scripts/make_release_manifest.py --check

The tracked checksum file records MP4s, Hindi SRTs and all three JPG thumbnail
options for each episode. Upload sheets are intentionally excluded: their real
URLs should change after channel publication. This is an integrity check, NOT
proof of licences, editorial correctness, publication or Studio configuration.
"""
from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'out/upload-media.sha256'
HEADER = ('# The Richest Man in Babylon — 9 local upload sets / 54 media files\n'
          '# SHA-256 integrity only; not YouTube publication, editorial or rights clearance.\n')


def paths() -> list[str]:
    files = []
    for ep in range(1, 10):
        slug = f'babylon-niyam-{ep}'
        files.extend((f'out/deep-explains-{slug}.mp4',
                      f'out/deep-explains-{slug}.hi.srt',
                      f'out/short-{ep}.mp4'))
        prefix = 'thumbnail-' if ep == 1 else f'thumbnail-niyam{ep}-'
        files.extend(f'out/{prefix}{variant}-1280x720.jpg' for variant in 'ABC')
    return files


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def write() -> None:
    lines = [HEADER]
    for name in paths():
        p = ROOT / name
        if not p.is_file() or p.stat().st_size == 0:
            raise FileNotFoundError(f'missing/empty release asset: {name}')
        lines.append(f'{digest(p)}  {name}\n')
    MANIFEST.write_text(''.join(lines), encoding='utf-8')
    print(f'wrote {MANIFEST.relative_to(ROOT)} ({len(paths())} files)')


def check() -> list[str]:
    if not MANIFEST.is_file():
        return [f'missing {MANIFEST.relative_to(ROOT)}; run --write after media QA']
    expected = set(paths())
    recorded: dict[str, str] = {}
    issues = []
    for line in MANIFEST.read_text(encoding='utf-8').splitlines():
        if line.startswith('#') or not line:
            continue
        match = re.fullmatch(r'([a-f0-9]{64})  (out/[^\s]+)', line)
        if not match:
            issues.append('malformed checksum line in upload-media.sha256')
            continue
        value, name = match.groups()
        if name not in expected:
            issues.append(f'unexpected path in upload-media.sha256: {name}')
        elif name in recorded:
            issues.append(f'duplicate checksum: {name}')
        else:
            recorded[name] = value
    for name in paths():
        if name not in recorded:
            issues.append(f'missing checksum: {name}')
            continue
        p = ROOT / name
        if not p.is_file() or p.stat().st_size == 0:
            issues.append(f'missing/empty release asset: {name}')
        elif digest(p) != recorded[name]:
            issues.append(f'checksum mismatch: {name}; rerender/review, then --write')
    return issues


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--write', action='store_true', help='snapshot current local assets')
    mode.add_argument('--check', action='store_true', help='verify expected paths and SHA-256 digests')
    args = parser.parse_args()
    if args.write:
        write()
        return
    errors = check()
    if errors:
        for error in errors:
            print('FAIL:', error)
        raise SystemExit(1)
    print(f'PASS: {len(paths())} local upload media files match the SHA-256 manifest. No channel checks.')


if __name__ == '__main__':
    main()
