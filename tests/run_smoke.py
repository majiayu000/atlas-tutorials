#!/usr/bin/env python3
"""Local-only media smoke tests. Never calls Atlas. Requires ffmpeg/ffprobe.
Usage: python3 tests/run_smoke.py --out /a/new/directory
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    out=a.out.resolve();out.mkdir(parents=True,exist_ok=False)
    results=[]
    def run(name,args,expected=0,timeout=90):
        start=time.monotonic()
        try:
            r=subprocess.run(list(map(str,args)),cwd=ROOT,capture_output=True,text=True,timeout=timeout)
            result={'name':name,'exit_code':r.returncode,'expected_exit_code':expected,'passed':r.returncode==expected,'seconds':round(time.monotonic()-start,3)}
            (out/(name+'.stdout.txt')).write_text(r.stdout,encoding='utf-8');(out/(name+'.stderr.txt')).write_text(r.stderr,encoding='utf-8')
        except subprocess.SubprocessError as e:result={'name':name,'passed':False,'error':str(e)}
        results.append(result);(out/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(name, 'PASS' if result['passed'] else 'FAIL', flush=True)
        return result['passed']
    py=sys.executable;s=ROOT/'scripts';f=out/'fixtures';d=out/'outputs';d.mkdir()
    if not run('fixtures',[py,s/'make_fixtures.py','--out',f]):return 1
    run('audit-original',[py,s/'media_audit.py',f/'clip-a.mp4','--width','320','--height','180','--duration','4','--require-audio','--decode','--output',d/'audit.json'])
    run('audit-wrong-spec-rejected',[py,s/'media_audit.py',f/'clip-a.mp4','--width','999'],expected=1)
    run('fit-contain',[py,s/'media_ops.py','fit-image','--inputs',f/'image.png','--output',d/'contain.png','--width','320','--height','320'])
    run('fit-cover',[py,s/'media_ops.py','fit-image','--inputs',f/'image.png','--output',d/'cover.png','--width','180','--height','320','--mode','cover'])
    run('overlay',[py,s/'media_ops.py','overlay-image','--inputs',f/'image.png',d/'contain.png','--box','60,30,160,160','--output',d/'overlay.png'])
    run('normalize',[py,s/'media_ops.py','normalize-video','--inputs',f/'clip-b.mp4','--output',d/'normalized.mp4','--width','320','--height','180','--fps','24'])
    run('concat',[py,s/'media_ops.py','concat','--inputs',f/'clip-a.mp4',f/'clip-b.mp4','--output',d/'concat.mp4','--width','320','--height','180','--fps','24'])
    run('concat-audit',[py,s/'media_audit.py',d/'concat.mp4','--duration','6','--width','320','--height','180','--decode'])
    run('subtitle-conversion',[py,s/'subtitles.py','from-json','--input',ROOT/'examples/subtitles/segments.json','--output',d/'captions.srt','--duration','4'])
    run('subtitle-lint',[py,s/'subtitles.py','lint','--input',d/'captions.srt','--duration','4'])
    run('subtitle-burn',[py,s/'media_ops.py','burn-subtitles','--inputs',f/'clip-a.mp4','--subtitles',d/'captions.srt','--output',d/'subtitled.mp4','--font-size','14'])
    run('voice-mix',[py,s/'media_ops.py','mix-audio','--inputs',f/'clip-a.mp4',f/'tone.wav','--output',d/'voice.mp4'])
    run('music-mix',[py,s/'media_ops.py','mix-audio','--inputs',f/'clip-a.mp4',f/'tone.wav',f/'tone.wav','--output',d/'mixed.mp4','--music-volume','0.1'])
    run('mixed-audit',[py,s/'media_audit.py',d/'mixed.mp4','--duration','4','--require-audio','--decode'])
    run('side-by-side',[py,s/'media_ops.py','side-by-side','--inputs',f/'clip-a.mp4',d/'mixed.mp4','--output',d/'comparison.mp4','--width','320','--height','180','--fps','24'])
    run('comparison-audit',[py,s/'media_audit.py',d/'comparison.mp4','--width','640','--height','180','--duration','4','--decode'])
    run('audio-chunks',[py,s/'audio_chunks.py','--input',f/'tone.wav','--out',out/'chunks','--seconds','2','--overlap','0.5'])
    run('blind-pack',[py,s/'blind_pack.py','--inputs',d/'contain.png',d/'cover.png','--out',out/'blind'])
    run('file-manifest',[py,s/'manifest.py','--root',d,'--output',out/'delivery-manifest.json'])
    run('overwrite-rejected',[py,s/'media_ops.py','fit-image','--inputs',f/'image.png','--output',d/'contain.png'],expected=2)
    run('missing-media-rejected',[py,s/'media_audit.py',out/'absent.mp4'],expected=2)
    run('batch-plan-local',[py,s/'batch_plan.py','--csv',ROOT/'examples/sku.csv','--model','test-provider/offline-fixture','--out',out/'sku','--max-jobs','3'])
    (out/'README.md').write_text('# 离线测试素材与输出\n\n所有图案、音调和片段由 FFmpeg 本地合成，不是 Atlas 模型输出、真实产品样片或内容质量基准。该目录记录工具运行结果；通过解码不等于通过中文字体/视觉/声音审核。没有调用 Atlas 或使用 API key。\n',encoding='utf-8')
    failures=[r['name'] for r in results if not r['passed']]
    print(f'{len(results)-len(failures)}/{len(results)} passed')
    return 1 if failures else 0
if __name__=='__main__':raise SystemExit(main())
