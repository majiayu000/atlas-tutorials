#!/usr/bin/env python3
"""Deterministic local media transforms. Requires FFmpeg. Refuses overwrite."""
from __future__ import annotations
import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from media_audit import probe, summarize


def ff(args, timeout=300):
    subprocess.run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-n','-threads','1',
                    '-filter_threads','1','-filter_complex_threads','1',*map(str,args)],check=True,timeout=timeout)


def local_input(path):
    return ['-protocol_whitelist','file,pipe','-i',str(Path(path).resolve(strict=True))]


def fit_filter(w,h,mode):
    if not 2<=w<=8192 or not 2<=h<=8192:raise ValueError('dimensions must be 2..8192')
    if mode=='cover':return f'scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1'
    return f'scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=white,setsar=1'


def normalize(src,dst,w,h,fps):
    if w%2 or h%2:raise ValueError('video dimensions must be even')
    ff([*local_input(src),'-map','0:v:0','-vf',fit_filter(w,h,'contain')+f',fps={fps},format=yuv420p',
        '-an','-c:v','libx264','-threads','1','-crf','18','-preset','fast','-map_metadata','-1',
        '-movflags','+faststart',dst])


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=['fit-image','overlay-image','normalize-video','concat','burn-subtitles','mix-audio','side-by-side'])
    p.add_argument('--inputs',type=Path,nargs='+',required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--width',type=int,default=1080);p.add_argument('--height',type=int,default=1920)
    p.add_argument('--mode',choices=['contain','cover'],default='contain');p.add_argument('--fps',type=int,default=30)
    p.add_argument('--box',default='0,0,640,360',help='x,y,width,height for overlay-image')
    p.add_argument('--subtitles',type=Path);p.add_argument('--font-size',type=int,default=24)
    p.add_argument('--music-volume',type=float,default=.12)
    a=p.parse_args()
    try:
        if not 1<=a.fps<=120:raise ValueError('fps must be 1..120')
        if not 8<=a.font_size<=96:raise ValueError('font-size must be 8..96')
        if not 0<=a.music_volume<=1:raise ValueError('music-volume must be 0..1')
        a.output=a.output.resolve()
        if a.output.exists():raise ValueError('output already exists; choose a new filename')
        for f in a.inputs:
            if not f.is_file() or not f.stat().st_size:raise ValueError(f'missing/empty input: {f}')
        a.output.parent.mkdir(parents=True,exist_ok=True)
        n=len(a.inputs)
        if a.action=='fit-image':
            if n!=1:raise ValueError('fit-image needs one image')
            ff([*local_input(a.inputs[0]),'-vf',fit_filter(a.width,a.height,a.mode),'-frames:v','1',
                '-update','1','-map_metadata','-1',a.output])
        elif a.action=='overlay-image':
            if n!=2:raise ValueError('overlay-image needs background and screenshot')
            x,y,w,h=map(int,a.box.split(','))
            if x<0 or y<0:raise ValueError('negative coordinates are not accepted')
            base=summarize(probe(a.inputs[0]))['video'][0]
            if x+w>base['width'] or y+h>base['height']:raise ValueError('overlay box exceeds background')
            graph=f'[1:v]{fit_filter(w,h,"contain")}[screen];[0:v][screen]overlay={x}:{y}:shortest=1[out]'
            ff([*local_input(a.inputs[0]),*local_input(a.inputs[1]),'-filter_complex',graph,
                '-map','[out]','-frames:v','1','-update','1','-map_metadata','-1',a.output])
        elif a.action=='normalize-video':
            if n!=1:raise ValueError('normalize-video needs one video')
            normalize(a.inputs[0],a.output,a.width,a.height,a.fps)
        elif a.action=='concat':
            if n<2:raise ValueError('concat needs at least two clips')
            with tempfile.TemporaryDirectory(prefix='atlas-concat-') as td:
                root=Path(td)
                for i,src in enumerate(a.inputs):normalize(src,root/f'{i:03d}.mp4',a.width,a.height,a.fps)
                listing=root/'clips.txt'
                listing.write_text(''.join(f"file '{i:03d}.mp4'\n" for i in range(n)),encoding='utf-8')
                ff(['-f','concat','-safe','1','-i',listing,'-c','copy','-an','-movflags','+faststart',a.output])
        elif a.action=='burn-subtitles':
            if n!=1 or not a.subtitles or not a.subtitles.is_file():raise ValueError('needs one video and an SRT file')
            with tempfile.TemporaryDirectory(prefix='atlas-subtitles-') as td:
                simple=Path(td)/'captions.srt';shutil.copyfile(a.subtitles,simple)
                # Temporary paths contain only portable safe ASCII characters on the supported POSIX path.
                # Drive letters need escaping on Windows.
                escaped=str(simple).replace('\\','/').replace(':','\\:').replace("'","\\'")
                vf=f"subtitles=filename='{escaped}':force_style='Fontsize={a.font_size},MarginV=24'"
                ff([*local_input(a.inputs[0]),'-vf',vf,'-map','0:v:0','-map','0:a?',
                    '-c:v','libx264','-threads','1','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-movflags','+faststart',a.output])
        elif a.action=='mix-audio':
            if n not in {2,3}:raise ValueError('needs video, voice, and optionally music')
            duration=summarize(probe(a.inputs[0]))['duration_seconds']
            if not duration or duration<=0:raise ValueError('cannot determine video duration')
            argv=[]
            for src in a.inputs:argv+=local_input(src)
            graph=f'[1:a]aresample=48000,apad,atrim=0:{duration}[voice];'
            if n==3:
                graph+=f'[2:a]aresample=48000,volume={a.music_volume},apad,atrim=0:{duration}[music];[voice][music]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95:level=0[outa]'
            else:graph+='[voice]alimiter=limit=0.95:level=0[outa]'
            ff([*argv,'-filter_complex',graph,'-map','0:v:0','-map','[outa]','-c:v','copy','-c:a','aac','-ar','48000',
                '-t',duration,'-movflags','+faststart',a.output])
        elif a.action=='side-by-side':
            if n!=2:raise ValueError('needs two temporally aligned videos')
            graph=f'[0:v]{fit_filter(a.width,a.height,"contain")},fps={a.fps},setpts=PTS-STARTPTS[left];[1:v]{fit_filter(a.width,a.height,"contain")},fps={a.fps},setpts=PTS-STARTPTS[right];[left][right]hstack=inputs=2:shortest=1[out]'
            ff([*local_input(a.inputs[0]),*local_input(a.inputs[1]),'-filter_complex',graph,'-map','[out]',
                '-an','-c:v','libx264','-threads','1','-crf','18','-pix_fmt','yuv420p',a.output])
        print(a.output);return 0
    except (OSError,ValueError,subprocess.SubprocessError,KeyError,IndexError) as e:
        print(f'Error: {e}. A partial output may exist; inspect it before retrying with a new path.',file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
