#!/usr/bin/env python3
"""
World Trends Explorer - Backend Server v1.4.0
🌍 SerpAPI integration for real Google Trends data
NO FAKE DATA - Real API calls only
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import os
from datetime import datetime
import requests
import json

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# SerpAPI configuration
SERPAPI_KEY = os.environ.get('SERPAPI_KEY', '')
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
    'CN': 'China',
    'NL': 'Netherlands',
    'SE': 'Sweden',
    'NO': 'Norway',
    'DK': 'Denmark',
    'FI': 'Finland'
}

class SerpAPIClient:
    """SerpAPI client - REAL API CALLS ONLY, NO FAKE DATA"""
    
    def __init__(self):
        self.api_key = SERPAPI_KEY
        self.base_url = SERPAPI_BASE_URL
        self.session = requests.Session()
        self.session.timeout = 30
        
    def make_request(self, params):
        """Make REAL SerpAPI request"""
        if not self.api_key:
            raise ValueError("SerpAPI key is required. Set SERPAPI_KEY environment variable.")
            
        try:
            params['api_key'] = self.api_key
            response = self.session.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            logger.error("SerpAPI request timeout")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"SerpAPI request error: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"SerpAPI JSON decode error: {e}")
            raise

# Initialize SerpAPI client
serpapi_client = SerpAPIClient()

@app.route('/api/trends/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy' if SERPAPI_KEY else 'unhealthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'World Trends Explorer API',
        'version': '1.4.0',
        'data_source': 'SerpAPI',
        'api_key_configured': bool(SERPAPI_KEY),
        'message': 'SerpAPI key required for real data' if not SERPAPI_KEY else 'Ready'
    })

@app.route('/api/trends/search', methods=['GET'])
def search_trends():
    """Search trends using REAL SerpAPI data"""
    try:
        keyword = request.args.get('keyword', '').strip()
        geo = request.args.get('geo', 'US')
        timeframe = request.args.get('timeframe', 'today 12-m')
        
        if not keyword:
            return jsonify({'error': 'Keyword parameter is required'}), 400
            
        if not SERPAPI_KEY:
            return jsonify({'error': 'SerpAPI key not configured. Please set SERPAPI_KEY environment variable.'}), 503
            
        logger.info(f"Searching trends: '{keyword}' in {geo}")
        
        # REAL SerpAPI request
        params = {
            'engine': 'google_trends',
            'q': keyword,
            'geo': geo,
            'data_type': 'TIMESERIES',
            'tz': '360'
        }
        
        result = serpapi_client.make_request(params)
        
        # Format REAL response
        response_data = {
            'keyword': keyword,
            'geo': geo,
            'timeframe': timeframe,
            'timestamp': datetime.now().isoformat(),
            'data_source': 'SerpAPI',
            'interest_over_time': [],
            'interest_by_region': [],
            'related_queries': {'top': [], 'rising': []}
        }
        
        # Process REAL data
        if 'interest_over_time' in result and 'timeline_data' in result['interest_over_time']:
            for point in result['interest_over_time']['timeline_data']:
                response_data['interest_over_time'].append({
                    'date': point.get('date', ''),
                    'value': point['values'][0]['extracted_value'] if point.get('values') else 0
                })
        
        # Get regional data - separate API call
        regional_params = params.copy()
        regional_params['data_type'] = 'GEO_MAP'
        
        try:
            regional_result = serpapi_client.make_request(regional_params)
            if 'interest_by_region' in regional_result:
                for region in regional_result['interest_by_region']:
                    response_data['interest_by_region'].append({
                        'geoName': region.get('location', ''),
                        'geoCode': region.get('location_code', ''),
                        'value': region.get('extracted_value', 0)
                    })
        except Exception as e:
            logger.warning(f"Failed to get regional data: {e}")
        
        # Get related queries - separate API call
        related_params = params.copy()
        related_params['data_type'] = 'RELATED_QUERIES'
        
        try:
            related_result = serpapi_client.make_request(related_params)
            if 'related_queries' in related_result:
                if 'top' in related_result['related_queries']:
                    response_data['related_queries']['top'] = [
                        {'query': q.get('query', ''), 'value': str(q.get('extracted_value', ''))}
                        for q in related_result['related_queries']['top']
                    ]
                if 'rising' in related_result['related_queries']:
                    response_data['related_queries']['rising'] = [
                        {'query': q.get('query', ''), 'value': q.get('extracted_value', 'Rising')}
                        for q in related_result['related_queries']['rising']
                    ]
        except Exception as e:
            logger.warning(f"Failed to get related queries: {e}")
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in search_trends: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/trends/trending', methods=['GET'])
def get_trending():
    """Get REAL trending searches"""
    try:
        geo = request.args.get('geo', 'US')
        
        if not SERPAPI_KEY:
            return jsonify({'error': 'SerpAPI key not configured. Please set SERPAPI_KEY environment variable.'}), 503
            
        logger.info(f"Getting trending for: {geo}")
        
        # REAL SerpAPI request
        params = {
            'engine': 'google_trends_trending_now',
            'geo': geo,
            'hl': 'en'
        }
        
        result = serpapi_client.make_request(params)
        
        # Format REAL response
        response_data = {
            'geo': geo,
            'country': COUNTRY_CODES.get(geo, geo),
            'timestamp': datetime.now().isoformat(),
            'data_source': 'SerpAPI',
            'trending_searches': []
        }
        
        # Extract REAL trending searches
        if 'trending_searches' in result:
            for idx, search in enumerate(result['trending_searches'][:20]):
                response_data['trending_searches'].append({
                    'rank': idx + 1,
                    'query': search.get('query', '')
                })
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in get_trending: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/trends/suggestions', methods=['GET'])
def get_suggestions():
    """Get REAL keyword suggestions"""
    try:
        keyword = request.args.get('keyword', '').strip()
        
        if not keyword:
            return jsonify({'error': 'Keyword parameter is required'}), 400
            
        if not SERPAPI_KEY:
            return jsonify({'error': 'SerpAPI key not configured. Please set SERPAPI_KEY environment variable.'}), 503
            
        logger.info(f"Getting suggestions for: '{keyword}'")
        
        # REAL Google Autocomplete via SerpAPI
        params = {
            'engine': 'google_autocomplete',
            'q': keyword,
            'hl': 'en'
        }
        
        result = serpapi_client.make_request(params)
        
        # Format REAL response
        suggestions = []
        if 'suggestions' in result:
            for suggestion in result['suggestions'][:10]:
                suggestions.append({
                    'title': suggestion.get('value', ''),
                    'type': 'Search term'
                })
        
        return jsonify({
            'keyword': keyword,
            'timestamp': datetime.now().isoformat(),
            'data_source': 'SerpAPI',
            'suggestions': suggestions
        })
        
    except Exception as e:
        logger.error(f"Error in get_suggestions: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/trends/countries', methods=['GET'])
def get_countries():
    """Get available countries list"""
    return jsonify({
        'countries': [
            {'code': code, 'name': name} 
            for code, name in COUNTRY_CODES.items()
        ],
        'timestamp': datetime.now().isoformat(),
        'version': '1.4.0'
    })

@app.route('/api/trends/compare', methods=['POST'])
def compare_trends():
    """Compare multiple keywords using REAL SerpAPI data"""
    try:
        data = request.get_json()
        keywords = data.get('keywords', [])
        geo = data.get('geo', 'US')
        timeframe = data.get('timeframe', 'today 12-m')
        
        if not keywords or len(keywords) < 2:
            return jsonify({'error': 'At least 2 keywords are required'}), 400
            
        if len(keywords) > 5:
            return jsonify({'error': 'Maximum 5 keywords allowed'}), 400
            
        if not SERPAPI_KEY:
            return jsonify({'error': 'SerpAPI key not configured. Please set SERPAPI_KEY environment variable.'}), 503
            
        logger.info(f"Comparing: {keywords} in {geo}")
        
        # REAL SerpAPI request with multiple keywords
        params = {
            'engine': 'google_trends',
            'q': ','.join(keywords),
            'geo': geo,
            'data_type': 'TIMESERIES',
            'tz': '360'
        }
        
        result = serpapi_client.make_request(params)
        
        # Format REAL response
        response_data = {
            'keywords': keywords,
            'geo': geo,
            'timeframe': timeframe,
            'timestamp': datetime.now().isoformat(),
            'data_source': 'SerpAPI',
            'comparison_data': []
        }
        
        # Process REAL comparison data
        if 'interest_over_time' in result and 'timeline_data' in result['interest_over_time']:
            for point in result['interest_over_time']['timeline_data']:
                data_point = {'date': point.get('date', '')}
                
                for idx, keyword in enumerate(keywords):
                    if 'values' in point and idx < len(point['values']):
                        data_point[keyword] = point['values'][idx].get('extracted_value', 0)
                    else:
                        data_point[keyword] = 0
                        
                response_data['comparison_data'].append(data_point)
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in compare_trends: {e}")
        return jsonify({'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found', 'version': '1.4.0'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error', 'version': '1.4.0'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print("🌍 World Trends Explorer API v1.4.0")
    print("=" * 50)
    print("📡 Using REAL SerpAPI data only - NO FAKE DATA")
    
    if not SERPAPI_KEY:
        print("❌ ERROR: SerpAPI key not configured!")
        print("⚠️  Set environment variable: export SERPAPI_KEY='your_key'")
        print("📝 Get your key from: https://serpapi.com")
    else:
        print("✅ SerpAPI key configured")
        print(f"🔑 Key: {SERPAPI_KEY[:10]}...")
    
    print(f"🚀 Server starting on port {port}")
    print(f"🔗 Health: http://localhost:{port}/api/trends/health")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=port, debug=debug)
