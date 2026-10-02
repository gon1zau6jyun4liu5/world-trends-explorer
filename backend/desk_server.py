#!/usr/bin/env python3
"""Country news desk. Python stdlib only; no paid API or browser cookies needed."""
import argparse
from contextlib import contextmanager
import hashlib
import html
import ipaddress
import json
import mimetypes
import re
from datetime import datetime, timezone
import os
from pathlib import Path
import secrets
import signal
import sqlite3
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse, urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
TTL = 600
COVERAGE = json.loads((ROOT / 'backend' / 'countries.json').read_text())
COUNTRIES = [(c['code'], c['name'], c['region'], c['mapId']) for c in COVERAGE]
COUNTRY_INFO = {c['code']: c for c in COVERAGE}
CODES = {row[0] for row in COUNTRIES}
NS = {'ht': 'https://trends.google.com/trending/rss'}


def safe_url(value):
    try:
        parsed = urlparse(value or '')
        return value if parsed.scheme in ('https', 'http') and parsed.hostname and not parsed.username else ''
    except ValueError:
        return ''


def safe_image_url(value):
    """Only use the Google-hosted thumbnail URLs supplied with the RSS feed."""
    value = safe_url(value)
    parsed = urlparse(value)
    if (parsed.scheme == 'https' and parsed.netloc in {
            host + suffix for host in (f'encrypted-tbn{i}.gstatic.com' for i in range(4))
            for suffix in ('', ':443')}):
        return value
    return ''


def parse_feed(body, geo):
    root = ET.fromstring(body)
    if root.tag != 'rss':
        raise ValueError('Unexpected feed format')
    items = []
    for item in root.findall('./channel/item')[:20]:
        title = html.unescape(item.findtext('title', '')).strip()
        if not title:
            continue
        articles = []
        for article in item.findall('ht:news_item', NS):
            url = safe_url(article.findtext('ht:news_item_url', '', NS))
            if url:
                articles.append({
                    'title': html.unescape(article.findtext('ht:news_item_title', '', NS)),
                    'url': url,
                    'source': html.unescape(article.findtext('ht:news_item_source', '', NS)),
                    'image': safe_image_url(article.findtext('ht:news_item_picture', '', NS)),
                })
        thumbnails = []
        seen_images = set()
        # Google's related-news order is the relevance signal available in RSS.
        for article in articles:
            if article['image'] and article['image'] not in seen_images:
                seen_images.add(article['image'])
                thumbnails.append({'url': article['image'], 'source': article['source'],
                                   'article_url': article['url']})
        picture = safe_image_url(item.findtext('ht:picture', '', NS))
        if picture and picture not in seen_images:
            thumbnails.append({'url': picture,
                               'source': html.unescape(item.findtext('ht:picture_source', '', NS)),
                               'article_url': ''})
        items.append({
            'id': hashlib.sha256((geo + ':' + title).encode()).hexdigest()[:24],
            'title': title, 'country': geo,
            'traffic': item.findtext('ht:approx_traffic', '', NS),
            'published': item.findtext('pubDate', ''),
            'articles': articles[:5],
            'thumbnails': thumbnails[:6],
            'thumbnail_version': 1,
        })
    return items


def news_image_url(value):
    value = safe_url(value)
    host = urlparse(value).hostname or ''
    if not value.startswith('https://') or '.' not in host or host.endswith(('.local', '.localhost', '.internal')):
        return ''
    try:
        if not ipaddress.ip_address(host).is_global:
            return ''
    except ValueError:
        pass
    return value


def parse_news(body, geo):
    data = json.loads(body)
    if not isinstance(data, dict) or not isinstance(data.get('articles'), list):
        raise ValueError('Unexpected news format')
    groups, seen = [], set()
    for a in data['articles']:
        title = html.unescape(a.get('title', '')).strip()
        url = safe_url(a.get('url', ''))
        if not title or not url or url in seen:
            continue
        seen.add(url)
        tokens = set(re.findall(r'\w+', title.casefold()))
        group = next((g for g in groups if len(tokens) >= 4 and
                      len(tokens & g['_tokens']) / max(1, len(tokens | g['_tokens'])) >= .65), None)
        article = {'title': title, 'url': url, 'source': a.get('domain', '')}
        if group:
            group['articles'].append(article)
            continue
        try:
            published = datetime.strptime(a.get('seendate', ''), '%Y%m%dT%H%M%SZ').replace(tzinfo=timezone.utc).isoformat()
        except ValueError:
            published = ''
        groups.append({'id': hashlib.sha256((geo + ':gdelt:' + url).encode()).hexdigest()[:24],
                       'title': title, 'country': geo, 'traffic': '', 'published': published,
                       'articles': [article], 'thumbnails': [{'url': news_image_url(a.get('socialimage', '')), 'source': a.get('domain', ''), 'article_url': url}] if news_image_url(a.get('socialimage', '')) else [], 'thumbnail_version': 1,
                       'source': 'gdelt', '_tokens': tokens})
    for g in groups:
        g.pop('_tokens')
        g['articles'] = g['articles'][:5]
    return groups[:20]


class NewsUnavailable(Exception):
    pass


class ProviderCooldown(NewsUnavailable):
    """An existing provider gate must not install a new country retry timer."""
    pass


class Desk:
    def __init__(self, db_path):
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self.csrf = secrets.token_urlsafe(32)
        self.locks = {code: threading.Lock() for code in CODES}
        self.retry_after = {}
        self.news_lock = threading.Lock()
        self.news_next = 0
        self.google_slots = threading.BoundedSemaphore(4)
        self.google_until = 0
        self.last_error = {}
        self.translation_lock = threading.Lock()
        self.translation_until = 0
        with self.db() as db:
            db.execute('CREATE TABLE IF NOT EXISTS feeds (country TEXT PRIMARY KEY, fetched REAL, body TEXT)')
            db.execute('CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, body TEXT)')
            db.execute('CREATE TABLE IF NOT EXISTS saved (id TEXT PRIMARY KEY, body TEXT, saved_at REAL)')
            db.execute('CREATE TABLE IF NOT EXISTS translations (target TEXT, original TEXT, translated TEXT, PRIMARY KEY(target, original))')

    @contextmanager
    def db(self):
        connection = sqlite3.connect(self.db_path, timeout=10)
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def selection(self):
        with self.db() as db:
            row = db.execute("SELECT body FROM settings WHERE key='countries'").fetchone()
        return json.loads(row[0]) if row else ['KR', 'JP', 'US']

    def display_counts(self):
        with self.db() as db:
            row = db.execute("SELECT body FROM settings WHERE key='display_counts'").fetchone()
        return json.loads(row[0]) if row else {'world': 1, 'regional': 5}

    def ui_preferences(self):
        with self.db() as db:
            row = db.execute("SELECT body FROM settings WHERE key='ui'").fetchone()
        return {'language': 'ko', 'showUnavailable': False} | (json.loads(row[0]) if row else {})

    @contextmanager
    def translation_slot(self):
        if not self.translation_lock.acquire(timeout=1):
            raise NewsUnavailable('translation_unavailable')
        try:
            yield
        finally:
            self.translation_lock.release()

    def translate(self, text, target):
        # Only public headlines, on demand. Never submit memories via the provider's set API.
        with self.translation_slot():
            with self.db() as db:
                row = db.execute('SELECT translated FROM translations WHERE target=? AND original=?', (target, text)).fetchone()
            if row:
                return row[0]
            if time.time() < self.translation_until:
                raise NewsUnavailable('translation_unavailable')
            chunks, chunk = [], ''
            for char in text:
                if len((chunk + char).encode('utf-8')) > 500:
                    split = chunk.rfind(' ') + 1
                    if not split or len(chunk[:split].encode('utf-8')) < len(char.encode('utf-8')):
                        split = len(chunk)
                    chunks.append(chunk[:split])
                    chunk = chunk[split:]
                chunk += char
            if chunk:
                chunks.append(chunk)
            result = []
            for chunk in chunks:
                params = urlencode({'q': chunk, 'langpair': 'autodetect|' + target})
                try:
                    with urlopen(Request('https://api.mymemory.translated.net/get?' + params,
                                         headers={'User-Agent': 'WorldTrendsExplorer/2.0'}), timeout=15) as response:
                        data = json.loads(response.read(100_001))
                    translated = data.get('responseData', {}).get('translatedText')
                    if (not data.get('quotaFinished') and str(data.get('responseStatus')) == '403'
                            and data.get('responseDetails') == 'PLEASE SELECT TWO DISTINCT LANGUAGES'):
                        # Auto-detection matched the requested target language.
                        result.append(chunk)
                        continue
                    if data.get('quotaFinished') or str(data.get('responseStatus')) != '200' or not isinstance(translated, str) or not translated.strip():
                        self.translation_until = time.time() + (3600 if data.get('quotaFinished') else 60)
                        raise NewsUnavailable('translation_unavailable')
                    translated = html.unescape(translated)
                    # Preserve a source separator if the provider strips it, but
                    # never invent a separator at a UTF-8 size-only split.
                    separator = re.search(r'\s+$', chunk)
                    if separator and not re.search(r'\s$', translated):
                        translated += separator.group()
                    result.append(translated)
                except Exception:
                    self.translation_until = max(self.translation_until, time.time() + 60)
                    raise NewsUnavailable('translation_unavailable') from None
            translated = ''.join(result)
            with self.db() as db:
                db.execute('INSERT OR REPLACE INTO translations VALUES (?,?,?)', (target, text, translated))
            return translated

    def fetch_items(self, geo):
        if COUNTRY_INFO[geo]['source'] == 'google':
            with self.google_slots:
                if time.time() < self.google_until:
                    raise ProviderCooldown('Google이 요청을 일시 제한했습니다. 잠시 후 자동으로 다시 확인합니다.')
                req = Request('https://trends.google.com/trending/rss?geo=' + geo,
                              headers={'User-Agent': 'WorldTrendsExplorer/2.0'})
                try:
                    with urlopen(req, timeout=12) as response:
                        body = response.read(2_000_001)
                except HTTPError as exc:
                    if exc.code == 429:
                        self.google_until = time.time() + 900
                        exc.close()
                        raise ProviderCooldown('Google이 요청을 일시 제한했습니다. 잠시 후 자동으로 다시 확인합니다.') from None
                    raise
                if len(body) > 2_000_000:
                    raise ValueError('Feed too large')
                return parse_feed(body, geo)
        # Nonblocking global gate: do not queue hundreds of country requests.
        if not self.news_lock.acquire(blocking=False):
            raise ProviderCooldown('다른 나라의 뉴스를 조회 중입니다. 잠시 후 다시 눌러 주세요.')
        try:
            if time.monotonic() < self.news_next:
                raise ProviderCooldown('뉴스 제공처의 요청 간격 제한입니다. 잠시 후 다시 눌러 주세요.')
            self.news_next = time.monotonic() + 6
            query = 'sourcecountry:' + COUNTRY_INFO[geo]['newsCountry']
            params = urlencode(dict(query=query, mode='artlist', format='json',
                                    maxrecords=100, timespan='24h', sort='hybridrel'))
            with urlopen(Request('https://api.gdeltproject.org/api/v2/doc/doc?' + params,
                                 headers={'User-Agent': 'WorldTrendsExplorer/2.0'}), timeout=12) as response:
                body = response.read(2_000_001)
            if len(body) > 2_000_000:
                raise ValueError('News too large')
            if b'Please limit requests' in body:
                self.news_next = time.monotonic() + 60
                raise NewsUnavailable('현지 뉴스 제공처가 현재 요청을 제한하고 있습니다. 1분 후 다시 시도해 주세요.')
            return parse_news(body, geo)
        except HTTPError as exc:
            if exc.code == 429:
                self.news_next = time.monotonic() + 60
                exc.close()
                raise NewsUnavailable('현지 뉴스 제공처가 현재 요청을 제한하고 있습니다. 1분 후 다시 시도해 주세요.') from None
            raise
        finally:
            self.news_lock.release()

    def feed(self, geo):
        with self.locks[geo]:
            now = time.time()
            with self.db() as db:
                row = db.execute('SELECT fetched, body FROM feeds WHERE country=?', (geo,)).fetchone()
            if row and COUNTRY_INFO[geo]['source'] == 'google' and not json.loads(row[1]):
                row = None  # Legacy empty caches are not evidence of a successful fetch.
            if row and now - row[0] < TTL and all(
                    item.get('thumbnail_version') == 1 for item in json.loads(row[1])):
                return dict(country=geo, source=COUNTRY_INFO[geo]['source'], fetched=row[0], stale=False, items=json.loads(row[1]))
            if self.retry_after.get(geo, 0) > now:
                return dict(country=geo, source=COUNTRY_INFO[geo]['source'],
                            fetched=row[0] if row else None, stale=bool(row),
                            items=json.loads(row[1]) if row else [],
                            error=self.last_error.get(geo, '잠시 후 다시 확인해 주세요.'))
            try:
                items = self.fetch_items(geo)
                if not items and COUNTRY_INFO[geo]['source'] == 'google':
                    raise NewsUnavailable('Google에서 화제를 받지 못했습니다. 잠시 후 다시 확인해 주세요.')
                fetched = time.time()
                with self.db() as db:
                    db.execute('INSERT OR REPLACE INTO feeds VALUES (?,?,?)',
                               (geo, fetched, json.dumps(items, ensure_ascii=False)))
                    for item in items:
                        saved = db.execute('SELECT body FROM saved WHERE id=?', (item['id'],)).fetchone()
                        if saved:
                            previous = json.loads(saved[0])
                            if not previous.get('thumbnail_version'):
                                previous.update(thumbnails=item['thumbnails'], thumbnail_version=1)
                                db.execute('UPDATE saved SET body=? WHERE id=?',
                                           (json.dumps(previous, ensure_ascii=False), item['id']))
                return dict(country=geo, source=COUNTRY_INFO[geo]['source'], fetched=fetched, stale=False, items=items)
            except Exception as exc:
                if not isinstance(exc, ProviderCooldown):
                    self.retry_after[geo] = time.time() + 60
                self.last_error[geo] = str(exc) if isinstance(exc, NewsUnavailable) else '최신 소식을 가져오지 못했습니다. 잠시 후 다시 확인해 주세요.'
                return dict(country=geo, source=COUNTRY_INFO[geo]['source'], fetched=row[0] if row else None, stale=bool(row),
                            items=json.loads(row[1]) if row else [],
                            error=str(exc) if isinstance(exc, NewsUnavailable) else '최신 소식을 가져오지 못했습니다. 잠시 후 다시 확인해 주세요.')

    def cached_news(self):
        # Bootstrap reads only local data; it must never spend provider quota.
        now = time.time()
        with self.db() as db:
            rows = db.execute('SELECT country, fetched, body FROM feeds').fetchall()
        feeds = {}
        for code, fetched, body in rows:
            if COUNTRY_INFO.get(code, {}).get('source') != 'gdelt':
                continue
            stale = now - fetched >= TTL
            feeds[code] = dict(country=code, source='gdelt', fetched=fetched,
                               stale=stale, items=json.loads(body))
            if stale:
                feeds[code]['error'] = '이전에 받은 현지 뉴스입니다. 뉴스 다시 확인을 눌러 최신 보도를 조회하세요.'
        return feeds

    def saved(self):
        with self.db() as db:
            rows = db.execute('SELECT body FROM saved ORDER BY saved_at DESC').fetchall()
        return [json.loads(row[0]) for row in rows]


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def guard(self):
        host = self.headers.get('Host', '')
        if host not in self.server.allowed_hosts:
            self.send_json({'error': '허용되지 않은 주소입니다.'}, 403)
            return False
        if self.client_address[0] == '127.0.0.1' and host in (
                f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'):
            return True
        if self.server.access:
            return self.server.access.guard(self)
        self.send_json({'error': '원격 접속이 설정되지 않았습니다.'}, 403)
        return False

    def send_body(self, body, content_type, status=200):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data: https:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, data, status=200):
        self.send_body(json.dumps(data, ensure_ascii=False).encode(), 'application/json; charset=utf-8', status)

    def do_GET(self):
        if not self.guard():
            return
        path = urlparse(self.path).path
        desk = self.server.app
        if path == '/api/bootstrap':
            return self.send_json({'countries': COVERAGE, 'newsFeeds': desk.cached_news(), 'uiPreferences': desk.ui_preferences(),
                                   'displayCounts': desk.display_counts(), 'selected': desk.selection(), 'saved': desk.saved(), 'csrf': desk.csrf})
        if path == '/api/trending':
            geo = parse_qs(urlparse(self.path).query).get('geo', [''])[0]
            if geo not in CODES:
                return self.send_json({'error': '지원하지 않는 국가입니다.'}, 400)
            return self.send_json(desk.feed(geo))
        if path == '/api/health':
            return self.send_json({'status': 'ok', 'source': 'Google Trends RSS', 'version': '2.0'})
        if path == '/api/saved':
            return self.send_json(desk.saved())
        # Explicit allowlist: never serve source, database, environment or other repository files.
        assets = {'/': 'desk/index.html', '/desk.css': 'desk/desk.css', '/desk.js': 'desk/desk.js', '/globe.js': 'desk/globe.js', '/i18n.js': 'desk/i18n.js',
                  '/vendor/d3.min.js': 'desk/vendor/d3.min.js',
                  '/vendor/topojson.min.js': 'desk/vendor/topojson.min.js',
                  '/vendor/countries.json': 'desk/vendor/countries.json'}
        if path not in assets:
            return self.send_json({'error': '페이지를 찾을 수 없습니다.'}, 404)
        file = ROOT / 'frontend' / assets[path]
        content_type = mimetypes.guess_type(str(file))[0] or 'application/octet-stream'
        return self.send_body(file.read_bytes(), content_type + '; charset=utf-8')

    def do_POST(self):
        if not self.guard():
            return
        desk = self.server.app
        if (self.headers.get('Origin') != 'http://' + self.headers.get('Host', '') or
                not secrets.compare_digest(self.headers.get('X-CSRF-Token', '').encode(), desk.csrf.encode())):
            return self.send_json({'error': '페이지를 새로고침한 뒤 다시 시도하세요.'}, 403)
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 8192:
                raise ValueError()
            body = json.loads(self.rfile.read(length))
            if not isinstance(body, dict):
                raise ValueError()
        except (ValueError, UnicodeError):
            return self.send_json({'error': '입력을 확인하세요.'}, 400)
        path = urlparse(self.path).path
        if path == '/api/ui-preferences':
            if not body or set(body) - {'language', 'showUnavailable'} or ('language' in body and body['language'] not in ('ko', 'ja', 'en')) or ('showUnavailable' in body and type(body['showUnavailable']) is not bool):
                return self.send_json({'error': 'invalid_preferences'}, 400)
            with desk.db() as db:
                db.execute('BEGIN IMMEDIATE')
                row = db.execute("SELECT body FROM settings WHERE key='ui'").fetchone()
                prefs = {'language': 'ko', 'showUnavailable': False}
                prefs.update(json.loads(row[0]) if row else {})
                prefs.update(body)
                db.execute("INSERT OR REPLACE INTO settings VALUES ('ui',?)", (json.dumps(prefs),))
            return self.send_json({'uiPreferences': prefs})
        if path == '/api/translate':
            text, target = body.get('text'), body.get('target')
            if not isinstance(text, str) or not text.strip() or len(text.encode('utf-8')) > 2500 or target not in ('ko', 'ja', 'en'):
                return self.send_json({'error': 'invalid_translation'}, 400)
            try:
                return self.send_json({'text': desk.translate(text, target), 'target': target, 'provider': 'MyMemory'})
            except NewsUnavailable:
                return self.send_json({'error': 'translation_unavailable'}, 503)
        if path == '/api/display-preferences':
            scope, count = body.get('scope'), body.get('count')
            if not isinstance(scope, str) or scope not in ('world', 'regional') or type(count) is not int or count not in (0, 1, 3, 5, 10):
                return self.send_json({'error': '표시할 화제 수를 확인해 주세요.'}, 400)
            with desk.db() as db:
                db.execute('BEGIN IMMEDIATE')
                row = db.execute("SELECT body FROM settings WHERE key='display_counts'").fetchone()
                counts = json.loads(row[0]) if row else {'world': 1, 'regional': 5}
                counts[scope] = count
                db.execute("INSERT OR REPLACE INTO settings VALUES ('display_counts',?)", (json.dumps(counts),))
            return self.send_json({'displayCounts': counts})
        if path == '/api/preferences':
            selected = body.get('countries')
            if not isinstance(selected, list) or not 1 <= len(selected) <= 8 or any(not isinstance(c,str) or c not in CODES for c in selected):
                return self.send_json({'error': '국가를 1~8개 선택해 주세요.'}, 400)
            selected = list(dict.fromkeys(selected))
            with desk.db() as db:
                db.execute("INSERT OR REPLACE INTO settings VALUES ('countries',?)", (json.dumps(selected),))
            return self.send_json({'selected': selected})
        if path == '/api/saved':
            geo, ident = body.get('country'), body.get('id')
            if not isinstance(geo, str) or geo not in CODES or not isinstance(ident, str) or len(ident) != 24 or type(body.get('save')) is not bool:
                return self.send_json({'error': '항목을 확인하세요.'}, 400)
            with desk.db() as db:
                if body['save']:
                    row = db.execute('SELECT body FROM feeds WHERE country=?', (geo,)).fetchone()
                    item = next((x for x in json.loads(row[0]) if x['id'] == ident), None) if row else None
                    if item is None:
                        return self.send_json({'error': '목록을 새로고침해 주세요.'}, 404)
                    db.execute('INSERT OR REPLACE INTO saved VALUES (?,?,?)', (ident, json.dumps(item, ensure_ascii=False), time.time()))
                else:
                    db.execute('DELETE FROM saved WHERE id=?', (ident,))
            return self.send_json({'saved': desk.saved()})
        return self.send_json({'error': '경로를 확인하세요.'}, 404)


def make_server(port, desk):
    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    server.app = desk
    server.allowed_hosts = {f'127.0.0.1:{server.server_port}', f'localhost:{server.server_port}'}
    server.access = None
    return server


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=49480)
    parser.add_argument('--data-dir', type=Path, default=ROOT / '.local')
    args = parser.parse_args()
    desk = Desk(args.data_dir / 'desk.sqlite3')
    local = make_server(args.port, desk)
    remote = None
    portal = os.environ.get('LOCAL_APPS_PORTAL')
    if portal:
        sys.path.insert(0, portal)
        import access
        host = access.network().get('tailscaleHost')
        if host:
            if ipaddress.ip_address(host) not in ipaddress.ip_network('100.64.0.0/10') or not access.AUTH.exists():
                raise ValueError('포털의 Tailscale 및 로그인 설정을 확인하세요.')
            remote = ThreadingHTTPServer((host, args.port), Handler)
            local.allowed_hosts.add(f'{host}:{args.port}')
            remote.allowed_hosts = local.allowed_hosts
            remote.app = desk
            remote.access = access
            threading.Thread(target=remote.serve_forever, daemon=True).start()
            print(f'Tailscale: http://{host}:{args.port}', flush=True)
    def stop(*_):
        threading.Thread(target=local.shutdown, daemon=True).start()
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    print(f'Local: http://127.0.0.1:{args.port}', flush=True)
    try:
        local.serve_forever()
    finally:
        local.server_close()
        if remote:
            remote.shutdown()
            remote.server_close()


if __name__ == '__main__':
    main()
