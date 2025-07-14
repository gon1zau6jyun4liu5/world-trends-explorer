#!/usr/bin/env python3
"""
World Trends Explorer - Instant Test Server
🌍 Minimal server for immediate testing without dependencies
Run with: python instant_test_server.py
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
from datetime import datetime, timedelta
import random

class TrendsTestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse URL
        url_parts = urllib.parse.urlparse(self.path)
        path = url_parts.path
        query_params = urllib.parse.parse_qs(url_parts.query)
        
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Type', 'application/json')
        
        # Route handling
        if path == '/api/trends/health':
            self.send_response(200)
            self.end_headers()
            response = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'service': 'World Trends Explorer API (Instant Test Mode)',
                'version': '1.2.2',
                'port': 5000,
                'note': 'Minimal test server - no dependencies required'
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif path == '/api/trends/countries':
            self.send_response(200)
            self.end_headers()
            countries = [
                {'name': 'United States', 'code': 'US'},
                {'name': 'South Korea', 'code': 'KR'},
                {'name': 'Japan', 'code': 'JP'},
                {'name': 'Germany', 'code': 'DE'},
                {'name': 'United Kingdom', 'code': 'GB'},
                {'name': 'France', 'code': 'FR'},
                {'name': 'Canada', 'code': 'CA'},
                {'name': 'Australia', 'code': 'AU'},
                {'name': 'Brazil', 'code': 'BR'},
                {'name': 'India', 'code': 'IN'}
            ]
            response = {
                'countries': countries,
                'timestamp': datetime.now().isoformat(),
                'total_countries': len(countries)
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif path == '/api/trends/trending':
            self.send_response(200)
            self.end_headers()
            geo = query_params.get('geo', ['US'])[0]
            
            trending_data = {
                'US': [
                    {'rank': 1, 'query': 'Olympics 2024'},
                    {'rank': 2, 'query': 'AI Technology'},
                    {'rank': 3, 'query': 'Climate Change'},
                    {'rank': 4, 'query': 'Cryptocurrency'},
                    {'rank': 5, 'query': 'Space Exploration'}
                ],
                'KR': [
                    {'rank': 1, 'query': '올림픽 2024'},
                    {'rank': 2, 'query': '인공지능'},
                    {'rank': 3, 'query': 'K-pop'},
                    {'rank': 4, 'query': '삼성전자'},
                    {'rank': 5, 'query': '비트코인'}
                ]
            }
            
            response = {
                'geo': geo,
                'country': geo,
                'timestamp': datetime.now().isoformat(),
                'trending_searches': trending_data.get(geo, trending_data['US'])
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif path == '/api/trends/search':
            keyword = query_params.get('keyword', [''])[0].strip()
            geo = query_params.get('geo', ['US'])[0]
            
            if not keyword:
                self.send_response(400)
                self.end_headers()
                response = {'error': 'Keyword parameter is required'}
                self.wfile.write(json.dumps(response).encode())
                return
            
            self.send_response(200)
            self.end_headers()
            
            # Generate mock time series data
            time_data = []
            start_date = datetime.now() - timedelta(days=365)
            for i in range(52):
                date = start_date + timedelta(weeks=i)
                value = random.randint(20, 100)
                time_data.append({
                    'date': date.isoformat(),
                    'value': value
                })
            
            # Generate mock regional data
            countries = ['United States', 'South Korea', 'Japan', 'Germany', 'United Kingdom']
            regional_data = []
            for country in countries:
                value = random.randint(10, 100)
                regional_data.append({
                    'geoName': country,
                    'geoCode': country[:2].upper(),
                    'value': value
                })
            
            response = {
                'keyword': keyword,
                'geo': geo,
                'timestamp': datetime.now().isoformat(),
                'interest_over_time': time_data,
                'interest_by_region': regional_data,
                'related_queries': {
                    'top': [
                        {'query': f'{keyword} technology', 'value': '100'},
                        {'query': f'{keyword} trends', 'value': '85'}
                    ],
                    'rising': [
                        {'query': f'{keyword} 2024', 'value': 'Breakout'},
                        {'query': f'{keyword} AI', 'value': '+300%'}
                    ]
                }
            }
            self.wfile.write(json.dumps(response).encode())
            
        else:
            self.send_response(404)
            self.end_headers()
            response = {'error': 'Endpoint not found'}
            self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        # Custom logging
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {format % args}")

if __name__ == '__main__':
    print("🌍 World Trends Explorer - Instant Test Server")
    print("=" * 50)
    print("🚀 Starting server on http://localhost:5000")
    print("📝 No dependencies required - pure Python!")
    print("🔍 Test endpoints:")
    print("   • Health: http://localhost:5000/api/trends/health")
    print("   • Countries: http://localhost:5000/api/trends/countries") 
    print("   • Search: http://localhost:5000/api/trends/search?keyword=AI")
    print("   • Trending: http://localhost:5000/api/trends/trending?geo=KR")
    print("=" * 50)
    print("💡 한국어 키워드 테스트: 인공지능, K-pop, 삼성전자")
    print("🛑 Stop server: Ctrl+C")
    print("")
    
    try:
        server = HTTPServer(('localhost', 5000), TrendsTestHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        print("💡 Try a different port or check if port 5000 is already in use")
