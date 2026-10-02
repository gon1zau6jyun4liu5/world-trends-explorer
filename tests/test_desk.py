"""Offline regression tests for feed failures, durable preferences, and API boundaries."""
from http.client import HTTPConnection
import io
import json
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
import desk_server as app

FEED = b'''<rss xmlns:ht="https://trends.google.com/trending/rss"><channel><item>
<title>A &amp; B</title><ht:approx_traffic>2000+</ht:approx_traffic>
<pubDate>Thu, 01 Oct 2026 09:00:00 GMT</pubDate>
<ht:news_item><ht:news_item_title>News</ht:news_item_title><ht:news_item_url>https://example.com/article</ht:news_item_url><ht:news_item_source>Publisher</ht:news_item_source></ht:news_item>
<ht:news_item><ht:news_item_url>javascript:alert(1)</ht:news_item_url></ht:news_item>
</item></channel></rss>'''


class DeskFixture:

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.desk = app.Desk(Path(self.temp.name) / 'data.sqlite3')

    def tearDown(self):
        self.temp.cleanup()


class DeskTests(DeskFixture, unittest.TestCase):
    def test_slow_failure_starts_backoff_at_failure_time(self):
        with patch.object(app.time,'time',side_effect=[1000,1090]), patch.object(self.desk,'fetch_items',side_effect=OSError('timeout')):
            self.desk.feed('KR')
        self.assertEqual(self.desk.retry_after['KR'],1150)
        with patch.object(app.time,'time',return_value=1149), patch.object(self.desk,'fetch_items') as fetch:
            self.desk.feed('KR')
            fetch.assert_not_called()

    def test_empty_google_refresh_preserves_previous_items_and_timestamp(self):
        items=app.parse_feed(FEED,'KR')
        with self.desk.db() as db:
            db.execute('INSERT INTO feeds VALUES (?,?,?)',('KR',1000,json.dumps(items)))
        with patch.object(app.time,'time',return_value=1700), patch.object(self.desk,'fetch_items',return_value=[]):
            result=self.desk.feed('KR')
        self.assertTrue(result['stale'])
        self.assertIn('error',result)
        self.assertEqual(result['items'],items)
        self.assertEqual(result['fetched'],1000)
        with self.desk.db() as db:
            self.assertEqual(db.execute("SELECT fetched FROM feeds WHERE country='KR'").fetchone()[0],1000)
        with patch.object(app.time,'time',return_value=1761), patch.object(self.desk,'fetch_items',return_value=items):
            self.assertFalse(self.desk.feed('KR')['stale'])

    def test_provider_cooldown_poll_allows_retry_at_provider_deadline(self):
        for geo, body in [('KR', FEED), ('CN', b'{"articles":[]}')]:
            with self.subTest(geo=geo):
                self.desk.google_until = 2000
                self.desk.news_next = 200
                for wall, monotonic in [(1998, 198), (1999, 199)]:
                    with patch.object(app.time, 'time', return_value=wall), patch.object(app.time, 'monotonic', return_value=monotonic), patch.object(app, 'urlopen') as request:
                        self.assertIn('error', self.desk.feed(geo))
                        request.assert_not_called()
                with patch.object(app.time, 'time', return_value=2000), patch.object(app.time, 'monotonic', return_value=200), patch.object(app, 'urlopen', return_value=io.BytesIO(body)) as request:
                    self.assertNotIn('error', self.desk.feed(geo))
                    request.assert_called_once()

    def test_polling_during_cooldown_does_not_postpone_recovery(self):
        with patch.object(app.time, 'time', return_value=1000), patch.object(app, 'urlopen', side_effect=OSError('offline')):
            self.desk.feed('KR')
        with patch.object(app.time, 'time', return_value=1030), patch.object(app, 'urlopen') as request:
            self.desk.feed('KR')
            request.assert_not_called()
            self.assertEqual(self.desk.retry_after['KR'], 1060)
        with patch.object(app.time, 'time', return_value=1061), patch.object(app, 'urlopen', return_value=io.BytesIO(FEED)):
            self.assertNotIn('error', self.desk.feed('KR'))

    def test_google_cooldown_is_set_before_slot_is_released(self):
        desk=self.desk
        class Slot:
            def __enter__(self): return self
            def __exit__(self, *args):
                self_deadline.append(desk.google_until)
        self_deadline=[]
        desk.google_slots=Slot()
        with patch.object(app.time, 'time', return_value=1000), patch.object(app, 'urlopen', side_effect=app.HTTPError('https://trends.google.com',429,'limited',{},None)):
            desk.feed('KR')
        self.assertEqual(self_deadline,[1900])

    def test_translation_is_cached_by_target_and_survives_restart(self):
        response=json.dumps({'responseStatus':200,'responseData':{'translatedText':'Hello &amp; world'}}).encode()
        with patch.object(app,'urlopen',return_value=io.BytesIO(response)) as request:
            self.assertEqual(self.desk.translate('안녕','en'),'Hello & world')
            self.assertEqual(app.Desk(self.desk.db_path).translate('안녕','en'),'Hello & world')
            request.assert_called_once()
        with patch.object(app,'urlopen',return_value=io.BytesIO(response)) as request:
            self.desk.translate('안녕','ja')
            request.assert_called_once()

    def test_long_translation_chunks_stay_within_utf8_limit(self):
        from urllib.parse import parse_qs, urlparse
        chunks=[]
        def translate_chunk(req, **kwargs):
            chunk=parse_qs(urlparse(req.full_url).query)['q'][0]
            chunks.append(chunk)
            return io.BytesIO(json.dumps({'responseStatus':200,'responseData':{'translatedText':'translated'}}).encode())
        text='Hello '+('가나다 😀 ' * 50)
        with patch.object(app,'urlopen',side_effect=translate_chunk):
            self.desk.translate(text,'en')
        self.assertGreater(len(chunks),1)
        self.assertTrue(all(len(chunk.encode())<=500 for chunk in chunks))
        self.assertEqual(''.join(chunks),text)

    def test_same_language_is_preserved_without_blocking_other_translations(self):
        response=json.dumps({'responseStatus':403,'responseDetails':'PLEASE SELECT TWO DISTINCT LANGUAGES','responseData':{'translatedText':'PLEASE SELECT TWO DISTINCT LANGUAGES'}}).encode()
        with patch.object(app,'urlopen',return_value=io.BytesIO(response)):
            self.assertEqual(self.desk.translate('A news headline','en'),'A news headline')
        self.assertEqual(self.desk.translation_until,0)
        with patch.object(app,'urlopen') as request:
            self.assertEqual(self.desk.translate('A news headline','en'),'A news headline')
            request.assert_not_called()

    def test_translation_quota_is_not_cached_as_a_translation(self):
        response=json.dumps({'responseStatus':200,'quotaFinished':True,'responseData':{'translatedText':'QUOTA EXCEEDED'}}).encode()
        with patch.object(app,'urlopen',return_value=io.BytesIO(response)) as request:
            for text in ['Hello','World']:
                with self.assertRaises(app.NewsUnavailable): self.desk.translate(text,'ko')
            request.assert_called_once()
        with self.desk.db() as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM translations').fetchone()[0],0)

    def test_news_http_429_throttles_other_countries(self):
        other = next(c['code'] for c in app.COVERAGE if c['source']=='gdelt' and c['code']!='CN')
        with patch.object(app.time, 'monotonic', return_value=100), patch.object(app, 'urlopen', side_effect=app.HTTPError('https://api.gdeltproject.org',429,'limited',{},None)):
            self.assertIn('제한', self.desk.feed('CN')['error'])
        with patch.object(app.time, 'monotonic', return_value=110), patch.object(app, 'urlopen') as request:
            self.assertIn('제한', self.desk.feed(other)['error'])
            request.assert_not_called()
            self.assertEqual(self.desk.news_next,160)

    def test_news_cache_reloads_without_network_and_marks_old_items(self):
        items=app.parse_news(json.dumps({'articles':[{'title':'Local story','url':'https://example.com/1'}]}), 'CN')
        with self.desk.db() as db:
            db.execute('INSERT INTO feeds VALUES (?,?,?)',('CN',1000,json.dumps(items)))
        restored=app.Desk(self.desk.db_path)
        with patch.object(app.time,'time',return_value=1700), patch.object(app,'urlopen') as request:
            data=restored.cached_news()['CN']
            request.assert_not_called()
            self.assertTrue(data['stale'])
            self.assertEqual(data['items'],items)
            self.assertIn('error',data)

    def test_google_rate_limit_stops_requests_across_countries(self):
        with patch.object(app, 'urlopen', side_effect=app.HTTPError('https://trends.google.com',429,'limited',{},None)) as request:
            first=self.desk.feed('TH')
            second=self.desk.feed('VN')
            self.assertIn('일시 제한',first['error'])
            self.assertIn('일시 제한',second['error'])
            self.assertEqual(request.call_count,1)

    def test_news_groups_near_duplicate_titles_without_search_volume(self):
        articles = [dict(title='A major election result announced today', url='https://a.example/1', domain='a.example', seendate='20261002T010000Z', socialimage='https://a.example/photo.jpg'),
                    dict(title='A major election result announced today!', url='https://b.example/2', domain='b.example'),
                    dict(title='Different story', url='javascript:alert(1)')]
        items = app.parse_news(json.dumps({'articles': articles}), 'CN')
        self.assertEqual(len(items), 1)
        self.assertEqual(len(items[0]['articles']), 2)
        self.assertEqual(items[0]['source'], 'gdelt')
        self.assertEqual(items[0]['traffic'], '')
        self.assertEqual(items[0]['published'], '2026-10-02T01:00:00+00:00')
        self.assertEqual(len(items[0]['thumbnails']), 1)
        for url in ['https://127.0.0.1/a', 'https://localhost/a', 'http://news.example/a', 'https://x.local/a']:
            self.assertEqual(app.news_image_url(url), '')

    def test_news_provider_rate_limit_is_visible_and_backed_off(self):
        with patch.object(app, 'urlopen', return_value=io.BytesIO(b'Please limit requests to one every 5 seconds')) as request:
            data = self.desk.feed('CN')
            self.assertIn('제한', data['error'])
            self.assertEqual(data['source'], 'gdelt')
            self.assertEqual(data['items'], [])
            self.desk.feed('CN')
            self.assertEqual(request.call_count, 1)

    def test_news_cache_uses_its_provider_and_preserves_source(self):
        body=json.dumps({'articles':[{'title':'Local news', 'url':'https://example.com/news'}]}).encode()
        with patch.object(app, 'urlopen', return_value=io.BytesIO(body)) as request:
            first=self.desk.feed('CN')
            self.assertEqual(first, self.desk.feed('CN'))
            self.assertIn('api.gdeltproject.org', request.call_args.args[0].full_url)
            self.assertEqual(first['items'][0]['source'], 'gdelt')

    def test_news_thumbnail_order_deduplication_and_url_validation(self):
        feed = b'''<rss xmlns:ht="https://trends.google.com/trending/rss"><channel><item>
        <title>Example</title><ht:picture>https://encrypted-tbn0.gstatic.com/images?q=first</ht:picture>
        <ht:news_item><ht:news_item_url>https://example.com/one</ht:news_item_url>
        <ht:news_item_source>First publisher</ht:news_item_source>
        <ht:news_item_picture>https://encrypted-tbn0.gstatic.com/images?q=first</ht:news_item_picture></ht:news_item>
        <ht:news_item><ht:news_item_url>https://example.com/two</ht:news_item_url>
        <ht:news_item_picture>https://encrypted-tbn1.gstatic.com/images?q=second</ht:news_item_picture></ht:news_item>
        <ht:news_item><ht:news_item_url>https://example.com/three</ht:news_item_url>
        <ht:news_item_picture>http://127.0.0.1/private</ht:news_item_picture></ht:news_item>
        </item></channel></rss>'''
        item = app.parse_feed(feed, 'KR')[0]
        self.assertEqual(len(item['thumbnails']), 2)
        self.assertEqual(item['thumbnails'][0]['source'], 'First publisher')
        self.assertTrue(item['thumbnails'][1]['url'].endswith('second'))
        self.assertEqual(app.parse_feed(FEED, 'KR')[0]['thumbnails'], [])
        for url in ['javascript:alert(1)', 'https://encrypted-tbn0.gstatic.com.evil.example/x',
                    'https://encrypted-tbn0.gstatic.com:bad/x', 'https://user:secret@encrypted-tbn0.gstatic.com/x']:
            self.assertEqual(app.safe_image_url(url), '')

    def test_parse_preserves_titles_and_rejects_unsafe_article_links(self):
        item = app.parse_feed(FEED, 'KR')[0]
        self.assertEqual(item['title'], 'A & B')
        self.assertEqual(item['traffic'], '2000+')
        self.assertEqual(len(item['articles']), 1)
        self.assertNotEqual(item['id'], app.parse_feed(FEED, 'JP')[0]['id'])

    def test_cache_deduplicates_requests_and_survives_restart(self):
        with patch.object(app, 'urlopen', return_value=io.BytesIO(FEED)) as request:
            first = self.desk.feed('KR')
            second = self.desk.feed('KR')
            self.assertEqual(first, second)
            self.assertEqual(request.call_count, 1)
        new = app.Desk(self.desk.db_path)
        with patch.object(app, 'urlopen', side_effect=AssertionError('Must use cache')):
            self.assertEqual(new.feed('KR')['items'], first['items'])

    def test_failed_refresh_keeps_old_data_and_backs_off(self):
        with self.desk.db() as db:
            db.execute('INSERT INTO feeds VALUES (?,?,?)', ('KR', time.time()-1000, json.dumps(app.parse_feed(FEED,'KR'))))
        with patch.object(app, 'urlopen', side_effect=OSError('offline')) as request:
            one = self.desk.feed('KR')
            two = self.desk.feed('KR')
            self.assertTrue(one['stale'])
            self.assertTrue(one['error'])
            self.assertEqual(len(two['items']), 1)
            self.assertEqual(request.call_count, 1)

    def test_initial_failure_is_not_reported_as_empty_success(self):
        with patch.object(app, 'urlopen', side_effect=OSError('offline')):
            data = self.desk.feed('JP')
            self.assertTrue(data['error'])
            self.assertIsNone(data['fetched'])
            self.assertFalse(data['stale'])

    def test_malformed_response_does_not_replace_cache(self):
        with patch.object(app, 'urlopen', return_value=io.BytesIO(b'<html>blocked</html>')):
            self.assertTrue(self.desk.feed('US')['error'])
        with self.desk.db() as db:
            self.assertEqual(db.execute('SELECT count(*) FROM feeds').fetchone()[0], 0)


class HTTPTests(DeskFixture, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.server = app.make_server(0, self.desk)
        self.host = f'127.0.0.1:{self.server.server_port}'
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        super().tearDown()

    def request(self, path, body=None, headers=None):
        connection = HTTPConnection('127.0.0.1', self.server.server_port, timeout=3)
        connection.request('POST' if body is not None else 'GET', path,
                           body=json.dumps(body) if body is not None else None, headers=headers or {})
        response = connection.getresponse()
        status, data = response.status, response.read()
        connection.close()
        return status, data

    def mutation_headers(self):
        return {'Origin': 'http://' + self.host, 'X-CSRF-Token': self.desk.csrf}

    def test_mutations_require_both_origin_and_csrf(self):
        body={'countries':['JP']}
        for headers in [{}, {'Origin':'http://'+self.host}, {'X-CSRF-Token':self.desk.csrf},
                        {'Origin':'https://evil.example','X-CSRF-Token':self.desk.csrf}]:
            self.assertEqual(self.request('/api/preferences',body,headers)[0],403)
        self.assertEqual(self.desk.selection(), ['KR','JP','US'])

    def test_preferences_persist_and_validate_country_count(self):
        self.assertEqual(self.request('/api/preferences',{'countries':['JP','GB']},self.mutation_headers())[0],200)
        self.assertEqual(app.Desk(self.desk.db_path).selection(), ['JP','GB'])
        for value in [[],['XX'],list(sorted(app.CODES)),'KR',[{}]]:
            self.assertEqual(self.request('/api/preferences',{'countries':value},self.mutation_headers())[0],400)

    def test_ui_language_and_visibility_persist_independently(self):
        self.assertEqual(self.request('/api/ui-preferences',{'language':'ja'})[0],403)
        for body in [{'language':'ja'},{'showUnavailable':True}]:
            self.assertEqual(self.request('/api/ui-preferences',body,self.mutation_headers())[0],200)
        self.assertEqual(app.Desk(self.desk.db_path).ui_preferences(),{'language':'ja','showUnavailable':True})
        self.assertEqual(json.loads(self.request('/api/bootstrap')[1])['uiPreferences']['language'],'ja')
        for body in [{'language':'fr'},{'language':[]},{'showUnavailable':1},{'other':True},{}]:
            self.assertEqual(self.request('/api/ui-preferences',body,self.mutation_headers())[0],400)

    def test_translation_api_requires_csrf_and_validates_input(self):
        self.assertEqual(self.request('/api/translate',{'text':'Hello','target':'ko'})[0],403)
        for body in [{'text':'','target':'ko'},{'text':[],'target':'ko'},{'text':'Hello','target':[]},{'text':'가'*1000,'target':'en'}]:
            self.assertEqual(self.request('/api/translate',body,self.mutation_headers())[0],400)
        with patch.object(self.desk,'translate',return_value='안녕하세요'):
            status,body=self.request('/api/translate',{'text':'Hello','target':'ko'},self.mutation_headers())
            self.assertEqual(status,200)
            self.assertEqual(json.loads(body)['text'],'안녕하세요')

    def test_display_counts_are_separate_persistent_and_protected(self):
        self.assertEqual(self.desk.display_counts(), {'world': 1, 'regional': 5})
        body = {'scope': 'world', 'count': 3}
        self.assertEqual(self.request('/api/display-preferences', body)[0], 403)
        self.assertEqual(self.request('/api/display-preferences', body, self.mutation_headers())[0], 200)
        self.assertEqual(app.Desk(self.desk.db_path).display_counts(), {'world': 3, 'regional': 5})
        self.assertEqual(self.desk.selection(), ['KR', 'JP', 'US'])
        for scope, count in [('world', True), ('world', -1), ('world', 99), ('world', '3'), ([], 1), ('other', 1)]:
            self.assertEqual(self.request('/api/display-preferences', {'scope': scope, 'count': count}, self.mutation_headers())[0], 400)
        data = json.loads(self.request('/api/bootstrap')[1])
        self.assertEqual(data['displayCounts'], {'world': 3, 'regional': 5})

    def test_bookmarks_use_server_feed_content_and_are_removable(self):
        item = app.parse_feed(FEED,'KR')[0]
        with self.desk.db() as db:
            db.execute('INSERT INTO feeds VALUES (?,?,?)', ('KR',time.time(),json.dumps([item])))
        body={'country':'KR','id':item['id'],'save':True,'title':'Injected'}
        self.assertEqual(self.request('/api/saved',body,self.mutation_headers())[0],200)
        self.assertEqual(self.desk.saved()[0]['title'],'A & B')
        body['save']=False
        self.assertEqual(self.request('/api/saved',body,self.mutation_headers())[0],200)
        self.assertEqual(self.desk.saved(),[])

    def test_only_supported_countries_and_public_assets_are_served(self):
        self.assertEqual(self.request('/api/trending?geo=../../secret')[0],400)
        for path in ['/.env','/.local/desk.sqlite3','/backend/desk_server.py','/../README.md']:
            self.assertEqual(self.request(path)[0],404)
        self.assertEqual(self.request('/')[0],200)
        self.assertEqual(self.request('/api/bootstrap',headers={'Host':'evil.example'})[0],403)


if __name__ == '__main__':
    unittest.main()
