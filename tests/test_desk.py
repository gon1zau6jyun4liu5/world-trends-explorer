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
