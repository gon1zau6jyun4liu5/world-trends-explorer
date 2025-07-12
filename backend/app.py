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

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Pytrends
pytrends = TrendReq(hl='en-US', tz=360)

# Country codes mapping for Pytrends
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

@app.route('/api/trends/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'World Trends Explorer API'
    })

@app.route('/api/trends/search', methods=['GET'])
def search_trends():
    """
    Get trends data for a specific keyword
    Query parameters:
    - keyword: Search term
    - geo: Country code (optional, default: 'US')
    - timeframe: Time period (optional, default: 'today 12-m')
    """
    try:
        keyword = request.args.get('keyword', '').strip()
        geo = request.args.get('geo', 'US')
        timeframe = request.args.get('timeframe', 'today 12-m')
        
        if not keyword:
            return jsonify({'error': 'Keyword parameter is required'}), 400
            
        logger.info(f"Searching trends for keyword: {keyword}, geo: {geo}")
        
        # Build payload for pytrends
        pytrends.build_payload([keyword], cat=0, timeframe=timeframe, geo=geo, gprop='')
        
        # Get interest over time
        interest_over_time = pytrends.interest_over_time()
        
        # Get interest by region
        interest_by_region = pytrends.interest_by_region(resolution='COUNTRY', inc_low_vol=True, inc_geo_code=True)
        
        # Get related queries
        related_queries = pytrends.related_queries()
        
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
        
        # Process interest over time
        if not interest_over_time.empty:
            interest_over_time.reset_index(inplace=True)
            for _, row in interest_over_time.iterrows():
                response_data['interest_over_time'].append({
                    'date': row['date'].isoformat() if pd.notna(row['date']) else None,
                    'value': int(row[keyword]) if pd.notna(row[keyword]) else 0
                })
        
        # Process interest by region
        if not interest_by_region.empty:
            interest_by_region.reset_index(inplace=True)
            for _, row in interest_by_region.iterrows():
                if pd.notna(row[keyword]) and row[keyword] > 0:
                    response_data['interest_by_region'].append({
                        'geoName': row['geoName'],
                        'geoCode': row['geoCode'],
                        'value': int(row[keyword])
                    })
        
        # Process related queries
        if related_queries and keyword in related_queries:
            if related_queries[keyword]['top'] is not None:
                response_data['related_queries']['top'] = related_queries[keyword]['top'].to_dict('records')
            if related_queries[keyword]['rising'] is not None:
                response_data['related_queries']['rising'] = related_queries[keyword]['rising'].to_dict('records')
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in search_trends: {str(e)}")
        return jsonify({'error': f'Failed to fetch trends data: {str(e)}'}), 500

@app.route('/api/trends/trending', methods=['GET'])
def get_trending():
    """Get current trending searches by country"""
    try:
        geo = request.args.get('geo', 'US')
        
        logger.info(f"Getting trending searches for geo: {geo}")
        
        # Get trending searches
        trending_searches = pytrends.trending_searches(pn=geo)
        
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
        
        # Get keyword suggestions
        suggestions = pytrends.suggestions(keyword=keyword)
        
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
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/trends/compare', methods=['POST'])
def compare_trends():
    """Compare multiple keywords"""
    try:
        data = request.get_json()
        keywords = data.get('keywords', [])
        geo = data.get('geo', 'US')
        timeframe = data.get('timeframe', 'today 12-m')
        
        if not keywords or len(keywords) < 2:
            return jsonify({'error': 'At least 2 keywords are required for comparison'}), 400
            
        if len(keywords) > 5:
            return jsonify({'error': 'Maximum 5 keywords allowed for comparison'}), 400
            
        logger.info(f"Comparing keywords: {keywords}, geo: {geo}")
        
        # Build payload for pytrends
        pytrends.build_payload(keywords, cat=0, timeframe=timeframe, geo=geo, gprop='')
        
        # Get interest over time
        interest_over_time = pytrends.interest_over_time()
        
        # Format response
        response_data = {
            'keywords': keywords,
            'geo': geo,
            'timeframe': timeframe,
            'timestamp': datetime.now().isoformat(),
            'comparison_data': []
        }
        
        # Process comparison data
        if not interest_over_time.empty:
            interest_over_time.reset_index(inplace=True)
            for _, row in interest_over_time.iterrows():
                data_point = {'date': row['date'].isoformat() if pd.notna(row['date']) else None}
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
    app.run(host='0.0.0.0', port=port, debug=debug)
