#!/usr/bin/env python3
"""Build a portable, offline editor from four rendered 4-slide posts."""
import argparse, base64, json, mimetypes, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def build_editor(dirs,out,names=None):
    versions=[]
    for i,folder in enumerate(dirs):
        p=Path(folder)/'editable'
        html=(p/'index.html').read_text(encoding='utf-8')
        css=(p/'style.css').read_text(encoding='utf-8')
        def embed(m):
            f=(p/m.group(1)).resolve()
            if not f.is_relative_to(p.resolve()) or not f.is_file(): raise ValueError('Invalid asset '+str(f))
            mime=mimetypes.guess_type(f.name)[0]
            if mime not in {'image/jpeg','image/png','image/webp'}: raise ValueError('Invalid image type')
            return 'src="data:'+mime+';base64,'+base64.b64encode(f.read_bytes()).decode()+'"'
        html=re.sub(r'src="(assets/[^"<>]+)"',embed,html)
        slides=re.findall(r'<article\b[^>]*>.*?</article>',html,re.S)
        if len(slides)!=4: raise ValueError(f'Version {i+1} must contain exactly four slides, got {len(slides)}')
        versions.append(dict(name=names[i] if names else f'시안 {i+1}',description='',css=css,slides=slides))
    if len(versions)!=4: raise ValueError('Exactly four versions required')
    data=json.dumps({'selected':0,'versions':versions},ensure_ascii=False).replace('<','\\u003c')
    template=(ROOT/'templates/editor.html').read_text(encoding='utf-8')
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(template.replace('__PROJECT__',data),encoding='utf-8')
    print('EDITOR_READY:',out)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('versions',nargs=4,type=Path);p.add_argument('--out',type=Path,required=True);p.add_argument('--names',nargs=4);a=p.parse_args();build_editor(a.versions,a.out,a.names)
