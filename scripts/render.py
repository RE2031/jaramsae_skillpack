import argparse, html, json, shutil, sys, base64
from pathlib import Path
from tempfile import TemporaryDirectory
from jsonschema import validate
from playwright.sync_api import sync_playwright
from video import composite, prepare
ROOT=Path(__file__).resolve().parents[1]
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, 'reconfigure'):
        _stream.reconfigure(encoding='utf-8', errors='replace')
e=html.escape

def media_path(src, value, extensions):
    path = (src.parent / value).resolve()
    if not path.is_relative_to(src.parent.resolve()) or not path.is_file() or path.suffix.lower() not in extensions:
        raise ValueError('유효한 로컬 미디어 파일이 필요합니다: ' + value)
    return path

def magazine_body(data, post, s, art, sid, page, colors, label, platform, logo, clip):
    variant = data['body_style']
    total = len(post['slides']) + int(data.get('body_only', False))
    footer = f'<footer><span>{page:02d} / {total:02d}</span><span>출처 | {platform}</span></footer>'
    copy = f'<div class="category">{label}</div><h1>{e(s["title"])}</h1><p>{e(s["body"])}</p>'
    if variant == 'playful':
        aside = f'<div class="photo-aside">{e(s["aside"])}</div>' if s.get('aside') else ''
        content = f'<div class="art">{art}</div><span class="spark" aria-hidden="true">✦</span>{aside}<div class="mag-copy">{copy}</div>{footer}'
    elif variant == 'interview':
        issue = e(data.get('issue') or f'{data["institution"]} · 01')
        question = f'<div class="interview-question"><b>Q.</b> <span>{e(s["question"])}</span></div>' if s.get('question') else ''
        quote = f'<blockquote><b>A.</b> <span class="source-quote">{e(s["quote"])}</span></blockquote>' if s.get('quote') else ''
        content = f'<div class="issue">{issue}</div><div class="section-label">INTERVIEW</div><div class="art">{art}</div><div class="mag-copy">{copy}{question}{quote}</div>{footer}'
    else:
        brand = ''
        if variant == 'overlay':
            identity = f'<img src="{e(logo)}" alt="{e(data["institution"])}">' if logo else f'<span>{e(data["institution"])}</span>'
            brand = f'<div class="overlay-brand">{identity}</div>'
        if clip:
            art += f'<video src="{e(clip)}" preload="metadata" playsinline muted></video>'
        subtitle = f'<div class="video-subtitle">{e(s.get("subtitle") or s["title"])}</div>' if clip else ''
        content = f'<div class="art">{art}</div><div class="media-shade"></div>{brand}<div class="mag-copy">{copy}{subtitle}</div>{footer}'
    return f'<article class="slide magazine-card magazine-{variant} page-{page}" id="{sid}" style="{colors}">{content}</article>'

def build(src,out):
    data=json.loads(src.read_text(encoding='utf-8'))
    validate(data,json.loads((ROOT/'schemas/feed.schema.json').read_text(encoding='utf-8')))
    if out.exists(): raise ValueError('출력 폴더가 이미 존재합니다. 새 경로를 사용하세요.')
    # Check all image permissions and paths before creating outputs.
    # Bold photo editorial requires a traceable, approved image on every slide.
    body_style = data.get('body_style')
    notice = ('사진에는 실제 게시물 대상을 촬영하지 않은 예시 이미지가 포함되어 있습니다.' if body_style
              else '사진은 실제 기관 활동을 촬영한 것이 아닌 예시 이미지입니다.')
    if data.get('style') == 'bold-photo-editorial':
        for post in data['posts']:
            for slide in post['slides']:
                if not slide.get('image'):
                    raise ValueError('bold-photo-editorial은 모든 슬라이드에 승인된 사진이 필요합니다.')
                if not slide.get('image_kind') or not slide.get('image_credit'):
                    raise ValueError('bold-photo-editorial 사진은 image_kind와 image_credit를 기록해야 합니다.')
    if data['style'] == 'bold-photo-editorial' and not data.get('body_only',False):
        for post in data['posts']:
            cover = post['slides'][0]
            lines = cover['title'].split('\n')
            if len(lines) != 2 or any(not line.strip() for line in lines):
                raise ValueError('Signature Cover: title에는 비어 있지 않은 두 줄을 명시해야 합니다.')
            eyebrow = cover.get('eyebrow', post['category'])
            if not eyebrow.strip() or '\n' in eyebrow or '\r' in eyebrow:
                raise ValueError('Signature Cover: eyebrow는 활동을 나타내는 한 줄이어야 합니다.')
            if cover['body'].strip() or cover.get('details'):
                raise ValueError('Signature Cover: body/details는 비우고 설명은 다음 장 또는 caption에 작성하세요.')
            if cover.get('image_kind') == 'stock' and not cover.get('image_source','').strip():
                raise ValueError('Signature Cover: stock 사진은 image_source에 실제 제공처를 기록하세요.')
            if cover.get('image_kind') in {'stock','generated'}:
                if notice not in post['caption']:
                    post['caption'] += '\n\n' + notice
    if data['style']=='bold-photo-editorial':
        for post in data['posts']:
            if any(s.get('image_kind')=='stock' and not s.get('image_source','').strip() for s in post['slides']):
                raise ValueError('Stock photos require image_source on every slide.')
            if any(s.get('image_kind') in {'stock','generated'} for s in post['slides']):
                if notice not in post['caption']: post['caption'] += '\n\n'+notice
            for s in post['slides'][0 if data.get('body_only',False) else 1:]:
                if not s['body'].strip() or s.get('details'):
                    raise ValueError('기사형 본문에는 body를 작성하고 details는 비워 주세요.')
    clips = {}
    logo_source = media_path(src, data['logo'], {'.png','.jpg','.jpeg','.webp'}) if body_style == 'overlay' and data.get('logo') else None
    for i, post in enumerate(data['posts'], 1):
        for j, s in enumerate(post['slides'], 1):
            interior = j > 1 or data.get('body_only')
            if body_style == 'interview' and interior and s.get('quote'):
                if s['quote'] not in data.get('interview_source', '') or not s['quote'].strip():
                    raise ValueError(f'{j}장 인용문은 인터뷰 원문에 연속해서 그대로 있어야 합니다.')
            if body_style == 'video' and interior and s.get('video'):
                clips[i,j] = media_path(src, s['video'], {'.mp4','.mov','.webm','.m4v'})
            if s.get('image'):
                path=(src.parent/s['image']).resolve()
                if not s.get('image_approved') or not path.is_relative_to(src.parent.resolve()) or not path.is_file() or path.suffix.lower() not in {'.jpg','.jpeg','.png','.webp'}:
                    raise ValueError('허가되지 않았거나 유효하지 않은 이미지: '+s['image'])
            elif s['layout'] in {'photo','hero-left-copy','hero-right-copy','split-editorial','photo-caption'}: raise ValueError('photo 레이아웃에는 승인된 이미지가 필요합니다.')
            if s.get('image_kind') in {'stock','generated'} and not s.get('image_credit'):
                raise ValueError('예시 사진은 image_credit 표시가 필요합니다.')
    edit=out/'editable'; assets=edit/'assets'; assets.mkdir(parents=True)
    shutil.copy(ROOT/'templates/style.css',edit/'style.css')
    logo = ''
    if logo_source:
        logo = 'assets/brand-logo' + logo_source.suffix.lower()
        shutil.copy(logo_source, edit/logo)
        data['logo'] = logo
    elif body_style:
        data.pop('logo', None)
    blocks=[]; covers=[]; captions=[]
    variant=data.get('editorial_variant','signature')
    edition_class='' if body_style or variant=='signature' else ' edition-'+variant
    for i,post in enumerate(data['posts'],1):
        captions.append(f"## {i:02d}. {post['category']}\n\n{post['caption']}\n\n{' '.join(post['hashtags'])}\n")
        for j,s in enumerate(post['slides'],1):
            sid=f'post-{i:02d}-slide-{j:02d}'
            if body_style and (i,j) not in clips:
                s.pop('video', None)
            art=''
            if s.get('image'):
                source=(src.parent/s['image']).resolve(); target=assets/(sid+source.suffix.lower()); shutil.copy(source,target); s['image']='assets/'+target.name
                art=f'<img src="{e(s["image"],quote=True)}" alt="게시물 사진" style="object-position:{s.get("image_position","center")}">'
            b=data['brand']; colors=f'--primary:{b["primary"]};--bg:{b["background"]};--accent:{b["accent"]}'
            draft='<span class="draft">초안 · 게시 전 확인</span>' if data['draft'] else ''
            details=''.join(f'<div>{e(v)}</div>' for v in s.get('details',[]))
            credit=e(s.get('image_credit',''))
            has_image=' has-image' if s.get('image') else ' no-image'
            if data['style'] == 'bold-photo-editorial' and j == 1 and not data.get('body_only',False):
                lines = ''.join(f'<span>{e(line.strip())}</span>' for line in s['title'].split('\n'))
                eyebrow = e(s.get('eyebrow',post['category']).strip())
                platform = 'AI 생성' if s.get('image_kind') == 'generated' else (s.get('image_source') or s.get('image_credit') or '기관 제공')
                platform = platform.removeprefix('출처 | ').strip()
                zoom = s.get('image_zoom',1.15)
                x = s.get('image_focus_x',50)
                y = s.get('image_focus_y',50)
                photo = f'<img src="{e(s["image"],quote=True)}" alt="활동 사진" style="object-position:{x}% {y}%;transform:scale({zoom});transform-origin:{x}% {y}%">'
                blocks.append(f'<article class="slide preset-bold-photo-editorial signature-cover has-image{edition_class}" id="{sid}" style="{colors}"><div class="art">{photo}</div><div class="cover-brand">{e(data["institution"])}</div><div class="cover-copy"><div class="cover-eyebrow">{eyebrow}</div><h1>{lines}</h1></div><div class="cover-credit">출처 | {e(platform)}</div></article>')
                continue
            if data['style']=='bold-photo-editorial':
                page_num=j+int(data.get('body_only',False))
                page_total=len(post['slides'])+int(data.get('body_only',False))
                labels={2:'놀이의 시작',3:'아이들이 해본 일',4:'이어진 놀이'}
                label=e(s.get('eyebrow',labels.get(page_num,post['category'])))
                platform='AI 생성' if s.get('image_kind')=='generated' else (s.get('image_source') or s.get('image_credit') or '기관 제공')
                platform=e(platform.removeprefix('출처 | ').strip())
                if body_style:
                    clip = ''
                    if (i,j) in clips:
                        original = clips[i,j]
                        clip = 'assets/' + sid + '.mp4'
                        prepare(original, edit/clip)
                        s['video'] = clip
                    blocks.append(magazine_body(data,post,s,art,sid,page_num,colors,label,platform,logo,clip))
                    continue
                blocks.append(f'<article class="slide article-body edition-{variant} page-{page_num} has-image" id="{sid}" style="{colors}"><div class="art">{art}</div><div class="article-copy"><div class="category">{label}</div><h1>{e(s["title"])}</h1><p>{e(s["body"])}</p><footer><span>{page_num:02d} / {page_total:02d}</span><span>출처 | {platform}</span></footer></div></article>')
                continue
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

def export_video(slide, clip, output):
    with TemporaryDirectory() as temp:
        layer = Path(temp) / 'layer.png'
        slide.evaluate("""el=>{
            el.style.background='transparent';
            el.querySelector('.art').style.visibility='hidden';
            document.body.style.background='transparent';
        }""")
        try:
            slide.screenshot(path=str(layer), animations='disabled', omit_background=True)
        finally:
            slide.evaluate("""el=>{
                el.style.removeProperty('background');
                el.querySelector('.art').style.removeProperty('visibility');
                document.body.style.removeProperty('background');
            }""")
        composite(clip, layer, output)

def magazine_issues(slide):
    return slide.evaluate("""card=>{
        if(!card.classList.contains('magazine-card'))return [];
        const bounds=card.getBoundingClientRect();
        const copy=card.querySelector('.mag-copy').getBoundingClientRect();
        const footer=card.querySelector('footer').getBoundingClientRect();
        const issues=[];
        if(copy.bottom>footer.top+1)issues.push('본문이 바닥글과 겹칩니다');
        for(const node of card.querySelectorAll('.mag-copy,.issue,.overlay-brand,.photo-aside,.video-subtitle,blockquote')){
            const box=node.getBoundingClientRect();
            if(box.top<bounds.top-1||box.bottom>bounds.bottom+1||box.left<bounds.left-1||box.right>bounds.right+1||node.scrollWidth>node.clientWidth+2)
                issues.push('잘린 본문 요소: '+(node.className||node.tagName));
        }
        return issues;
    }""")

def render(out,browser_path):
    png=out/'png'; png.mkdir(exist_ok=True)
    errors=[]; files=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=browser_path, args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1080,'height':1350},device_scale_factor=1)
        source=(out/'editable/index.html').read_text(encoding='utf-8')
        source=source.replace('<link rel="stylesheet" href="style.css">','<style>'+ (out/'editable/style.css').read_text(encoding='utf-8')+'</style>')
        for asset in (out/'editable/assets').iterdir():
            mime={'jpg':'jpeg','jpeg':'jpeg','png':'png','webp':'webp'}.get(asset.suffix.lower()[1:])
            if not mime:
                continue
            source=source.replace('src="assets/'+asset.name+'"','src="data:image/'+mime+';base64,'+base64.b64encode(asset.read_bytes()).decode()+'"')
        page.set_content(source); page.evaluate('document.fonts.ready')
        for slide in page.locator('.slide').all():
            sid=slide.get_attribute('id'); files.append(sid)
            issues=slide.evaluate('''el=>{const r=el.getBoundingClientRect();let a=[];if(r.width!==1080||r.height!==1350)a.push('wrong size');for(const c of el.querySelectorAll('header,h1,p,footer,.category,.art,.details')){if(getComputedStyle(c).display==='none')continue;let b=c.getBoundingClientRect();if(b.bottom>r.bottom||b.right>r.right||b.left<r.left||b.top<r.top||(!c.classList.contains('art')&&c.scrollWidth>c.clientWidth+2))a.push('overflow '+c.tagName+' '+c.className)}if(el.classList.contains('signature-cover')){let spans=el.querySelectorAll('h1>span');if(spans.length!==2)a.push('cover headline must have two lines');for(const s of spans)if(s.scrollWidth>s.clientWidth+2)a.push('cover headline line overflow');for(const c of el.querySelectorAll('.cover-brand,.cover-eyebrow,.cover-credit'))if(c.scrollWidth>c.clientWidth+2)a.push('cover label overflow');if(el.querySelector('p,.details'))a.push('cover contains body copy');const brand=el.querySelector('.cover-brand');if(!brand||brand.children.length||el.querySelector('svg,.logo,.brand-logo'))a.push('brand must be plain text only')}if(el.classList.contains('article-body')){const art=el.querySelector('.art'),copy=el.querySelector('.article-copy');if(!art||!copy||art.getBoundingClientRect().bottom>copy.getBoundingClientRect().top+1||copy.scrollHeight>copy.clientHeight+2)a.push('article photo/text layout overflow');if(!el.querySelector('p')?.textContent.trim())a.push('article body missing')}for(const im of el.querySelectorAll('img'))if(!im.complete||!im.naturalWidth)a.push('image failed');return a}''')
            issues.extend(magazine_issues(slide))
            if issues: errors.append({'slide':sid,'issues':issues})
            slide.screenshot(path=str(png/(sid+'.png')),animations='disabled')
            clip = slide.locator('video')
            if not issues and clip.count():
                (out/'mp4').mkdir(exist_ok=True)
                export_video(slide, out/'editable'/clip.get_attribute('src'), out/'mp4'/(sid+'.mp4'))
        browser.close()
    feed=json.loads((out/'editable/feed.json').read_text(encoding='utf-8'))
    covers=[] if feed.get('body_only',False) else [s for s in files if s.endswith('slide-01')]
    expected=0 if feed.get('body_only',False) else len(feed['posts'])
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
