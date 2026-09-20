#!/usr/bin/env python3
"""Validate canonical timed segments, write SRT, or merge offset segments. No ASR calls."""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import re
import sys


def validate(segments, duration=None, allow_overlap=False):
    if not isinstance(segments,list) or not segments:raise ValueError('segments must be a nonempty list')
    result=[];last_start=-1.;last_end=0.
    for index,s in enumerate(segments,1):
        if not isinstance(s,dict):raise ValueError(f'segment {index} is not an object')
        start,end=s.get('start'),s.get('end');text=s.get('text')
        if (isinstance(start,bool) or isinstance(end,bool) or not isinstance(start,(int,float)) or not isinstance(end,(int,float))
            or not math.isfinite(start) or not math.isfinite(end) or start<0 or end<=start):raise ValueError(f'invalid time in segment {index}')
        if duration is not None and end>duration+.001:raise ValueError(f'segment {index} exceeds media duration')
        if start<last_start:raise ValueError(f'segment {index} starts before the previous start')
        if not allow_overlap and start<last_end-.001:raise ValueError(f'overlap at segment {index}; review before publishing')
        if not isinstance(text,str) or not text.strip():raise ValueError(f'empty text in segment {index}')
        if '-->' in text or '\x00' in text or any(not ln.strip() for ln in text.strip().splitlines()):raise ValueError('invalid/blank line inside cue text')
        if round(end*1000)<=round(start*1000):raise ValueError('cue becomes zero length at millisecond precision')
        result.append({'start':float(start),'end':float(end),'text':text.strip()});last_start=start;last_end=max(last_end,end)
    return result


def stamp(seconds):
    total=round(seconds*1000);hours,total=divmod(total,3600000);minutes,total=divmod(total,60000);secs,ms=divmod(total,1000)
    return f'{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}'


def as_srt(segments):
    return '\n\n'.join(f'{i}\n{stamp(s["start"])} --> {stamp(s["end"])}\n{s["text"]}' for i,s in enumerate(segments,1))+'\n'


def parse_stamp(text):
    m=re.fullmatch(r'(\d{2,}):(\d{2}):(\d{2})[,.](\d{3})',text)
    if not m:raise ValueError('invalid SRT timestamp')
    h,mn,s,ms=map(int,m.groups())
    if mn>=60 or s>=60:raise ValueError('timestamp minutes/seconds out of range')
    return h*3600+mn*60+s+ms/1000


def parse_srt(text):
    blocks=re.split(r'\n\s*\n',text.lstrip('\ufeff').replace('\r\n','\n').strip());out=[]
    for index,b in enumerate(blocks,1):
        lines=b.splitlines()
        if len(lines)<3 or not lines[0].isdigit():raise ValueError(f'invalid SRT block {index}')
        if int(lines[0])!=index:raise ValueError('SRT cue numbers must be sequential')
        parts=lines[1].split(' --> ')
        if len(parts)!=2:raise ValueError('invalid SRT time line')
        out.append({'start':parse_stamp(parts[0]),'end':parse_stamp(parts[1]),'text':'\n'.join(lines[2:])})
    return out


def merge_chunks(chunks,base):
    if not isinstance(chunks,list) or not chunks:raise ValueError('manifest must be a nonempty list')
    out=[]
    for c in chunks:
        offset=c.get('offset_seconds');name=c.get('segments_file')
        if isinstance(offset,bool) or not isinstance(offset,(int,float)) or not math.isfinite(offset) or offset<0:raise ValueError('invalid offset')
        p=(base/name).resolve();p.relative_to(base.resolve())
        for s in validate(json.loads(p.read_text(encoding='utf-8')),allow_overlap=True):
            out.append({'start':s['start']+offset,'end':s['end']+offset,'text':s['text']})
    return sorted(out,key=lambda s:(s['start'],s['end']))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['from-json','lint','merge'])
    p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path)
    p.add_argument('--duration',type=float);p.add_argument('--offset',type=float,default=0)
    p.add_argument('--allow-overlap',action='store_true');a=p.parse_args()
    try:
        if not math.isfinite(a.offset) or a.offset<0:raise ValueError('invalid offset')
        if a.duration is not None and (not math.isfinite(a.duration) or a.duration<=0):raise ValueError('invalid duration')
        raw=a.input.read_text(encoding='utf-8-sig')
        if a.action=='lint':segments=parse_srt(raw)
        elif a.action=='merge':segments=merge_chunks(json.loads(raw),a.input.parent)
        else:
            segments=validate(json.loads(raw),allow_overlap=True)
            segments=[dict(s,start=s['start']+a.offset,end=s['end']+a.offset) for s in segments]
        segments=validate(segments,a.duration,a.allow_overlap)
        if a.action!='lint':
            if not a.output:raise ValueError('output required')
            a.output.parent.mkdir(parents=True,exist_ok=True)
            with a.output.open('x',encoding='utf-8') as f:f.write(as_srt(segments))
        print(json.dumps({'cues':len(segments),'timeline_valid':True,'content_review':'not_performed','overlap_allowed':a.allow_overlap}));return 0
    except (ValueError,OSError,KeyError,TypeError) as e:print(f'Error: {e}',file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
