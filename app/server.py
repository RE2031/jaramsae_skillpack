#!/usr/bin/env python3
"""Local card-news studio backed by the command-line renderer."""
import argparse
import base64
import io
import json
import os
import subprocess
import sys
import traceback
import re
from tempfile import TemporaryDirectory
from uuid import uuid4
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from export_editor_selection import export
from make_editions import EDITIONS

APP = Path(__file__).resolve().parent
OUT = ROOT / 'output'
RUNS = OUT / 'runs'
EYEBROWS = ['매거진', '이야기의 시작', '이야기 속 한 장면', '이야기를 마치며']
BRAND = {'primary': '#2E332B', 'background': '#F6F1E7', 'accent': '#B4843C'}
MIME = {
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.html': 'text/html; charset=utf-8',
    '.json': 'application/json; charset=utf-8',
    '.md': 'text/markdown; charset=utf-8',
    '.css': 'text/css; charset=utf-8',
    '.mp4': 'video/mp4',
}


def load_profile():
    for path in sorted((ROOT / 'profiles').glob('*/brand-profile.json')):
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except Exception:
            continue
    return {}


def title_words(text):
    return [w for w in ' '.join((text or '').split()).split(' ')
            if w and w not in ('·', '|', '/', '-')]


def clamp_line(line, limit=11):
    """Keep a cover line inside the 94px nowrap headline box."""
    if len(line) <= limit:
        return line, False
    cut = line[:limit]
    if ' ' in cut:
        cut = cut[:cut.rfind(' ')]
    return (cut.strip() or line[:limit]), True


def two_lines(raw, fallback):
    """Return exactly two title lines, splitting the description when needed."""
    raw = (raw or '').strip()
    if '\n' in raw:
        parts = [p.strip() for p in raw.split('\n') if p.strip()]
        if len(parts) >= 2:
            return parts[0] + '\n' + parts[1]
        if parts:
            return parts[0] + '\n' + fallback
    words = [w for w in ' '.join(raw.split()).split(' ') if w]
    if not words:
        words = [w for w in fallback.split(' ') if w]
    if not words:
        words = ['오늘의 기록']
    if len(words) == 1:
        return words[0] + '\n' + fallback
    mid = max(1, len(words) // 2)
    return ' '.join(words[:mid]) + '\n' + ' '.join(words[mid:])


def save_photo(data_url, path):
    payload = data_url.split(',', 1)[1] if ',' in data_url else data_url
    raw = base64.b64decode(payload)
    image = Image.open(io.BytesIO(raw)).convert('RGB')
    if image.width > 1600:
        image = image.resize((1600, round(image.height * 1600 / image.width)), Image.LANCZOS)
    image.save(path, quality=92, subsampling=0)
    return path


def build_feed(payload, run_dir, profile):
    institution = (payload.get('displayName') or profile.get('institution') or '').strip()
    if not institution:
        raise ValueError('표시 이름을 입력해 주세요.')
    slides = payload.get('slides') or []
    if len(slides) != 4:
        raise ValueError('사진 4장이 필요합니다 (표지 + 사진 1~3).')
    activity = ' '.join((payload.get('topic') or payload.get('activity') or '').split())
    if not activity:
        raise ValueError('이번 게시물 주제를 입력해 주세요.')
    photo_dir = run_dir / 'photos'
    photo_dir.mkdir(parents=True, exist_ok=True)
    for index, slide in enumerate(slides, 1):
        if not slide.get('photo'):
            raise ValueError(f'{index}번째 사진이 없습니다.')
        save_photo(slide['photo'], photo_dir / f'photo-{index:02d}.jpg')

    activity_title = ' '.join(title_words(activity)) or '오늘의 기록'
    feed_slides = []
    captions = []
    warnings = []
    any_example = False
    for index, slide in enumerate(slides):
        description = ' '.join((slide.get('description') or '').split())
        captions.append(description)
        owned = bool(slide.get('owned'))
        any_example = any_example or not owned
        user_body = ' '.join((slide.get('body') or '').split())
        body = '' if index == 0 else (user_body or description)
        if index > 0 and not body:
            raise ValueError(f'{index + 1}번째 사진의 설명이나 본문을 적어 주세요.')
        if len(body) > 180:
            body = body[:180]
            warnings.append(f'{index + 1}번째 본문이 180자를 넘어 잘렸습니다.')
        title = (slide.get('title') or '').strip()
        if index == 0:
            if title:
                if len(title.splitlines()) != 2 or any(not line.strip() for line in title.splitlines()):
                    raise ValueError('표지 제목은 줄바꿈 한 번으로 두 줄을 적어 주세요.')
                title = '\n'.join(title.splitlines())
            else:
                title = '\n'.join(clamp_line(line)[0] for line in two_lines(activity_title, '이야기').split('\n'))
        else:
            title = title or EYEBROWS[index]
        if len(title) > 60:
            raise ValueError(f'{index + 1}번째 제목을 60자 이내로 써 주세요.')
        entry = {
            'title': title,
            'eyebrow': (slide.get('eyebrow') or (activity if index == 0 and len(activity) <= 18 else EYEBROWS[index]))[:40],
            'body': body[:180],
            'layout': 'fullbleed-photo',
            'image': f'photos/photo-{index + 1:02d}.jpg',
            'image_approved': True,
            'image_kind': 'provided' if owned else 'stock',
            'image_source': '사용자 제공' if owned else '예시 이미지',
            'image_credit': '사용자 제공 사진' if owned else '예시 이미지',
        }
        if index == 0:
            for field in ('image_zoom', 'image_focus_x', 'image_focus_y'):
                if field in slide:
                    entry[field] = slide[field]
        else:
            for field in ('aside', 'question', 'quote', 'subtitle'):
                value = (slide.get(field) or '').strip()
                if value:
                    entry[field] = value
            if slide.get('video') and payload.get('selection') in ('all','video'):
                entry['video'] = f'photos/video-{index + 1:02d}.mp4'
                (run_dir/entry['video']).write_bytes(base64.b64decode(slide['video'].split(',',1)[-1],validate=True))
        feed_slides.append(entry)

    head = ' '.join(part for part in [institution, activity, '기록입니다.'] if part)
    paragraphs = [head] + [text for text in captions if text]
    if any_example:
        paragraphs.append('사진에는 실제 게시물 대상을 촬영하지 않은 예시 이미지가 포함되어 있습니다.')
    caption = '\n\n'.join(paragraphs)
    hashtags = ['#' + re.sub(r'[^\w]','',value) for value in (institution,activity) if re.search(r'\w',value)]

    feed = {
        'institution': institution,
        'goal': activity,
        'style': 'bold-photo-editorial',
        'brand': {key:(profile.get('colors') or profile.get('brand') or {}).get(key,value) for key,value in BRAND.items()},
        'draft': True,
        'posts': [{
            'category': activity,
            'purpose': activity,
            'caption': caption,
            'hashtags': hashtags,
            'slides': feed_slides,
        }],
    }
    if payload.get('logo') and payload.get('selection') in ('all','overlay'):
        raw = base64.b64decode(payload['logo'].split(',',1)[-1],validate=True)
        with Image.open(io.BytesIO(raw)) as logo:
            logo.thumbnail((640,640))
            logo.convert('RGBA').save(photo_dir/'brand-logo.png')
        feed['logo'] = 'photos/brand-logo.png'
    for field in ('interview_source','issue'):
        if payload.get(field):
            feed[field] = payload[field]
    return feed, caption, hashtags, warnings


def handle_render(payload):
    profile = load_profile()
    selection = payload.get('selection') or 'all'
    if selection != 'all' and selection not in EDITIONS:
        raise ValueError('본문 스타일을 선택해 주세요.')
    payload['selection'] = selection
    run_id = uuid4().hex
    run_dir = RUNS / run_id
    run_dir.mkdir(parents=True)

    feed, caption, hashtags, warnings = build_feed(payload, run_dir, profile)
    feed_path = run_dir / 'feed.json'
    feed_path.write_text(json.dumps(feed, ensure_ascii=False, indent=2), encoding='utf-8')

    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    command = [sys.executable, str(ROOT / 'scripts/make_editions.py'), str(feed_path),
               '--out', str(run_dir / 'editions'), '--export-url',f'/api/export?run={run_id}']
    if selection != 'all':
        command.extend(['--style',selection])
    proc = subprocess.run(
        command,
        capture_output=True, text=True, encoding='utf-8', errors='replace',
        env=env, cwd=str(ROOT), timeout=900,
    )
    if proc.returncode != 0:
        tail = ((proc.stdout or '') + (proc.stderr or ''))[-1500:]
        raise ValueError('렌더 실패: ' + tail.strip())

    editions = [{
        'id': edition,
        'name': EDITIONS[edition],
        'slides': [
            {'poster': f'/files/runs/{run_id}/editions/{edition}/png/{stem}.png',
             'video': f'/files/runs/{run_id}/editions/{edition}/mp4/{stem}.mp4'
             if (run_dir/'editions'/edition/'mp4'/f'{stem}.mp4').is_file() else None}
            for stem in (f'post-01-slide-{n:02d}' for n in range(1,5))
        ],
    } for edition in (EDITIONS if selection == 'all' else [selection])]
    return {
        'ok': True,
        'runId': run_id,
        'editions': editions,
        'caption': caption,
        'hashtags': hashtags,
        'warnings': warnings,
        'editor': f'/files/runs/{run_id}/editions/editor.html',
    }


def handle_export(payload):
    run_id = str(payload.get('runId') or '')
    edition = str(payload.get('edition') or '')
    if edition not in EDITIONS or not re.fullmatch(r'[a-f0-9]{32}',run_id):
        raise ValueError('시안을 다시 선택해 주세요.')
    source = RUNS / run_id / 'editions' / edition / 'editable' / 'index.html'
    if not source.is_file():
        raise ValueError('해당 시안을 찾지 못했습니다.')
    folder = OUT / f'approved-{run_id}-{edition}-{uuid4().hex[:8]}'
    with TemporaryDirectory(dir=OUT) as temp:
        staging = Path(temp)/'cards'
        export(source,staging,edits=payload.get('edits'))
        files = sorted(p.name for p in staging.iterdir())
        staging.rename(folder)
    return {
        'ok': True,
        'folder': str(folder.relative_to(ROOT)),
        'files': [f'/files/{folder.name}/{name}' for name in files],
    }


class Handler(BaseHTTPRequestHandler):
    server_version = 'JaramsaeStudio/1.0'
    protocol_version = 'HTTP/1.1'

    def log_message(self, fmt, *args):
        print('%s - %s' % (self.address_string(), fmt % args), flush=True)

    def send_file(self, path):
        path = Path(path)
        if not path.is_file():
            return self.send_error(404)
        size = path.stat().st_size
        if path.suffix == '.mp4':
            header = self.headers.get('Range')
            match = re.fullmatch(r'bytes=(\d*)-(\d*)',header or '')
            if header and (not match or not any(match.groups())):
                return self.send_error(416)
            start, end = 0, size - 1
            if match:
                first,last = match.groups()
                start = int(first) if first else max(0,size - int(last))
                end = min(end,int(last)) if first and last else end
                if not 0 <= start <= end < size:
                    self.send_response(416)
                    self.send_header('Content-Range',f'bytes */{size}')
                    self.send_header('Content-Length','0')
                    self.end_headers()
                    return
            self.send_response(206 if match else 200)
            self.send_header('Content-Type','video/mp4')
            self.send_header('Accept-Ranges','bytes')
            self.send_header('Content-Length',str(end - start + 1))
            if match:
                self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
            self.end_headers()
            with path.open('rb') as stream:
                stream.seek(start)
                left = end - start + 1
                while left:
                    chunk = stream.read(min(left,65536))
                    self.wfile.write(chunk)
                    left -= len(chunk)
            return
        data = path.read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', MIME.get(path.suffix.lower(), 'application/octet-stream'))
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, payload, status=200):
        data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(data)

    def read_json(self):
        length = int(self.headers.get('Content-Length') or 0)
        if not 0 < length <= 180 * 1024**2:
            self.close_connection = True
            raise ValueError('요청이 비어 있거나 업로드 용량이 너무 큽니다.')
        return json.loads(self.rfile.read(length).decode('utf-8'))

    def do_GET(self):
        path = unquote(urlparse(self.path).path)
        if path in ('/', '/index.html'):
            return self.send_file(APP / 'static' / 'index.html')
        if path == '/studio-style.css':
            return self.send_file(ROOT/'templates/style.css')
        if path == '/api/profile':
            return self.send_json({'profile': load_profile()})
        if path.startswith('/files/'):
            target = (OUT / path[len('/files/'):]).resolve()
            if not target.is_relative_to(OUT.resolve()):
                return self.send_error(403)
            return self.send_file(target)
        return self.send_error(404)

    def do_POST(self):
        path = urlparse(self.path).path
        try:
            payload = self.read_json()
            if path == '/api/render':
                return self.send_json(handle_render(payload))
            if path == '/api/export':
                query = parse_qs(urlparse(self.path).query)
                if 'run' in query:
                    payload['runId'] = query['run'][0]
                return self.send_json(handle_export(payload))
            return self.send_error(404)
        except ValueError as error:
            return self.send_json({'ok': False, 'error': str(error)}, 400)
        except Exception as error:  # noqa: BLE001 - surface the reason to the page
            traceback.print_exc()
            return self.send_json({'ok': False, 'error': str(error)}, 500)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    OUT.mkdir(exist_ok=True)
    RUNS.mkdir(exist_ok=True)
    class StudioServer(ThreadingHTTPServer):
        request_queue_size = 32

    httpd = StudioServer((args.host, args.port), Handler)
    print(f'STUDIO_READY http://{args.host}:{args.port}/', flush=True)
    httpd.serve_forever()


if __name__ == '__main__':
    main()
