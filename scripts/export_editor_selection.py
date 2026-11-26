#!/usr/bin/env python3
"""Render a selected four-slide HTML export into new 1080x1350 PNGs."""
import argparse, json
from pathlib import Path
from playwright.sync_api import sync_playwright

def export(source, out, browser=None):
    source=Path(source); out=Path(out)
    if out.exists(): raise ValueError('Choose a new output directory')
    with sync_playwright() as pw:
        chromium=pw.chromium.launch(executable_path=browser,args=['--no-sandbox'])
        page=chromium.new_page(viewport={'width':1080,'height':1350},device_scale_factor=1)
        page.set_content(source.read_text(encoding='utf-8'));page.evaluate('document.fonts.ready')
        slides=page.locator('article.slide');errors=[]
        if slides.count()!=4: raise ValueError('Selected HTML must contain exactly four slides')
        for i,slide in enumerate(slides.all(),1):
            issues=slide.evaluate('''el=>{let a=[],r=el.getBoundingClientRect();if(r.width!==1080||r.height!==1350)a.push('size');for(const c of el.querySelectorAll('h1,h1 span,p,header,footer,.cover-brand,.cover-eyebrow,.cover-credit,.category')){if(getComputedStyle(c).display==='none'||!c.getClientRects().length)continue;const b=c.getBoundingClientRect();if(b.bottom>r.bottom+2||b.right>r.right+2||b.left<r.left-2||b.top<r.top-2||c.scrollWidth>c.clientWidth+2&&getComputedStyle(c).display!=='inline')a.push('overflow '+c.tagName)}for(const im of el.querySelectorAll('img'))if(!im.complete||!im.naturalWidth)a.push('image failed');if(el.classList.contains('signature-cover')){const lines=Array.from(el.querySelectorAll('h1>span'));if(lines.length!==2||lines.some(s=>!s.textContent.trim()||s.scrollWidth>s.clientWidth+2))a.push('cover headline')}return a}''')
            if issues:errors.append({'slide':i,'issues':issues})
        if errors:raise ValueError('Resolve layout issues before export: '+json.dumps(errors,ensure_ascii=False))
        out.mkdir(parents=True)
        for i,slide in enumerate(slides.all(),1):slide.screenshot(path=str(out/f'slide-{i:02d}.png'),animations='disabled')
        chromium.close()
    print('PNG_EXPORT_OK',out)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('--out',type=Path,required=True);p.add_argument('--browser');a=p.parse_args();export(a.source,a.out,a.browser)
