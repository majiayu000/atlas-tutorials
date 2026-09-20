#!/usr/bin/env python3
"""Offline structural checks. Does not execute tutorial commands or validate live APIs."""
from pathlib import Path
import argparse
import ast
import json
import re
import shutil
import subprocess
import tempfile
import urllib.parse
ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path);args=p.parse_args()
    problems=[];counts={'tutorials':0,'markdown_files':0,'local_links':0,'bash_blocks':0,'python_files':0,'json_files':0,'node_files':0,'yaml_files':0}
    cat=json.loads((ROOT/'catalog.json').read_text())
    if len(cat)!=48 or {i['id'] for i in cat}!=set(range(1,49)):problems.append('catalog must contain IDs 1..48 exactly')
    for item in cat:
        f=ROOT/item['path']
        if not f.is_file():problems.append('missing tutorial: '+item['path']);continue
        text=f.read_text();counts['tutorials']+=1
        if len(text)<1000:problems.append('tutorial too short for a full article: '+item['path'])
        if '##' not in text or '验收' not in text and '检查' not in text:problems.append('missing practical checks: '+item['path'])
    for f in sorted(ROOT.rglob('*')):
        if not f.is_file() or '__pycache__' in f.parts:continue
        rel=f.relative_to(ROOT).as_posix()
        try:
            if f.suffix=='.py':ast.parse(f.read_text(),filename=rel);counts['python_files']+=1
            if f.suffix=='.json':json.loads(f.read_text());counts['json_files']+=1
            if f.suffix=='.mjs':
                proc=subprocess.run(['node','--check',str(f)],capture_output=True,text=True)
                counts['node_files']+=1
                if proc.returncode:problems.append(rel+': '+proc.stderr[:300])
            if f.suffix in {'.yaml','.yml'}:
                try:
                    import yaml
                    yaml.load(f.read_text(),Loader=yaml.BaseLoader);counts['yaml_files']+=1
                except ImportError:problems.append('PyYAML absent; YAML parse not performed')
            if f.suffix!='.md':continue
            text=f.read_text();counts['markdown_files']+=1
            for index,match in enumerate(re.finditer(r'^```(?:bash|sh)\s*\n(.*?)^```\s*$',text,re.S|re.M),1):
                counts['bash_blocks']+=1
                proc=subprocess.run(['bash','-n'],input=match.group(1),capture_output=True,text=True)
                if proc.returncode:problems.append(f'{rel} shell block {index}: {proc.stderr}')
            stripped=re.sub(r'^```[^\n]*\n.*?^```\s*$','',text,flags=re.S|re.M)
            for match in re.finditer(r'!?\[[^\]]*\]\(([^)]+)\)',stripped):
                target=match.group(1).split(' "',1)[0].strip('<>')
                if target.startswith(('https://','http://','mailto:','#','data:')):continue
                path=urllib.parse.unquote(target.split('#',1)[0].split('?',1)[0])
                if not path:continue
                counts['local_links']+=1
                if not (f.parent/path).exists():problems.append(f'{rel}: missing link {target}')
        except (ValueError,SyntaxError,OSError) as e:problems.append(rel+': '+str(e))
    result={'passed':not problems,'counts':counts,'problems':problems,'scope':'syntax, document paths and presence only; shell blocks NOT executed; no live generation'}
    text=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if args.output:args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(text)
    print(text);return 1 if problems else 0
if __name__=='__main__':raise SystemExit(main())
