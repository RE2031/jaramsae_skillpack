#!/usr/bin/env python3
"""Render the same four-slide post in four TIO-first visual editions."""
import argparse, json, shutil, subprocess, sys, tempfile
from pathlib import Path
from build_editor import build_editor
ROOT=Path(__file__).resolve().parents[1]
EDITIONS=['signature','modern','story','creative']
NAMES=['A · Signature','B · Modern','C · Story','D · Creative']
def make(source,out):
    source=Path(source).resolve();out=Path(out).resolve()
    data=json.loads(source.read_text(encoding='utf-8'))
    if data.get('body_only',False) or data['style']!='bold-photo-editorial' or len(data['posts'])!=1 or len(data['posts'][0]['slides'])!=4:
        raise ValueError('Expected one bold-photo-editorial post with four approved photo slides')
    out.mkdir(parents=True,exist_ok=False)
    with tempfile.TemporaryDirectory() as tmp:
        stage=Path(tmp)
        for i,s in enumerate(data['posts'][0]['slides'],1):
            src=(source.parent/s['image']).resolve()
            if not s.get('image_approved') or not src.is_relative_to(source.parent) or not src.is_file():
                raise ValueError('Image must be an approved local file')
            dest=stage/f'photo-{i}{src.suffix.lower()}';shutil.copyfile(src,dest);s['image']=dest.name
        folders=[]
        for variant in EDITIONS:
            data['editorial_variant']=variant
            feed=stage/'feed.json';feed.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
            folder=out/variant
            subprocess.run([sys.executable,str(ROOT/'scripts/pipeline.py'),str(feed),'--out',str(folder)],check=True)
            folders.append(folder)
        build_editor(folders,out/'editor.html',NAMES)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();make(a.input,a.out)
