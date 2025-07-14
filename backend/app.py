#!/usr/bin/env python3
"""
World Trends Explorer - Backend Server v1.2.3
🌍 Real-time Google Trends data using SerpAPI
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import os
from datetime import datetime
import traceback

# Import SerpAPI adapter
try:
    from serpapi_adapter import SerpAPIAdapter
    SERPAPI_AVAILABLE = True
except ImportError:
    print("❌ SerpAPI adapter not available")
    SERPAPI_AVAILABLE = False

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize SerpAPI client
serpapi_client = None
if SERPAPI_AVAILABLE:
    try:
        serpapi_client = SerpAPIAdapter()
        logger.info("✅ SerpAPI adapter initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize SerpAPI: {e}")

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
    'FI': 'Finland',
    'BE': 'Belgium',
    'CH': 'Switzerland',
    'AT': 'Austria',
    'IE': 'Ireland',
    'PT': 'Portugal',
    'GR': 'Greece',
    'PL': 'Poland',
    'CZ': 'Czech Republic',
    'HU': 'Hungary',
    'RO': 'Romania',
    'BG': 'Bulgaria',
    'HR': 'Croatia',
    'SK': 'Slovakia',
    'SI': 'Slovenia',
    'LT': 'Lithuania',
    'LV': 'Latvia',
    'EE': 'Estonia',
    'IS': 'Iceland',
    'LU': 'Luxembourg',
    'MT': 'Malta',
    'CY': 'Cyprus',
    'TR': 'Turkey',
    'IL': 'Israel',
    'AE': 'United Arab Emirates',
    'SA': 'Saudi Arabia',
    'EG': 'Egypt',
    'ZA': 'South Africa',
    'NG': 'Nigeria',
    'KE': 'Kenya',
    'GH': 'Ghana',
    'TH': 'Thailand',
    'VN': 'Vietnam',
    'ID': 'Indonesia',
    'MY': 'Malaysia',
    'SG': 'Singapore',
    'PH': 'Philippines',
    'TW': 'Taiwan',
    'HK': 'Hong Kong',
    'NZ': 'New Zealand',
    'AR': 'Argentina',
    'CL': 'Chile',
    'CO': 'Colombia',
    'PE': 'Peru',
    'VE': 'Venezuela',
    'UY': 'Uruguay',
    'EC': 'Ecuador',
    'BO': 'Bolivia',
    'PY': 'Paraguay'
}

@app.route('/api/trends/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    if not serpapi_client:
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'World Trends Explorer API',
            'error': 'SerpAPI client not available',
            'version': '1.2.3'
        }), 500
    
    # Test SerpAPI connection
    health = serpapi_client.health_check()
    
    return jsonify({
        'status': health.get('status', 'unknown'),
        'timestamp': datetime.now().isoformat(),
        'service': 'World Trends Explorer API',
        'data_source': 'SerpAPI',
        'countries_available': len(COUNTRY_CODES),
        'version': '1.2.3',
        'serpapi_status': health.get('status', 'unknown')
    })

@app.route('/api/trends/search', methods=['GET'])
def search_trends():
    """Search trends data using SerpAPI"""
    try:
        keyword = request.args.get('keyword', '').strip()
        geo = request.args.get('geo', '')
        timeframe = request.args.get('timeframe', 'today 12-m')
        
        if not keyword:
            return jsonify({'error': 'Keyword parameter is required'}), 400
        
        if not serpapi_client:
            return jsonify({'error': 'SerpAPI service not available'}), 503
            
        logger.info(f"Searching trends for keyword: '{keyword}', geo: '{geo}'")
        
        # Get trends data from SerpAPI
        result = serpapi_client.search_trends(keyword, geo, timeframe)
        
        # Add version info
        result['version'] = '1.2.3'
        result['data_source'] = 'SerpAPI'
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in search_trends: {str(e)}")
        return jsonify({'error': f'Failed to fetch trends data: {str(e)}'}), 500

@app.route('/api/trends/trending', methods=['GET'])
def get_trending():
    """Get trending searches using SerpAPI"""
    try:
        geo = request.args.get('geo', 'US')
        
        if geo not in COUNTRY_CODES:
            return jsonify({'error': f'Unsupported country code: {geo}'}), 400
        
        if not serpapi_client:
            return jsonify({'error': 'SerpAPI service not available'}), 503
            
        logger.info(f"Getting trending searches for geo: {geo}")
        
        # Get trending data from SerpAPI
        result = serpapi_client.get_trending_searches(geo)
        
        # Add version info
        result['version'] = '1.2.3'
        result['data_source'] = 'SerpAPI'
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in get_trending: {str(e)}")
        return jsonify({'error': f'Failed to fetch trending searches: {str(e)}'}), 500

@app.route('/api/trends/suggestions', methods=['GET'])
def get_suggestions():
    """Get keyword suggestions using SerpAPI"""
    try:
        keyword = request.args.get('keyword', '').strip()
        
        if not keyword:
            return jsonify({'error': 'Keyword parameter is required'}), 400
        
        if not serpapi_client:
            return jsonify({'error': 'SerpAPI service not available'}), 503
            
        logger.info(f"Getting suggestions for keyword: {keyword}")
        
        # Get suggestions from SerpAPI
        result = serpapi_client.get_suggestions(keyword)
        
        # Add version info
        result['version'] = '1.2.3'
        result['data_source'] = 'SerpAPI'
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in get_suggestions: {str(e)}")
        return jsonify({'error': f'Failed to fetch suggestions: {str(e)}'}), 500

@app.route('/api/trends/countries', methods=['GET'])
def get_countries():
    """Get available countries list"""
    return jsonify({
        'countries': [
            {'code': code, 'name': name} 
            for code, name in COUNTRY_CODES.items()
        ],
        'timestamp': datetime.now().isoformat(),
        'total_countries': len(COUNTRY_CODES),
        'version': '1.2.3'
    })

@app.route('/api/trends/compare', methods=['POST'])
def compare_trends():
    """Compare multiple keywords using SerpAPI"""
    try:
        data = request.get_json()
        keywords = data.get('keywords', [])
        geo = data.get('geo', '')
        timeframe = data.get('timeframe', 'today 12-m')
        
        if not keywords or len(keywords) < 2:
            return jsonify({'error': 'At least 2 keywords are required for comparison'}), 400
            
        if len(keywords) > 5:
            return jsonify({'error': 'Maximum 5 keywords allowed for comparison'}), 400
        
        if not serpapi_client:
            return jsonify({'error': 'SerpAPI service not available'}), 503
            
        logger.info(f"Comparing keywords: {keywords}, geo: {geo}")
        
        # Get trends for each keyword
        comparison_data = []
        for keyword in keywords:
            try:
                result = serpapi_client.search_trends(keyword, geo, timeframe)
                comparison_data.append(result)
            except Exception as e:
                logger.warning(f"Failed to get data for keyword '{keyword}': {e}")
        
        # Format comparison response
        response_data = {
            'keywords': keywords,
            'geo': geo,
            'timeframe': timeframe,
            'timestamp': datetime.now().isoformat(),
            'comparison_data': comparison_data,
            'version': '1.2.3',
            'data_source': 'SerpAPI'
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in compare_trends: {str(e)}")
        return jsonify({'error': f'Failed to compare trends: {str(e)}'}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found', 'version': '1.2.3'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error', 'version': '1.2.3'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print("🌍 World Trends Explorer API v1.2.3")
    print("=" * 50)
    print("🔍 Data Source: SerpAPI Only")
    print(f"🌏 Supported Countries: {len(COUNTRY_CODES)}")
    
    if serpapi_client:
        health = serpapi_client.health_check()
        status_emoji = "✅" if health.get('status') == 'healthy' else "⚠️"
        print(f"{status_emoji} SerpAPI Status: {health.get('status', 'unknown')}")
    else:
        print("❌ SerpAPI: Not available")
    
    print(f"🚀 Server starting on port {port}")
    print(f"🔗 Health check: http://localhost:{port}/api/trends/health")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=port, debug=debug)
