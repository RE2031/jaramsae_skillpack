import argparse, html, json, shutil, sys, base64
from pathlib import Path
from jsonschema import validate
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
e=html.escape

def build(src,out):
    data=json.loads(src.read_text(encoding='utf-8'))
    validate(data,json.loads((ROOT/'schemas/feed.schema.json').read_text(encoding='utf-8')))
    if out.exists(): raise ValueError('출력 폴더가 이미 존재합니다. 새 경로를 사용하세요.')
    # Check all image permissions and paths before creating outputs.
    # Bold photo editorial requires a traceable, approved image on every slide.
    if data.get('style') == 'bold-photo-editorial':
        for post in data['posts']:
            for slide in post['slides']:
                if not slide.get('image'):
                    raise ValueError('bold-photo-editorial은 모든 슬라이드에 승인된 사진이 필요합니다.')
                if not slide.get('image_kind') or not slide.get('image_credit'):
                    raise ValueError('bold-photo-editorial 사진은 image_kind와 image_credit를 기록해야 합니다.')
    for post in data['posts']:
        for s in post['slides']:
            if s.get('image'):
                path=(src.parent/s['image']).resolve()
                if not s.get('image_approved') or not path.is_relative_to(src.parent.resolve()) or not path.is_file() or path.suffix.lower() not in {'.jpg','.jpeg','.png','.webp'}:
                    raise ValueError('허가되지 않았거나 유효하지 않은 이미지: '+s['image'])
            elif s['layout'] in {'photo','hero-left-copy','hero-right-copy','split-editorial','photo-caption'}: raise ValueError('photo 레이아웃에는 승인된 이미지가 필요합니다.')
            if s.get('image_kind') in {'stock','generated'} and not s.get('image_credit'):
                raise ValueError('예시 사진은 image_credit 표시가 필요합니다.')
    edit=out/'editable'; assets=edit/'assets'; assets.mkdir(parents=True)
    shutil.copy(ROOT/'templates/style.css',edit/'style.css')
    blocks=[]; covers=[]; captions=[]
    for i,post in enumerate(data['posts'],1):
        captions.append(f"## {i:02d}. {post['category']}\n\n{post['caption']}\n\n{' '.join(post['hashtags'])}\n")
        for j,s in enumerate(post['slides'],1):
            sid=f'post-{i:02d}-slide-{j:02d}'
            art=''
            if s.get('image'):
                source=(src.parent/s['image']).resolve(); target=assets/(sid+source.suffix.lower()); shutil.copy(source,target); s['image']='assets/'+target.name
                art=f'<img src="{e(s["image"],quote=True)}" alt="게시물 사진" style="object-position:{s.get("image_position","center")}">'
            b=data['brand']; colors=f'--primary:{b["primary"]};--bg:{b["background"]};--accent:{b["accent"]}'
            draft='<span class="draft">초안 · 게시 전 확인</span>' if data['draft'] else ''
            details=''.join(f'<div>{e(v)}</div>' for v in s.get('details',[]))
            credit=e(s.get('image_credit',''))
            has_image=' has-image' if s.get('image') else ' no-image'
            blocks.append(f'<article class="slide {s["layout"]} preset-{data["style"]}{has_image}" id="{sid}" style="{colors}"><header><span>{e(data["institution"])}</span>{draft}</header><div class="category">{e(post["category"])}</div><h1>{e(s["title"])}</h1><div class="art">{art}</div><p>{e(s["body"])}</p><div class="details">{details}</div><footer><span> {i:02d} · {e(post["category"])}</span><span>{credit or (str(j).zfill(2)+" / "+str(len(post["slides"])).zfill(2))}</span></footer></article>')
    (edit/'index.html').write_text('<!doctype html><html lang="ko"><head><meta charset="utf-8"><link rel="stylesheet" href="style.css"></head><body>'+''.join(blocks)+'</body></html>',encoding='utf-8')
    (edit/'feed.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'captions.md').write_text('\n'.join(captions),encoding='utf-8')
    sources=['# 이미지 출처 및 사용 권한','']
    for i,post in enumerate(data['posts'],1):
        for j,s in enumerate(post['slides'],1):
            if s.get('image'):
                sources.append(f'- {i:02d}-{j:02d}: {s.get("image_credit") or "기관 제공 이미지 (사용 권한 별도 확인)"}')
    (out/'sources.md').write_text('\n'.join(sources)+'\n',encoding='utf-8')

def render(out,browser_path):
    png=out/'png'; png.mkdir(exist_ok=True)
    errors=[]; files=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=browser_path, args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1080,'height':1350},device_scale_factor=1)
        source=(out/'editable/index.html').read_text(encoding='utf-8')
        source=source.replace('<link rel="stylesheet" href="style.css">','<style>'+ (out/'editable/style.css').read_text(encoding='utf-8')+'</style>')
        for asset in (out/'editable/assets').iterdir():
            mime={'jpg':'jpeg','jpeg':'jpeg','png':'png','webp':'webp'}[asset.suffix.lower()[1:]]
            source=source.replace('src="assets/'+asset.name+'"','src="data:image/'+mime+';base64,'+base64.b64encode(asset.read_bytes()).decode()+'"')
        page.set_content(source); page.evaluate('document.fonts.ready')
        for slide in page.locator('.slide').all():
            sid=slide.get_attribute('id'); files.append(sid)
            issues=slide.evaluate('''el=>{const r=el.getBoundingClientRect();let a=[];if(r.width!==1080||r.height!==1350)a.push('wrong size');for(const c of el.querySelectorAll('header,h1,p,footer,.category,.art,.details')){if(getComputedStyle(c).display==='none')continue;let b=c.getBoundingClientRect();if(b.bottom>r.bottom||b.right>r.right||b.left<r.left||b.top<r.top||c.scrollWidth>c.clientWidth+2)a.push('overflow '+c.tagName)}for(const im of el.querySelectorAll('img'))if(!im.complete||!im.naturalWidth)a.push('image failed');return a}''')
            if issues: errors.append({'slide':sid,'issues':issues})
            slide.screenshot(path=str(png/(sid+'.png')),animations='disabled')
        browser.close()
    covers=[s for s in files if s.endswith('slide-01')]
    expected=len(json.loads((out/'editable/feed.json').read_text(encoding='utf-8'))['posts'])
    if len(covers)!=expected: errors.append({'issue':f'expected {expected} covers'})
    def img(s):
        image_path=png/(s+'.png')
        uri='data:image/png;base64,'+base64.b64encode(image_path.read_bytes()).decode('ascii')
        return f'<a href="{uri}" target="_blank" rel="noopener"><img src="{uri}" alt="{s}" loading="lazy"></a>'
    preview='''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>인스타그램 피드 미리보기</title><style>*{box-sizing:border-box}body{font-family:Arial,"Malgun Gothic",sans-serif;background:#f5f4f1;color:#292722;max-width:1100px;margin:32px auto;padding:20px}h1{font-size:clamp(26px,4vw,40px)}.note{color:#6b675f}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}.grid img{width:100%;height:auto;display:block;box-shadow:0 3px 14px #00000012}@media(max-width:700px){body{margin:12px auto;padding:14px}.grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}}</style></head><body><h1>인스타그램 피드 미리보기</h1><p class="note">이미지가 HTML 안에 포함되어 있어 이 파일 하나만 전달해도 미리 볼 수 있습니다. 이미지를 누르면 큰 크기로 열립니다.</p><div class="grid covers">'''+''.join(map(img,covers))+'''</div><h2>전체 슬라이드</h2><div class="grid">'''+''.join(map(img,files))+'''</div></body></html>'''
    (out/'preview.html').write_text(preview,encoding='utf-8')
    report={'automatic_checks_passed':not errors,'slide_count':len(files),'cover_count':len(covers),'errors':errors,'manual_review_required':['기관 사실 및 연락처','사진 공개 동의 및 외부 전송 권한','한국어 맞춤법','색 대비 및 디자인 완성도','게시 승인']}
    (out/'review-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False)); return not errors

def main():
    p=argparse.ArgumentParser();p.add_argument('input',nargs='?',type=Path);p.add_argument('--out',required=True,type=Path);p.add_argument('--browser');p.add_argument('--rerender',action='store_true');a=p.parse_args()
    if not a.rerender:
        if not a.input: p.error('input required')
        build(a.input.resolve(),a.out.resolve())
    return 0 if render(a.out.resolve(),a.browser) else 1
if __name__=='__main__': sys.exit(main())
