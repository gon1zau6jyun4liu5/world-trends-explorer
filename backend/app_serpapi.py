#!/usr/bin/env python3
"""
World Trends Explorer - SerpAPI Backend Server
🌍 Real-time global trends explorer using SerpAPI for Google Trends data
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import logging
from datetime import datetime
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SerpAPI configuration
SERPAPI_API_KEY = os.getenv('SERPAPI_API_KEY')
if not SERPAPI_API_KEY:
    logger.warning("SERPAPI_API_KEY not found in environment variables")

SERPAPI_BASE_URL = "https://serpapi.com/search"

# Country codes mapping
COUNTRY_CODES = {
    'US': 'United States',
    'GB': 'United Kingdom', 
    'DE': 'Germany',
    'FR': 'France',
    'IT': 'Italy',
    'ES': 'Spain',
    'CA': 'Canada',
    'AU': 'Australia',
    'JP': 'Japan',
    'KR': 'South Korea',
    'IN': 'India',
    'BR': 'Brazil',
    'MX': 'Mexico',
    'RU': 'Russia',
    'CN': 'China'
}

def make_serpapi_request(engine, params):
    """Make a request to SerpAPI"""
    if not SERPAPI_API_KEY:
        raise ValueError("SERPAPI_API_KEY is not configured")
    
    params['api_key'] = SERPAPI_API_KEY
    params['engine'] = engine
    
    response = requests.get(SERPAPI_BASE_URL, params=params)
    response.raise_for_status()
    
    return response.json()

@app.route('/api/trends/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'World Trends Explorer API (SerpAPI)',
        'api_key_configured': bool(SERPAPI_API_KEY)
    })

@app.route('/api/trends/search', methods=['GET'])
def search_trends():
    """
    Get trends data for a specific keyword using SerpAPI
    """
    try:
        keyword = request.args.get('keyword', '').strip()
        geo = request.args.get('geo', 'US')
        timeframe = request.args.get('timeframe', 'today 12-m')
        
        if not keyword:
            return jsonify({'error': 'Keyword parameter is required'}), 400
        
        if not SERPAPI_API_KEY:
            return jsonify({'error': 'API key not configured'}), 500
            
        logger.info(f"Searching trends for keyword: {keyword}, geo: {geo}")
        
        # Get Google Trends data via SerpAPI
        params = {
            'q': keyword,
            'data_type': 'TIMESERIES',
            'tz': '0',
            'hl': 'en',
            'gl': geo.lower()
        }
        
        try:
            trends_data = make_serpapi_request('google_trends', params)
        except Exception as e:
            logger.error(f"SerpAPI request failed: {str(e)}")
            # Return mock data if SerpAPI fails
            return get_mock_data(keyword, geo, timeframe)
        
        # Format response
        response_data = {
            'keyword': keyword,
            'geo': geo,
            'timeframe': timeframe,
            'timestamp': datetime.now().isoformat(),
            'interest_over_time': [],
            'interest_by_region': [],
            'related_queries': {
                'top': [],
                'rising': []
            }
        }
        
        # Process time series data
        if 'interest_over_time' in trends_data:
            time_data = trends_data.get('interest_over_time', {}).get('timeline_data', [])
            for item in time_data:
                response_data['interest_over_time'].append({
                    'date': item.get('date', ''),
                    'value': item.get('values', [{}])[0].get('value', 0)
                })
        
        # Process regional data
        if 'interest_by_region' in trends_data:
            for region in trends_data.get('interest_by_region', []):
                response_data['interest_by_region'].append({
                    'geoName': region.get('location', ''),
                    'geoCode': region.get('geo', '').upper(),
                    'value': region.get('value', 0)
                })
        
        # Process related queries
        if 'related_queries' in trends_data:
            related = trends_data.get('related_queries', {})
            if 'top' in related:
                response_data['related_queries']['top'] = [
                    {'query': q.get('query', ''), 'value': str(q.get('value', 0))}
                    for q in related.get('top', [])
                ]
            if 'rising' in related:
                response_data['related_queries']['rising'] = [
                    {'query': q.get('query', ''), 'value': q.get('value', 'N/A')}
                    for q in related.get('rising', [])
                ]
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in search_trends: {str(e)}")
        return jsonify({'error': f'Failed to fetch trends data: {str(e)}'}), 500

@app.route('/api/trends/trending', methods=['GET'])
def get_trending():
    """Get current trending searches by country"""
    try:
        geo = request.args.get('geo', 'US')
        
        if not SERPAPI_API_KEY:
            return jsonify({'error': 'API key not configured'}), 500
        
        logger.info(f"Getting trending searches for geo: {geo}")
        
        # Get trending searches via SerpAPI
        params = {
            'gl': geo.lower(),
            'hl': 'en'
        }
        
        try:
            trends_data = make_serpapi_request('google_trends_trending_searches', params)
        except Exception as e:
            logger.error(f"SerpAPI request failed: {str(e)}")
            # Return mock data if SerpAPI fails
            return get_mock_trending_data(geo)
        
        # Format response
        response_data = {
            'geo': geo,
            'country': COUNTRY_CODES.get(geo, geo),
            'timestamp': datetime.now().isoformat(),
            'trending_searches': []
        }
        
        # Process trending searches
        trending_searches = trends_data.get('trending_searches', [])
        for i, search in enumerate(trending_searches[:20]):
            response_data['trending_searches'].append({
                'rank': i + 1,
                'query': search.get('title', '')
            })
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in get_trending: {str(e)}")
        return jsonify({'error': f'Failed to fetch trending searches: {str(e)}'}), 500

@app.route('/api/trends/countries', methods=['GET'])
def get_countries():
    """Get available countries list"""
    return jsonify({
        'countries': [
            {'code': code, 'name': name} 
            for code, name in COUNTRY_CODES.items()
        ],
        'timestamp': datetime.now().isoformat()
    })

def get_mock_data(keyword, geo, timeframe):
    """Return mock data when SerpAPI is not available"""
    import random
    from datetime import timedelta
    
    # Generate mock time series data
    time_data = []
    start_date = datetime.now() - timedelta(days=365)
    for i in range(52):  # 52 weeks
        date = start_date + timedelta(weeks=i)
        value = random.randint(20, 100)
        time_data.append({
            'date': date.isoformat(),
            'value': value
        })
    
    # Generate mock regional data
    regional_data = []
    for code, name in list(COUNTRY_CODES.items())[:10]:
        regional_data.append({
            'geoName': name,
            'geoCode': code,
            'value': random.randint(10, 100)
        })
    
    return jsonify({
        'keyword': keyword,
        'geo': geo,
        'timeframe': timeframe,
        'timestamp': datetime.now().isoformat(),
        'interest_over_time': time_data,
        'interest_by_region': sorted(regional_data, key=lambda x: x['value'], reverse=True),
        'related_queries': {
            'top': [
                {'query': f'{keyword} news', 'value': '100'},
                {'query': f'{keyword} 2024', 'value': '85'},
                {'query': f'what is {keyword}', 'value': '70'}
            ],
            'rising': [
                {'query': f'{keyword} AI', 'value': 'Breakout'},
                {'query': f'{keyword} trend', 'value': '+500%'}
            ]
        },
        'note': 'Mock data - Configure SERPAPI_API_KEY for real data'
    })

def get_mock_trending_data(geo):
    """Return mock trending data"""
    mock_trending = {
        'US': ['Taylor Swift', 'NFL', 'iPhone 16', 'Climate Change', 'AI'],
        'KR': ['BTS', 'K-drama', 'Samsung', 'Seoul', 'Kimchi'],
        'JP': ['Anime', 'Tokyo Olympics', 'Nintendo', 'Sushi', 'Mount Fuji']
    }
    
    queries = mock_trending.get(geo, mock_trending['US'])
    
    return jsonify({
        'geo': geo,
        'country': COUNTRY_CODES.get(geo, geo),
        'timestamp': datetime.now().isoformat(),
        'trending_searches': [
            {'rank': i+1, 'query': query}
            for i, query in enumerate(queries)
        ],
        'note': 'Mock data - Configure SERPAPI_API_KEY for real data'
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    if not SERPAPI_API_KEY:
        print("⚠️  WARNING: SERPAPI_API_KEY not found in environment variables")
        print("📝 To set it up:")
        print("   1. Create a .env file in the backend directory")
        print("   2. Add: SERPAPI_API_KEY=your-api-key-here")
        print("   3. Or set it as an environment variable")
        print("")
        print("🎭 Running in MOCK MODE - showing sample data")
    else:
        print("✅ SERPAPI_API_KEY configured")
    
    print(f"🚀 Starting World Trends Explorer API server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
