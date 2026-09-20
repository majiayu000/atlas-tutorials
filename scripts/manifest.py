#!/usr/bin/env python3
"""Hash a dedicated delivery directory. Excludes no secrets automatically: review first."""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def sha256(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    try:
        root=a.root.resolve(strict=True);output=a.output.resolve()
        if not root.is_dir():raise ValueError('root must be a directory')
        records=[]
        for f in sorted(root.rglob('*')):
            if f.resolve()==output:continue
            if f.is_symlink():raise ValueError('refuse symlinks in delivery directory')
            if f.is_file():records.append({'path':f.relative_to(root).as_posix(),'bytes':f.stat().st_size,'sha256':sha256(f)})
        if not records:raise ValueError('empty delivery directory')
        output.parent.mkdir(parents=True,exist_ok=True)
        with output.open('x',encoding='utf-8') as f:json.dump({'files':records,'content_review':'not_performed'},f,ensure_ascii=False,indent=2)
        print(f'{len(records)} files recorded');return 0
    except (OSError,ValueError) as e:print(f'Error: {e}',file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
