#!/usr/bin/env python3
"""
World Trends Explorer - Backend Server
🌍 Real-time Google Trends explorer with interactive world map using Pytrends
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import pytrends
from pytrends.request import TrendReq
import pandas as pd
import logging
import os
from datetime import datetime, timedelta
import time
import random
import requests

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Pytrends with better error handling
def get_pytrends_client():
    """Get a fresh Pytrends client with error handling"""
    try:
        return TrendReq(
            hl='en-US', 
            tz=360, 
            timeout=(10, 25), 
            retries=2, 
            backoff_factor=0.1,
            proxies=None,
            requests_args={'verify': False}  # For potential SSL issues
        )
    except Exception as e:
        logger.error(f"Failed to initialize Pytrends client: {e}")
        return None

# Country codes mapping for Pytrends (comprehensive list)
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
    try:
        # Test Pytrends connection
        pytrends_client = get_pytrends_client()
        pytrends_status = "healthy" if pytrends_client else "unavailable"
        
        # Quick connectivity test
        try:
            test_response = requests.get('https://trends.google.com', timeout=5)
            google_trends_accessible = test_response.status_code == 200
        except:
            google_trends_accessible = False
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'World Trends Explorer API',
            'pytrends_status': pytrends_status,
            'google_trends_accessible': google_trends_accessible,
            'countries_available': len(COUNTRY_CODES),
            'version': '2.0.0'
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/trends/search', methods=['GET'])
def search_trends():
    """Get trends data for a specific keyword"""
    try:
        keyword = request.args.get('keyword', '').strip()
        geo = request.args.get('geo', '')
        timeframe = request.args.get('timeframe', 'today 12-m')
        
        if not keyword:
            return jsonify({'error': 'Keyword parameter is required'}), 400
            
        logger.info(f"Searching trends for keyword: '{keyword}', geo: '{geo}', timeframe: '{timeframe}'")
        
        # Get fresh Pytrends client
        pytrends = get_pytrends_client()
        if not pytrends:
            return jsonify({'error': 'Pytrends service unavailable'}), 503
        
        # Format geo parameter
        geo_param = geo if geo in COUNTRY_CODES else ''
        
        # Build payload for pytrends
        try:
            logger.info(f"Building payload with geo='{geo_param}'")
            pytrends.build_payload([keyword], cat=0, timeframe=timeframe, geo=geo_param, gprop='')
        except Exception as e:
            logger.error(f"Failed to build payload: {e}")
            return jsonify({'error': f'Failed to build search query: {str(e)}'}), 400
        
        # Get interest over time
        interest_over_time = pd.DataFrame()
        try:
            interest_over_time = pytrends.interest_over_time()
            logger.info(f"Retrieved {len(interest_over_time)} time data points")
        except Exception as e:
            logger.warning(f"Failed to get interest over time: {e}")
        
        # Get interest by region
        interest_by_region = pd.DataFrame()
        try:
            interest_by_region = pytrends.interest_by_region(
                resolution='COUNTRY', 
                inc_low_vol=True, 
                inc_geo_code=True
            )
            logger.info(f"Retrieved {len(interest_by_region)} regional data points")
        except Exception as e:
            logger.warning(f"Failed to get interest by region: {e}")
        
        # Get related queries
        related_queries = {}
        try:
            related_queries = pytrends.related_queries()
            logger.info(f"Retrieved related queries")
        except Exception as e:
            logger.warning(f"Failed to get related queries: {e}")
        
        # Format response
        response_data = {
            'keyword': keyword,
            'geo': geo_param,
            'timeframe': timeframe,
            'timestamp': datetime.now().isoformat(),
            'interest_over_time': [],
            'interest_by_region': [],
            'related_queries': {
                'top': [],
                'rising': []
            }
        }
        
        # Process interest over time
        if not interest_over_time.empty and keyword in interest_over_time.columns:
            interest_over_time.reset_index(inplace=True)
            for _, row in interest_over_time.iterrows():
                if pd.notna(row['date']):
                    response_data['interest_over_time'].append({
                        'date': row['date'].isoformat(),
                        'value': int(row[keyword]) if pd.notna(row[keyword]) else 0
                    })
        
        # Process interest by region
        if not interest_by_region.empty and keyword in interest_by_region.columns:
            interest_by_region.reset_index(inplace=True)
            for _, row in interest_by_region.iterrows():
                if pd.notna(row[keyword]) and row[keyword] > 0:
                    geo_name = row.get('geoName', 'Unknown')
                    geo_code = row.get('geoCode', '')
                    
                    response_data['interest_by_region'].append({
                        'geoName': geo_name,
                        'geoCode': geo_code,
                        'value': int(row[keyword])
                    })
        
        # Process related queries
        if related_queries and keyword in related_queries:
            if related_queries[keyword]['top'] is not None:
                response_data['related_queries']['top'] = related_queries[keyword]['top'].to_dict('records')
            if related_queries[keyword]['rising'] is not None:
                response_data['related_queries']['rising'] = related_queries[keyword]['rising'].to_dict('records')
        
        logger.info(f"Returning {len(response_data['interest_over_time'])} time points, {len(response_data['interest_by_region'])} regions")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in search_trends: {str(e)}")
        return jsonify({'error': f'Failed to fetch trends data: {str(e)}'}), 500

@app.route('/api/trends/trending', methods=['GET'])
def get_trending():
    """Get current trending searches by country"""
    try:
        geo = request.args.get('geo', 'US')
        
        if geo not in COUNTRY_CODES:
            return jsonify({'error': f'Unsupported country code: {geo}'}), 400
        
        logger.info(f"Getting trending searches for geo: {geo}")
        
        # Get fresh Pytrends client
        pytrends = get_pytrends_client()
        if not pytrends:
            return jsonify({'error': 'Pytrends service unavailable'}), 503
        
        # Get trending searches
        trending_searches = pd.DataFrame()
        try:
            trending_searches = pytrends.trending_searches(pn=geo)
            logger.info(f"Retrieved {len(trending_searches)} trending searches")
        except Exception as e:
            logger.error(f"Failed to get trending searches for {geo}: {e}")
            return jsonify({'error': f'No trending data available for {geo}'}), 400
        
        # Format response
        response_data = {
            'geo': geo,
            'country': COUNTRY_CODES.get(geo, geo),
            'timestamp': datetime.now().isoformat(),
            'trending_searches': []
        }
        
        if not trending_searches.empty:
            # Convert to list and take top 20
            trending_list = trending_searches[0].tolist()[:20]
            response_data['trending_searches'] = [
                {'rank': i+1, 'query': query} 
                for i, query in enumerate(trending_list)
            ]
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in get_trending: {str(e)}")
        return jsonify({'error': f'Failed to fetch trending searches: {str(e)}'}), 500

@app.route('/api/trends/suggestions', methods=['GET'])
def get_suggestions():
    """Get keyword suggestions"""
    try:
        keyword = request.args.get('keyword', '').strip()
        
        if not keyword:
            return jsonify({'error': 'Keyword parameter is required'}), 400
            
        logger.info(f"Getting suggestions for keyword: {keyword}")
        
        # Get fresh Pytrends client
        pytrends = get_pytrends_client()
        if not pytrends:
            return jsonify({'error': 'Pytrends service unavailable'}), 503
        
        # Get keyword suggestions
        suggestions = []
        try:
            suggestions = pytrends.suggestions(keyword=keyword)
        except Exception as e:
            logger.error(f"Failed to get suggestions: {e}")
            suggestions = []
        
        # Format response
        response_data = {
            'keyword': keyword,
            'timestamp': datetime.now().isoformat(),
            'suggestions': suggestions
        }
        
        return jsonify(response_data)
        
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
        'total_countries': len(COUNTRY_CODES)
    })

@app.route('/api/trends/compare', methods=['POST'])
def compare_trends():
    """Compare multiple keywords"""
    try:
        data = request.get_json()
        keywords = data.get('keywords', [])
        geo = data.get('geo', '')
        timeframe = data.get('timeframe', 'today 12-m')
        
        if not keywords or len(keywords) < 2:
            return jsonify({'error': 'At least 2 keywords are required for comparison'}), 400
            
        if len(keywords) > 5:
            return jsonify({'error': 'Maximum 5 keywords allowed for comparison'}), 400
            
        logger.info(f"Comparing keywords: {keywords}, geo: {geo}")
        
        # Get fresh Pytrends client
        pytrends = get_pytrends_client()
        if not pytrends:
            return jsonify({'error': 'Pytrends service unavailable'}), 503
        
        # Format geo parameter
        geo_param = geo if geo in COUNTRY_CODES else ''
        
        # Build payload for pytrends
        try:
            pytrends.build_payload(keywords, cat=0, timeframe=timeframe, geo=geo_param, gprop='')
        except Exception as e:
            logger.error(f"Failed to build comparison payload: {e}")
            return jsonify({'error': f'Failed to build comparison query: {str(e)}'}), 400
        
        # Get interest over time
        interest_over_time = pd.DataFrame()
        try:
            interest_over_time = pytrends.interest_over_time()
        except Exception as e:
            logger.error(f"Failed to get comparison data: {e}")
            return jsonify({'error': f'Failed to get comparison data: {str(e)}'}), 500
        
        # Format response
        response_data = {
            'keywords': keywords,
            'geo': geo_param,
            'timeframe': timeframe,
            'timestamp': datetime.now().isoformat(),
            'comparison_data': []
        }
        
        # Process comparison data
        if not interest_over_time.empty:
            interest_over_time.reset_index(inplace=True)
            for _, row in interest_over_time.iterrows():
                if pd.notna(row['date']):
                    data_point = {'date': row['date'].isoformat()}
                    for keyword in keywords:
                        data_point[keyword] = int(row[keyword]) if pd.notna(row[keyword]) else 0
                    response_data['comparison_data'].append(data_point)
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in compare_trends: {str(e)}")
        return jsonify({'error': f'Failed to compare trends: {str(e)}'}), 500

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
    
    logger.info(f"Starting World Trends Explorer API server on port {port}")
    logger.info(f"Supporting {len(COUNTRY_CODES)} countries")
    logger.info(f"Debug mode: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)