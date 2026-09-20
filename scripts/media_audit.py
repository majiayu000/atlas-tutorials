#!/usr/bin/env python3
"""Inspect local media metadata and optionally decode it. Does not judge aesthetics."""
from __future__ import annotations
import argparse
from fractions import Fraction
import json
import math
from pathlib import Path
import subprocess
import sys


def rate(value):
    try:
        result = float(Fraction(str(value)))
        return result if math.isfinite(result) else None
    except (ValueError, ZeroDivisionError, TypeError): return None


def probe(path: Path) -> dict:
    path = path.resolve(strict=True)
    if not path.is_file() or path.stat().st_size == 0: raise ValueError('input must be a nonempty regular file')
    proc = subprocess.run(['ffprobe', '-v', 'error', '-protocol_whitelist', 'file,pipe',
                           '-show_format', '-show_streams', '-of', 'json', str(path)],
                          stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=60)
    if proc.returncode: raise ValueError('ffprobe failed: ' + proc.stderr[:500])
    return json.loads(proc.stdout)


def summarize(info: dict) -> dict:
    streams = info.get('streams', [])
    video = [s for s in streams if s.get('codec_type') == 'video']
    audio = [s for s in streams if s.get('codec_type') == 'audio']
    duration = rate(info.get('format', {}).get('duration'))
    return {'format': info.get('format', {}).get('format_name'), 'duration_seconds': duration,
            'video': [{'codec': s.get('codec_name'), 'width': s.get('width'), 'height': s.get('height'),
                       'avg_fps': rate(s.get('avg_frame_rate')), 'r_fps': rate(s.get('r_frame_rate')),
                       'sample_aspect_ratio': s.get('sample_aspect_ratio'),
                       'pixel_format': s.get('pix_fmt'), 'color_space': s.get('color_space'),
                       'color_transfer': s.get('color_transfer'),
                       'rotation': [d.get('rotation') for d in s.get('side_data_list', []) if 'rotation' in d]}
                      for s in video],
            'audio': [{'codec': s.get('codec_name'), 'sample_rate': s.get('sample_rate'),
                       'channels': s.get('channels')} for s in audio]}


def audit(path: Path, decode=False, width=None, height=None, duration=None, tolerance=.15, require_audio=False, decode_timeout=180):
    metadata = summarize(probe(path))
    checks = {}; issues = []
    for key, expected in [('width', width), ('height', height)]:
        if expected is not None:
            actual = metadata['video'][0].get(key) if metadata['video'] else None
            checks[key] = actual == expected
            if not checks[key]: issues.append(f'{key}: expected {expected}, got {actual}')
    if duration is not None:
        got = metadata['duration_seconds']
        checks['duration'] = got is not None and abs(got-duration) <= tolerance
        if not checks['duration']: issues.append(f'duration: expected {duration} ± {tolerance}, got {got}')
    if require_audio:
        checks['audio_present'] = bool(metadata['audio'])
        if not checks['audio_present']: issues.append('audio stream missing')
    checks['decode'] = None
    if decode:
        try:
            p = subprocess.run(['ffmpeg','-nostdin','-v','error','-xerror','-err_detect','explode',
                                '-protocol_whitelist','file,pipe','-i',str(path.resolve()),
                                '-map','0:v?','-map','0:a?','-f','null','-'],
                               capture_output=True, text=True, timeout=decode_timeout)
            checks['decode'] = p.returncode == 0
            if p.returncode: issues.append('decode failed: '+p.stderr[:500])
        except subprocess.TimeoutExpired:
            issues.append('decode timed out: full-file decoding is unverified')
    return {'file': str(path), 'bytes':path.stat().st_size, 'metadata':metadata, 'checks':checks,
            'issues':issues, 'passed_requested_checks':not issues,
            'content_review':'not_performed', 'note':'Metadata fps does not establish constant frame rate; decode is not visual/audio quality review.'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('input',type=Path);p.add_argument('--output',type=Path)
    p.add_argument('--decode',action='store_true');p.add_argument('--width',type=int);p.add_argument('--height',type=int)
    p.add_argument('--duration',type=float);p.add_argument('--tolerance',type=float,default=.15)
    p.add_argument('--require-audio',action='store_true');p.add_argument('--decode-timeout',type=int,default=180)
    a=p.parse_args()
    try:
        if a.tolerance<0 or not math.isfinite(a.tolerance): raise ValueError('invalid tolerance')
        if a.duration is not None and (a.duration<=0 or not math.isfinite(a.duration)): raise ValueError('invalid duration')
        if a.decode_timeout<=0: raise ValueError('invalid timeout')
        r=audit(a.input,a.decode,a.width,a.height,a.duration,a.tolerance,a.require_audio,a.decode_timeout)
        text=json.dumps(r,ensure_ascii=False,indent=2)+'\n'
        if a.output:
            a.output.parent.mkdir(parents=True,exist_ok=True)
            with a.output.open('x',encoding='utf-8') as f:f.write(text)
        print(text,end='');return 0 if r['passed_requested_checks'] else 1
    except (ValueError,OSError,subprocess.SubprocessError) as e:
        print(f'Error: {e}',file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
