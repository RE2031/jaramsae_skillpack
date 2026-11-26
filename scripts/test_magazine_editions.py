"""Four-edition smoke test: synthetic images only."""
import json, tempfile, struct, zlib
from pathlib import Path
from render import build, render
from build_editor import build_editor
def chunk(k,d):
    return struct.pack('>I',len(d))+k+d+struct.pack('>I',zlib.crc32(k+d)&0xffffffff)
with tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp);slides=[]
    for i in range(4):
        w,h=400,500
        pixels=b''.join(b'\0'+bytes((70+i*25,140,185))*w for _ in range(h))
        path=root/f'fixture{i}.png'
        path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(pixels))+chunk(b'IEND',b''))
        slides.append({'title':'모래로 만드는\n작은 세상' if i==0 else '놀이 속 작은 발견','body':'' if i==0 else '모래를 담고 뒤집으며 다양한 모양을 살펴보았어요.','layout':'fullbleed-photo','eyebrow':'오늘의 놀이 기록','image':path.name,'image_approved':True,'image_kind':'generated','image_credit':'Synthetic fixture'})
    data={'institution':'햇살숲','goal':'test','style':'bold-photo-editorial','brand':{'primary':'#263B50','background':'#EAF6FD','accent':'#A8D8F0'},'draft':True,'posts':[{'category':'놀이','purpose':'test','caption':'fixture','hashtags':[],'slides':slides}]}
    source=root/'feed.json';folders=[]
    for variant in ['signature','modern','story','creative']:
        data['editorial_variant']=variant
        source.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
        out=root/variant;build(source,out);assert render(out,None),(out/'review-report.json').read_text()
        markup=(out/'editable/index.html').read_text()
        assert 'signature-cover' in markup
        if variant!='signature': assert 'magazine-interior edition-'+variant in markup
        else: assert 'magazine-interior' not in markup
        folders.append(out)
    build_editor(folders,root/'editor.html')
    assert (root/'editor.html').is_file()
    print('FOUR_EDITION_TEST_PASSED')
