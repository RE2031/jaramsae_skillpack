"""End-to-end signature cover smoke test using a synthetic technical fixture."""
import json
import struct
import tempfile
import zlib
from pathlib import Path
from render import build, render

def chunk(kind, data):
    return struct.pack(">I",len(data))+kind+data+struct.pack(">I",zlib.crc32(kind+data)&0xffffffff)

with tempfile.TemporaryDirectory() as directory:
    root=Path(directory)
    w,h=1080,1350
    pixels=b"".join(b"\x00"+bytes((125,155,175) if y<800 else (180,135,95))*w for y in range(h))
    (root/"fixture.png").write_bytes(b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",struct.pack(">IIBBBBB",w,h,8,2,0,0,0))+chunk(b"IDAT",zlib.compress(pixels))+chunk(b"IEND",b""))
    slide={"title":"블록 하나로 만드는\n나만의 작은 세상","body":"","eyebrow":"오늘의 놀이 기록","layout":"fullbleed-photo","image":"fixture.png","image_approved":True,"image_kind":"generated","image_credit":"Synthetic technical fixture","image_zoom":1.15,"image_focus_x":50,"image_focus_y":54}
    data={"institution":"햇살숲","goal":"technical test","style":"bold-photo-editorial","brand":{"primary":"#302D25","background":"#F7F3EA","accent":"#788052"},"draft":True,"posts":[{"category":"놀이","purpose":"test","caption":"technical fixture","hashtags":[],"slides":[slide]}]}
    source=root/"feed.json"
    def save():
        source.write_text(json.dumps(data,ensure_ascii=False),encoding="utf-8")
    save()
    out=root/"output"
    build(source,out)
    markup=(out/"editable/index.html").read_text(encoding="utf-8")
    assert "signature-cover" in markup
    assert "<span>블록 하나로 만드는</span><span>나만의 작은 세상</span>" in markup
    assert "오늘의 놀이 기록" in markup and "햇살숲" in markup
    assert "출처 | AI 생성" in markup
    assert "<p>" not in markup
    assert render(out,None), (out/"review-report.json").read_text(encoding="utf-8")
    assert (out/"png/post-01-slide-01.png").is_file()
    for field,value in [("title","한 줄 제목"),("body","표지 설명은 금지")]:
        original=slide[field]
        slide[field]=value
        save()
        try:
            build(source,root/("invalid-"+field))
        except ValueError:
            pass
        else:
            raise AssertionError("invalid cover accepted: "+field)
        slide[field]=original
    print("SIGNATURE_COVER_TEST_PASSED")
