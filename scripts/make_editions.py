#!/usr/bin/env python3
"""Render one or four body styles with the same Signature cover."""
import argparse, json, shutil, subprocess, sys, tempfile
from pathlib import Path
from build_editor import build_editor
from render import media_path
ROOT=Path(__file__).resolve().parents[1]
EDITIONS = {
    'playful': 'A · 아기자기 편집형',
    'overlay': 'B · 사진 오버레이형',
    'video': 'C · 영상 매거진형',
    'interview': 'D · 인터뷰 지면형',
}
def make(source,out,style=None,export_url=None):
    source=Path(source).resolve();out=Path(out).resolve()
    data=json.loads(source.read_text(encoding='utf-8'))
    if data.get('body_only',False) or data['style']!='bold-photo-editorial' or len(data['posts'])!=1 or len(data['posts'][0]['slides'])!=4:
        raise ValueError('Expected one bold-photo-editorial post with four approved photo slides')
    variants = [style] if style else list(EDITIONS)
    if any(variant not in EDITIONS for variant in variants):
        raise ValueError('Unknown body style')
    out.mkdir(parents=True,exist_ok=False)
    with tempfile.TemporaryDirectory() as tmp:
        stage=Path(tmp)
        for i,s in enumerate(data['posts'][0]['slides'],1):
            src=(source.parent/s['image']).resolve()
            if not s.get('image_approved') or not src.is_relative_to(source.parent) or not src.is_file():
                raise ValueError('Image must be an approved local file')
            dest=stage/f'photo-{i}{src.suffix.lower()}';shutil.copyfile(src,dest);s['image']=dest.name
            if i > 1 and s.get('video') and 'video' in variants:
                clip = media_path(source, s['video'], {'.mp4','.mov','.webm','.m4v'})
                dest = stage / f'video-{i}{clip.suffix.lower()}'
                shutil.copyfile(clip, dest)
                s['video'] = dest.name
        if data.get('logo') and 'overlay' in variants:
            logo = media_path(source, data['logo'], {'.png','.jpg','.jpeg','.webp'})
            dest = stage / ('logo' + logo.suffix.lower())
            shutil.copyfile(logo, dest)
            data['logo'] = dest.name
        folders=[]
        data.pop('editorial_variant', None)
        for variant in variants:
            data['body_style']=variant
            feed=stage/'feed.json';feed.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
            folder=out/variant
            subprocess.run([sys.executable,str(ROOT/'scripts/pipeline.py'),str(feed),'--out',str(folder)],check=True)
            folders.append(folder)
        build_editor(folders,out/'editor.html',[EDITIONS[v] for v in variants], variants, export_url)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--style',choices=EDITIONS);p.add_argument('--export-url')
    a=p.parse_args();make(a.input,a.out,a.style,a.export_url)
