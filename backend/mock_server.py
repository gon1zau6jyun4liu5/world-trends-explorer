#!/usr/bin/env python3
"""
World Trends Explorer - Mock Server for Testing
🌍 Realistic test data server when Google Trends API is unavailable
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import random
import datetime
from datetime import timedelta

app = Flask(__name__)
CORS(app)

# Mock trending data by country
TRENDING_DATA = {
    'US': [
        {'rank': 1, 'query': 'Olympics 2024'},
        {'rank': 2, 'query': 'AI Technology'},
        {'rank': 3, 'query': 'Climate Change'},
        {'rank': 4, 'query': 'Cryptocurrency'},
        {'rank': 5, 'query': 'Space Exploration'},
        {'rank': 6, 'query': 'Electric Vehicles'},
        {'rank': 7, 'query': 'Machine Learning'},
        {'rank': 8, 'query': 'Remote Work'},
        {'rank': 9, 'query': 'Sustainable Energy'},
        {'rank': 10, 'query': 'Quantum Computing'}
    ],
    'KR': [
        {'rank': 1, 'query': '올림픽 2024'},
        {'rank': 2, 'query': '인공지능'},
        {'rank': 3, 'query': 'K-pop'},
        {'rank': 4, 'query': '삼성전자'},
        {'rank': 5, 'query': '비트코인'},
        {'rank': 6, 'query': '넷플릭스'},
        {'rank': 7, 'query': '테슬라'},
        {'rank': 8, 'query': '메타버스'},
        {'rank': 9, 'query': '블록체인'},
        {'rank': 10, 'query': 'ChatGPT'}
    ],
    'JP': [
        {'rank': 1, 'query': 'オリンピック 2024'},
        {'rank': 2, 'query': '人工知能'},
        {'rank': 3, 'query': 'アニメ'},
        {'rank': 4, 'query': 'トヨタ'},
        {'rank': 5, 'query': 'ソニー'},
        {'rank': 6, 'query': '任天堂'},
        {'rank': 7, 'query': 'ポケモン'},
        {'rank': 8, 'query': 'ロボット'},
        {'rank': 9, 'query': '宇宙開発'},
        {'rank': 10, 'query': '再生可能エネルギー'}
    ],
    'DE': [
        {'rank': 1, 'query': 'Olympia 2024'},
        {'rank': 2, 'query': 'Künstliche Intelligenz'},
        {'rank': 3, 'query': 'Klimawandel'},
        {'rank': 4, 'query': 'Elektroautos'},
        {'rank': 5, 'query': 'Erneuerbare Energie'},
        {'rank': 6, 'query': 'Fußball WM'},
        {'rank': 7, 'query': 'Tesla'},
        {'rank': 8, 'query': 'Bitcoin'},
        {'rank': 9, 'query': 'Nachhaltigkeit'},
        {'rank': 10, 'query': 'Innovation'}
    ]
}

# Country data for regional interest
COUNTRIES = [
    {'name': 'United States', 'code': 'US'},
    {'name': 'Germany', 'code': 'DE'},
    {'name': 'United Kingdom', 'code': 'GB'},
    {'name': 'France', 'code': 'FR'},
    {'name': 'Japan', 'code': 'JP'},
    {'name': 'South Korea', 'code': 'KR'},
    {'name': 'Canada', 'code': 'CA'},
    {'name': 'Australia', 'code': 'AU'},
    {'name': 'Brazil', 'code': 'BR'},
    {'name': 'India', 'code': 'IN'},
    {'name': 'China', 'code': 'CN'},
    {'name': 'Russia', 'code': 'RU'},
    {'name': 'Italy', 'code': 'IT'},
    {'name': 'Spain', 'code': 'ES'},
    {'name': 'Netherlands', 'code': 'NL'},
    {'name': 'Sweden', 'code': 'SE'},
    {'name': 'Norway', 'code': 'NO'},
    {'name': 'Denmark', 'code': 'DK'},
    {'name': 'Finland', 'code': 'FI'},
    {'name': 'Switzerland', 'code': 'CH'}
]

def generate_time_series_data(keyword, base_value=50):
    """Generate realistic time series data"""
    data = []
    start_date = datetime.datetime.now() - timedelta(days=365)
    
    for i in range(52):  # 52 weeks
        date = start_date + timedelta(weeks=i)
        # Add some realistic variation
        trend = base_value + random.randint(-30, 30)
        trend = max(0, min(100, trend))  # Clamp between 0-100
        
        data.append({
            'date': date.isoformat(),
            'value': trend
        })
    
    return data

def generate_regional_data(keyword):
    """Generate realistic regional interest data"""
    regional_data = []
    
    for country in COUNTRIES:
        # Generate realistic interest values
        value = random.randint(10, 100)
        
        regional_data.append({
            'geoName': country['name'],
            'geoCode': country['code'],
            'value': value
        })
    
    # Sort by value descending
    regional_data.sort(key=lambda x: x['value'], reverse=True)
    return regional_data

def generate_related_queries(keyword):
    """Generate realistic related queries"""
    
    # Generic related queries based on keyword
    if 'ai' in keyword.lower() or '인공지능' in keyword:
        top_queries = [
            {'query': 'machine learning', 'value': '100'},
            {'query': 'artificial intelligence jobs', 'value': '85'},
            {'query': 'AI chatbot', 'value': '75'},
            {'query': 'deep learning', 'value': '65'},
            {'query': 'neural networks', 'value': '55'}
        ]
        rising_queries = [
            {'query': 'ChatGPT', 'value': 'Breakout'},
            {'query': 'AI ethics', 'value': '+1200%'},
            {'query': 'generative AI', 'value': '+800%'},
            {'query': 'AI regulation', 'value': '+500%'},
            {'query': 'AI safety', 'value': '+300%'}
        ]
    else:
        # Generic related queries
        top_queries = [
            {'query': f'{keyword} news', 'value': '100'},
            {'query': f'{keyword} trends', 'value': '85'},
            {'query': f'{keyword} analysis', 'value': '70'},
            {'query': f'{keyword} data', 'value': '60'},
            {'query': f'{keyword} research', 'value': '50'}
        ]
        rising_queries = [
            {'query': f'{keyword} 2024', 'value': 'Breakout'},
            {'query': f'{keyword} future', 'value': '+500%'},
            {'query': f'{keyword} market', 'value': '+300%'},
            {'query': f'{keyword} investment', 'value': '+200%'},
            {'query': f'{keyword} technology', 'value': '+150%'}
        ]
    
    return {
        'top': top_queries,
        'rising': rising_queries
    }

@app.route('/api/trends/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'service': 'World Trends Explorer API (Mock Mode)',
        'note': 'Using realistic test data for demonstration'
    })

@app.route('/api/trends/trending')
def get_trending():
    """Get trending searches by country"""
    geo = request.args.get('geo', 'US')
    
    trending_data = TRENDING_DATA.get(geo, TRENDING_DATA['US'])
    
    return jsonify({
        'geo': geo,
        'country': geo,
        'timestamp': datetime.datetime.now().isoformat(),
        'trending_searches': trending_data,
        'note': 'Mock data for demonstration'
    })

@app.route('/api/trends/search')
def search_trends():
    """Search trends for a keyword"""
    keyword = request.args.get('keyword', '').strip()
    geo = request.args.get('geo', 'US')
    timeframe = request.args.get('timeframe', 'today 12-m')
    
    if not keyword:
        return jsonify({'error': 'Keyword parameter is required'}), 400
    
    # Generate realistic mock data
    response_data = {
        'keyword': keyword,
        'geo': geo,
        'timeframe': timeframe,
        'timestamp': datetime.datetime.now().isoformat(),
        'interest_over_time': generate_time_series_data(keyword),
        'interest_by_region': generate_regional_data(keyword),
        'related_queries': generate_related_queries(keyword),
        'note': 'Mock data for demonstration - patterns are realistic but not real Google Trends data'
    }
    
    return jsonify(response_data)

@app.route('/api/trends/countries')
def get_countries():
    """Get available countries"""
    return jsonify({
        'countries': [
            {'code': country['code'], 'name': country['name']} 
            for country in COUNTRIES
        ],
        'timestamp': datetime.datetime.now().isoformat()
    })

@app.route('/api/trends/suggestions')
def get_suggestions():
    """Get keyword suggestions"""
    keyword = request.args.get('keyword', '').strip()
    
    suggestions = [
        {'mid': f'/m/{keyword}1', 'title': f'{keyword} technology', 'type': 'Technology'},
        {'mid': f'/m/{keyword}2', 'title': f'{keyword} trends', 'type': 'Topic'},
        {'mid': f'/m/{keyword}3', 'title': f'{keyword} news', 'type': 'News'},
    ]
    
    return jsonify({
        'keyword': keyword,
        'suggestions': suggestions,
        'timestamp': datetime.datetime.now().isoformat()
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🌍 Starting World Trends Explorer Mock Server...")
    print("📊 Using realistic test data for demonstration")
    print("🚀 Server will be available at: http://localhost:5555")
    print("🔍 Try searching for: AI, Olympics, Climate Change, K-pop")
    print("")
    
    app.run(host='0.0.0.0', port=5555, debug=True)
