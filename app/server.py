#!/usr/bin/env python3
"""Local studio: four photos + short descriptions -> four TIO editions.

Runs on 127.0.0.1 only and shells out to scripts/make_editions.py, so the
rendered PNGs are identical to the command-line pipeline.
"""
import argparse
import base64
import io
import json
import os
import shutil
import subprocess
import sys
import time
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
APP = Path(__file__).resolve().parent
OUT = ROOT / 'output'
RUNS = OUT / 'runs'
EDITIONS = ['signature', 'modern', 'story', 'creative']
NAMES = {
    'signature': 'A · Signature',
    'modern': 'B · Modern',
    'story': 'C · Story',
    'creative': 'D · Creative',
}
EYEBROWS = ['오늘의 놀이 기록', '놀이의 시작', '아이들이 해본 일', '이어진 놀이']
BRAND = {'primary': '#2E332B', 'background': '#F6F1E7', 'accent': '#B4843C'}
MIME = {
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.html': 'text/html; charset=utf-8',
    '.json': 'application/json; charset=utf-8',
    '.md': 'text/markdown; charset=utf-8',
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
    institution = (profile.get('institution') or '').strip()
    if not institution:
        raise ValueError('기관 프로필이 없습니다. profiles/<id>/brand-profile.json 을 먼저 저장해 주세요.')
    slides = payload.get('slides') or []
    if len(slides) != 4:
        raise ValueError('사진 4장이 필요합니다 (표지 + 사진 1~3).')
    activity = ' '.join((payload.get('activity') or '').split())
    fallback = activity or '오늘의 기록'

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
        lines = []
        clipped = False
        for line in two_lines(slide.get('title') or description, activity_title).split('\n'):
            fitted, cut = clamp_line(line)
            lines.append(fitted)
            clipped = clipped or cut
        if clipped:
            warnings.append(f'{index + 1}번째 제목이 길어 두 줄에 맞게 줄였습니다.')
        feed_slides.append({
            'title': '\n'.join(lines)[:60],
            'eyebrow': (slide.get('eyebrow') or EYEBROWS[index])[:40],
            'body': body[:180],
            'layout': 'fullbleed-photo',
            'image': f'photos/photo-{index + 1:02d}.jpg',
            'image_approved': True,
            'image_kind': 'institution' if owned else 'stock',
            'image_source': '기관 제공' if owned else '예시 이미지',
            'image_credit': '기관 제공 사진' if owned else '예시 이미지 · 실제 기관 활동 사진 아님',
        })

    head = ' '.join(part for part in [institution, activity, '기록입니다.'] if part)
    paragraphs = [head] + [text for text in captions if text]
    if any_example:
        paragraphs.append('사진은 실제 기관 활동을 촬영한 것이 아닌 예시 이미지입니다.')
    caption = '\n\n'.join(paragraphs)
    hashtags = ['#' + institution.replace(' ', ''), '#놀이기록', '#어린이집일상']

    feed = {
        'institution': institution,
        'goal': '학부모에게 아이들의 일상과 활동 전달',
        'style': 'bold-photo-editorial',
        'brand': dict(BRAND),
        'draft': True,
        'posts': [{
            'category': '오늘의 놀이 기록',
            'purpose': activity or '오늘의 놀이 기록',
            'caption': caption,
            'hashtags': hashtags,
            'slides': feed_slides,
        }],
    }
    return feed, caption, hashtags, warnings


def handle_render(payload):
    profile = load_profile()
    run_id = time.strftime('%y%m%d-%H%M%S')
    run_dir = RUNS / run_id
    if run_dir.exists():
        raise ValueError('잠시 후 다시 시도해 주세요 (같은 초에 두 번 요청).')
    run_dir.mkdir(parents=True)

    feed, caption, hashtags, warnings = build_feed(payload, run_dir, profile)
    feed_path = run_dir / 'feed.json'
    feed_path.write_text(json.dumps(feed, ensure_ascii=False, indent=2), encoding='utf-8')

    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    proc = subprocess.run(
        [sys.executable, str(ROOT / 'scripts/make_editions.py'), str(feed_path),
         '--out', str(run_dir / 'editions')],
        capture_output=True, text=True, encoding='utf-8', errors='replace',
        env=env, cwd=str(ROOT), timeout=900,
    )
    if proc.returncode != 0:
        tail = ((proc.stdout or '') + (proc.stderr or ''))[-1500:]
        raise ValueError('렌더 실패: ' + tail.strip())

    editions = [{
        'id': edition,
        'name': NAMES[edition],
        'slides': [f'/files/runs/{run_id}/editions/{edition}/png/post-01-slide-{n:02d}.png'
                   for n in range(1, 5)],
    } for edition in EDITIONS]
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
    if edition not in EDITIONS:
        raise ValueError('시안을 다시 선택해 주세요.')
    source = RUNS / run_id / 'editions' / edition / 'png'
    if not source.is_dir():
        raise ValueError('해당 시안 PNG를 찾지 못했습니다.')
    folder = OUT / f'approved-{run_id}-{edition}'
    if folder.exists():
        shutil.rmtree(folder)
    shutil.copytree(source, folder)
    files = sorted(p.name for p in folder.glob('*.png'))
    return {
        'ok': True,
        'folder': str(folder.relative_to(ROOT)),
        'files': [f'/files/approved-{run_id}-{edition}/{name}' for name in files],
    }


class Handler(BaseHTTPRequestHandler):
    server_version = 'JaramsaeStudio/1.0'

    def log_message(self, fmt, *args):
        print('%s - %s' % (self.address_string(), fmt % args), flush=True)

    def send_file(self, path):
        path = Path(path)
        if not path.is_file():
            return self.send_error(404)
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
        if length <= 0:
            raise ValueError('빈 요청입니다.')
        return json.loads(self.rfile.read(length).decode('utf-8'))

    def do_GET(self):
        path = unquote(urlparse(self.path).path)
        if path in ('/', '/index.html'):
            return self.send_file(APP / 'static' / 'index.html')
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
    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f'STUDIO_READY http://{args.host}:{args.port}/', flush=True)
    httpd.serve_forever()


if __name__ == '__main__':
    main()
