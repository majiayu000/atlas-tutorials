#!/usr/bin/env python3
"""Create offline test media from FFmpeg test sources, not model-generated examples."""
import argparse
from pathlib import Path
import subprocess


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=False)
    def run(args):subprocess.run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-n','-threads','1','-filter_threads','1',*map(str,args)],check=True,timeout=45)
    run(['-f','lavfi','-i','testsrc2=size=320x180:rate=24','-f','lavfi','-i','sine=frequency=440:sample_rate=48000','-t','4','-c:v','libx264','-threads','1','-pix_fmt','yuv420p','-c:a','aac',a.out/'clip-a.mp4'])
    run(['-f','lavfi','-i','testsrc2=size=180x320:rate=30','-t','2','-c:v','libx264','-threads','1','-pix_fmt','yuv420p',a.out/'clip-b.mp4'])
    run(['-f','lavfi','-i','sine=frequency=660:sample_rate=48000','-t','4','-c:a','pcm_s16le',a.out/'tone.wav'])
    run(['-f','lavfi','-i','testsrc=size=640x360','-frames:v','1','-update','1',a.out/'image.png'])
    (a.out/'README.txt').write_text('Synthetic FFmpeg test patterns and sine tone. Not Atlas results; no speech or model-quality claims.\n',encoding='utf-8')
    print(a.out)
if __name__=='__main__':main()
