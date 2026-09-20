#!/usr/bin/env python3
"""Split a trusted local recording into PCM chunks and record offsets. No transcription."""
import argparse
import json
import math
from pathlib import Path
import subprocess
import sys
from media_audit import probe, summarize


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--seconds',type=float,default=120);p.add_argument('--overlap',type=float,default=2);a=p.parse_args()
    try:
        if not math.isfinite(a.seconds) or not math.isfinite(a.overlap) or not 0<=a.overlap<a.seconds or a.seconds<=0:raise ValueError('need 0 <= overlap < seconds')
        duration=summarize(probe(a.input))['duration_seconds']
        if not duration or duration<=0:raise ValueError('duration unknown')
        if math.ceil(duration/(a.seconds-a.overlap))>10000:raise ValueError('too many chunks')
        a.out.mkdir(parents=True,exist_ok=False);records=[];start=0.;index=0
        while start<duration-0.001:
            end=min(start+a.seconds,duration);name=f'chunk-{index:04d}.wav'
            subprocess.run(['ffmpeg','-nostdin','-v','error','-n','-protocol_whitelist','file,pipe',
                            '-i',str(a.input.resolve()),'-ss',str(start),'-t',str(end-start),'-map','0:a:0',
                            '-vn','-ac','1','-ar','16000','-c:a','pcm_s16le',str(a.out/name)],check=True,timeout=300)
            records.append({'audio_file':name,'offset_seconds':start,'end_seconds':end,'segments_file':f'chunk-{index:04d}.segments.json','transcribed':False})
            (a.out/'chunks.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            if end>=duration:break
            start+=a.seconds-a.overlap;index+=1
        print(f'{len(records)} chunks written; no ASR requests made.');return 0
    except (OSError,ValueError,subprocess.SubprocessError) as e:print(f'Error: {e}; preserve partial output.',file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
