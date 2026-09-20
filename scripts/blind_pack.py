#!/usr/bin/env python3
"""Randomize candidate filenames for human review. This is not an effectiveness test."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import random
import shutil
import sys


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--inputs',type=Path,nargs='+',required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--seed',type=int,default=42);a=p.parse_args()
    try:
        if len(a.inputs)<2:raise ValueError('need at least two candidates')
        files=[f.resolve(strict=True) for f in a.inputs]
        if any(not f.is_file() for f in files) or len(files)!=len(set(files)):raise ValueError('inputs must be distinct regular files')
        order=list(files);random.Random(a.seed).shuffle(order)
        a.out.mkdir(parents=True,exist_ok=False);public=a.out/'review';public.mkdir()
        mapping=[]
        for i,src in enumerate(order,1):
            name=f'candidate-{i:02d}{src.suffix.lower()}';shutil.copyfile(src,public/name)
            mapping.append({'candidate':name,'source':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest()})
        (a.out/'private-map.json').write_text(json.dumps({'seed':a.seed,'mapping':mapping},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        with (public/'ratings.csv').open('w',newline='',encoding='utf-8') as f:
            writer=csv.writer(f);writer.writerow(['rater','candidate','instruction_1_5','fidelity_1_5','artifacts_1_5','preference_1_5','reject','notes'])
            for row in mapping:writer.writerow(['',row['candidate'],'','','','','',''])
        (public/'README.txt').write_text('Share only this review directory, never private-map.json. No scores have been filled. Compare at the same display size. Metadata may reveal source; sanitize in a separate reviewed step when strict blinding is required.\n',encoding='utf-8')
        print(public);return 0
    except (OSError,ValueError) as e:print(f'Error: {e}',file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
