#!/usr/bin/env python3
"""Export the selected cards in order, including composited video."""
import argparse, base64, io, json, re
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
from render import export_video, magazine_issues
from tempfile import TemporaryDirectory

TEXT_FIELDS = ['.cover-brand', '.cover-eyebrow', 'h1 span:first-child',
               'h1 span:nth-child(2)', '.cover-credit', '.category', 'h1',
               'p', 'footer span:last-child', '.photo-aside', '.video-subtitle',
               'header span:first-child', '.overlay-brand span', '.issue', '.interview-question span']

def export(source, out, browser=None, edits=None):
    source=Path(source).resolve(); out=Path(out)
    if out.exists(): raise ValueError('Choose a new output directory')
    with sync_playwright() as pw:
        chromium=pw.chromium.launch(executable_path=browser,args=['--no-sandbox'])
        page=chromium.new_page(viewport={'width':1080,'height':1350},device_scale_factor=1)
        page.goto(source.as_uri(),wait_until='load')
        slides=page.locator('article.slide');errors=[]
        if slides.count()!=4: raise ValueError('Selected HTML must contain exactly four slides')
        if edits is not None:
            if not isinstance(edits, list) or len(edits) != slides.count():
                raise ValueError('편집할 카드가 일치하지 않습니다.')
            for slide, edit in zip(slides.all(), edits):
                if not isinstance(edit, dict) or not isinstance(edit.get('text'), dict):
                    raise ValueError('잘못된 카드 편집 데이터입니다.')
                image = edit.get('image') or {}
                src = image.get('src')
                if src is not None:
                    match = re.fullmatch(r'data:image/(jpeg|png|webp);base64,([A-Za-z0-9+/=]+)',src)
                    if not match:
                        raise ValueError('편집기에서 지원하는 이미지 형식으로 교체해 주세요.')
                    with Image.open(io.BytesIO(base64.b64decode(match[2],validate=True))) as replacement:
                        output = io.BytesIO()
                        replacement.save(output,format='PNG')
                    image['src'] = 'data:image/png;base64,' + base64.b64encode(output.getvalue()).decode()
                text = {key:value for key,value in edit['text'].items()
                        if key in TEXT_FIELDS and isinstance(value,str) and len(value)<=1000}
                slide.evaluate("""(card,{text,image,size})=>{
                    for(const [selector,value] of Object.entries(text)){
                        const node=card.querySelector(selector);
                        if(node && (selector!=='h1' || !node.children.length))node.textContent=value;
                    }
                    if(Number.isFinite(size)&&size>=40&&size<=120)
                        card.querySelector('h1').style.setProperty('font-size',size+'px','important');
                    const photo=card.querySelector('.art img');
                    if(!photo)return;
                    if(image.src)photo.src=image.src;
                    if([image.x,image.y].every(n=>Number.isFinite(n)&&n>=0&&n<=100)){
                        const position=image.x+'% '+image.y+'%';
                        photo.style.setProperty('object-position',position,'important');
                        photo.style.transformOrigin=position;
                    }
                    if(Number.isFinite(image.zoom)&&image.zoom>=1&&image.zoom<=3)
                        photo.style.transform='scale('+image.zoom+')';
                }""",{'text':text,'image':image,'size':edit.get('size')})
        page.evaluate("""async()=>{await document.fonts.ready;await Promise.all([...document.images].map(img=>img.decode().catch(()=>{})));}""")
        for i,slide in enumerate(slides.all(),1):
            issues=slide.evaluate('''el=>{let a=[],r=el.getBoundingClientRect();if(r.width!==1080||r.height!==1350)a.push('size');for(const c of el.querySelectorAll('h1,h1 span,p,header,footer,.cover-brand,.cover-eyebrow,.cover-credit,.category')){if(getComputedStyle(c).display==='none'||!c.getClientRects().length)continue;const b=c.getBoundingClientRect();if(b.bottom>r.bottom+2||b.right>r.right+2||b.left<r.left-2||b.top<r.top-2||c.scrollWidth>c.clientWidth+2&&getComputedStyle(c).display!=='inline')a.push('overflow '+c.tagName)}for(const im of el.querySelectorAll('img'))if(!im.complete||!im.naturalWidth)a.push('image failed');if(el.classList.contains('signature-cover')){const lines=Array.from(el.querySelectorAll('h1>span'));if(lines.length!==2||lines.some(s=>!s.textContent.trim()||s.scrollWidth>s.clientWidth+2))a.push('cover headline')}return a}''')
            issues.extend(magazine_issues(slide))
            if issues:errors.append({'slide':i,'issues':issues})
        if errors:raise ValueError('Resolve layout issues before export: '+json.dumps(errors,ensure_ascii=False))
        out.mkdir(parents=True)
        for i,slide in enumerate(slides.all(),1):
            video=slide.locator('video')
            if not video.count():
                slide.screenshot(path=str(out/f'slide-{i:02d}.png'),animations='disabled')
                continue
            src=video.get_attribute('src')
            with TemporaryDirectory() as temp:
                if src.startswith('data:video/'):
                    clip=Path(temp)/'clip'
                    clip.write_bytes(base64.b64decode(src.split(',',1)[1]))
                else:
                    clip=(source.parent/src).resolve()
                    if not clip.is_relative_to(source.parent):
                        raise ValueError('Invalid local video path')
                export_video(slide,clip,out/f'slide-{i:02d}.mp4')
        chromium.close()
    print('EXPORT_OK',out)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('--out',type=Path,required=True);p.add_argument('--browser');a=p.parse_args();export(a.source,a.out,a.browser)
