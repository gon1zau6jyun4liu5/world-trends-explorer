#!/usr/bin/env python3
"""
World Trends Explorer - Enhanced Backend Server with SerpAPI Integration
🌍 Real-time trends data using SerpAPI as primary source with Pytrends fallback
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import os
from datetime import datetime
import traceback

# Import data adapters
try:
    from serpapi_adapter import SerpAPIAdapter
    SERPAPI_AVAILABLE = True
except ImportError:
    print("⚠️ SerpAPI adapter not available")
    SERPAPI_AVAILABLE = False

try:
    import pytrends
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except ImportError:
    print("⚠️ Pytrends not available")
    PYTRENDS_AVAILABLE = False

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrendsDataProvider:
    """
    Unified data provider that manages multiple data sources
    Priority: SerpAPI -> Pytrends -> Mock Data
    """
    
    def __init__(self):
        self.providers = []
        self.active_provider = None
        
        # Initialize SerpAPI if available
        if SERPAPI_AVAILABLE:
            try:
                self.serpapi = SerpAPIAdapter()
                health = self.serpapi.health_check()
                if health['status'] in ['healthy', 'degraded']:
                    self.providers.append(('SerpAPI', self.serpapi))
                    logger.info("✅ SerpAPI adapter initialized")
                else:
                    logger.warning("⚠️ SerpAPI health check failed")
            except Exception as e:
                logger.error(f"❌ Failed to initialize SerpAPI: {e}")
        
        # Initialize Pytrends as fallback
        if PYTRENDS_AVAILABLE:
            try:
                self.pytrends = TrendReq(hl='en-US', tz=360)
                self.providers.append(('Pytrends', self.pytrends))
                logger.info("✅ Pytrends fallback available")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Pytrends: {e}")
        
        # Mock data as final fallback
        self.providers.append(('Mock', self._create_mock_provider()))
        
        # Set active provider
        if self.providers:
            self.active_provider = self.providers[0]
            logger.info(f"🎯 Active provider: {self.active_provider[0]}")
        else:
            logger.error("❌ No data providers available")

    def _create_mock_provider(self):
        """Create mock data provider"""
        class MockProvider:
            def search_trends(self, keyword, geo='', timeframe='today 12-m'):
                return self._generate_mock_trends(keyword, geo, timeframe)
            
            def get_trending_searches(self, geo='US'):
                return self._generate_mock_trending(geo)
            
            def get_suggestions(self, keyword):
                return self._generate_mock_suggestions(keyword)
            
            def health_check(self):
                return {
                    'status': 'healthy',
                    'data_source': 'Mock Data',
                    'timestamp': datetime.now().isoformat(),
                    'note': 'Using fallback mock data'
                }
            
            def _generate_mock_trends(self, keyword, geo, timeframe):
                from datetime import timedelta
                import random
                
                # Generate time series
                start_date = datetime.now() - timedelta(days=365)
                interest_over_time = []
                
                for i in range(52):
                    date = start_date + timedelta(weeks=i)
                    value = max(10, min(100, 50 + random.randint(-20, 20)))
                    interest_over_time.append({
                        'date': date.isoformat(),
                        'value': value
                    })
                
                # Generate regional data
                countries = [
                    ('United States', 'US'), ('Germany', 'DE'), ('United Kingdom', 'GB'),
                    ('France', 'FR'), ('Japan', 'JP'), ('South Korea', 'KR'),
                    ('Canada', 'CA'), ('Australia', 'AU'), ('Brazil', 'BR'),
                    ('India', 'IN'), ('China', 'CN'), ('Russia', 'RU')
                ]
                
                interest_by_region = []
                for name, code in countries:
                    value = random.randint(10, 100)
                    interest_by_region.append({
                        'geoName': name,
                        'geoCode': code,
                        'value': value
                    })
                
                # Generate related queries
                related_queries = {
                    'top': [
                        {'query': f'{keyword} tutorial', 'value': '100'},
                        {'query': f'{keyword} guide', 'value': '80'},
                        {'query': f'{keyword} examples', 'value': '60'},
                        {'query': f'{keyword} tips', 'value': '40'}
                    ],
                    'rising': [
                        {'query': f'{keyword} 2025', 'value': 'Breakout'},
                        {'query': f'{keyword} new', 'value': '+500%'},
                        {'query': f'{keyword} latest', 'value': '+300%'}
                    ]
                }
                
                return {
                    'keyword': keyword,
                    'geo': geo,
                    'timeframe': timeframe,
                    'timestamp': datetime.now().isoformat(),
                    'interest_over_time': interest_over_time,
                    'interest_by_region': interest_by_region,
                    'related_queries': related_queries,
                    'data_source': 'Mock Data',
                    'note': 'Generated mock data for demonstration'
                }
            
            def _generate_mock_trending(self, geo):
                trending_searches = [
                    {'rank': 1, 'query': 'Artificial Intelligence'},
                    {'rank': 2, 'query': 'Climate Change'},
                    {'rank': 3, 'query': 'Electric Vehicles'},
                    {'rank': 4, 'query': 'Cryptocurrency'},
                    {'rank': 5, 'query': 'Space Exploration'},
                    {'rank': 6, 'query': 'Renewable Energy'},
                    {'rank': 7, 'query': 'Machine Learning'},
                    {'rank': 8, 'query': 'Remote Work'},
                    {'rank': 9, 'query': 'Sustainable Living'},
                    {'rank': 10, 'query': 'Digital Transformation'}
                ]
                
                return {
                    'geo': geo,
                    'country': geo,
                    'timestamp': datetime.now().isoformat(),
                    'trending_searches': trending_searches,
                    'data_source': 'Mock Data'
                }
            
            def _generate_mock_suggestions(self, keyword):
                suggestions = [
                    {'mid': f'/m/{keyword}1', 'title': f'{keyword} tutorial', 'type': 'Topic'},
                    {'mid': f'/m/{keyword}2', 'title': f'{keyword} guide', 'type': 'Topic'},
                    {'mid': f'/m/{keyword}3', 'title': f'{keyword} examples', 'type': 'Topic'}
                ]
                
                return {
                    'keyword': keyword,
                    'suggestions': suggestions,
                    'timestamp': datetime.now().isoformat(),
                    'data_source': 'Mock Data'
                }
        
        return MockProvider()

    def get_provider(self, provider_name=None):
        """Get specific provider or active provider"""
        if provider_name:
            for name, provider in self.providers:
                if name.lower() == provider_name.lower():
                    return provider
        return self.active_provider[1] if self.active_provider else None

    def switch_provider(self, provider_name):
        """Switch to different provider"""
        for i, (name, provider) in enumerate(self.providers):
            if name.lower() == provider_name.lower():
                self.active_provider = self.providers[i]
                logger.info(f"🔄 Switched to provider: {name}")
                return True
        return False

    def get_provider_status(self):
        """Get status of all providers"""
        status = {}
        for name, provider in self.providers:
            try:
                health = provider.health_check()
                status[name] = health
            except Exception as e:
                status[name] = {
                    'status': 'error',
                    'note': str(e)
                }
        return status

# Initialize data provider
try:
    data_provider = TrendsDataProvider()
except Exception as e:
    logger.error(f"Failed to initialize data provider: {e}")
    data_provider = None

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

@app.route('/api/trends/health', methods=['GET'])
def health_check():
    """Enhanced health check with provider status"""
    if not data_provider:
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'World Trends Explorer API (Enhanced)',
            'note': 'Data provider initialization failed'
        }), 500
    
    provider_status = data_provider.get_provider_status()
    active_provider_name = data_provider.active_provider[0] if data_provider.active_provider else 'None'
    
    # Determine overall health
    active_health = provider_status.get(active_provider_name, {}).get('status', 'unknown')
    overall_status = 'healthy' if active_health in ['healthy', 'degraded'] else 'degraded'
    
    return jsonify({
        'status': overall_status,
        'timestamp': datetime.now().isoformat(),
        'service': 'World Trends Explorer API (Enhanced)',
        'active_provider': active_provider_name,
        'providers': provider_status,
        'version': '1.1.0',
        'features': ['SerpAPI', 'Pytrends Fallback', 'Mock Data']
    })

@app.route('/api/trends/search', methods=['GET'])
def search_trends():
    """Enhanced search with multiple data sources"""
    try:
        keyword = request.args.get('keyword', '').strip()
        geo = request.args.get('geo', '')
        timeframe = request.args.get('timeframe', 'today 12-m')
        
        if not keyword:
            return jsonify({'error': 'Keyword parameter is required'}), 400
        
        if not data_provider:
            return jsonify({'error': 'Data provider not available'}), 500
            
        logger.info(f"Searching trends for keyword: {keyword}, geo: {geo}")
        
        provider = data_provider.get_provider()
        result = provider.search_trends(keyword, geo, timeframe)
        
        # Add metadata
        result['api_version'] = '1.1.0'
        result['provider_used'] = data_provider.active_provider[0]
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in search_trends: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'Failed to fetch trends data: {str(e)}'}), 500

@app.route('/api/trends/trending', methods=['GET'])
def get_trending():
    """Enhanced trending searches with multiple sources"""
    try:
        geo = request.args.get('geo', 'US')
        
        if not data_provider:
            return jsonify({'error': 'Data provider not available'}), 500
            
        logger.info(f"Getting trending searches for geo: {geo}")
        
        provider = data_provider.get_provider()
        result = provider.get_trending_searches(geo)
        
        # Add metadata
        result['api_version'] = '1.1.0'
        result['provider_used'] = data_provider.active_provider[0]
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in get_trending: {str(e)}")
        return jsonify({'error': f'Failed to fetch trending searches: {str(e)}'}), 500

@app.route('/api/trends/suggestions', methods=['GET'])
def get_suggestions():
    """Enhanced suggestions with multiple sources"""
    try:
        keyword = request.args.get('keyword', '').strip()
        
        if not keyword:
            return jsonify({'error': 'Keyword parameter is required'}), 400
        
        if not data_provider:
            return jsonify({'error': 'Data provider not available'}), 500
            
        logger.info(f"Getting suggestions for keyword: {keyword}")
        
        provider = data_provider.get_provider()
        result = provider.get_suggestions(keyword)
        
        # Add metadata
        result['api_version'] = '1.1.0'
        result['provider_used'] = data_provider.active_provider[0]
        
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
        'api_version': '1.1.0'
    })

@app.route('/api/trends/compare', methods=['POST'])
def compare_trends():
    """Enhanced compare functionality"""
    try:
        data = request.get_json()
        keywords = data.get('keywords', [])
        geo = data.get('geo', 'US')
        timeframe = data.get('timeframe', 'today 12-m')
        
        if not keywords or len(keywords) < 2:
            return jsonify({'error': 'At least 2 keywords are required for comparison'}), 400
            
        if len(keywords) > 5:
            return jsonify({'error': 'Maximum 5 keywords allowed for comparison'}), 400
        
        if not data_provider:
            return jsonify({'error': 'Data provider not available'}), 500
            
        logger.info(f"Comparing keywords: {keywords}, geo: {geo}")
        
        # Get trends for each keyword
        comparison_data = []
        provider = data_provider.get_provider()
        
        for keyword in keywords:
            try:
                result = provider.search_trends(keyword, geo, timeframe)
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
            'api_version': '1.1.0',
            'provider_used': data_provider.active_provider[0]
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in compare_trends: {str(e)}")
        return jsonify({'error': f'Failed to compare trends: {str(e)}'}), 500

@app.route('/api/trends/providers', methods=['GET'])
def get_providers():
    """Get available data providers and their status"""
    if not data_provider:
        return jsonify({'error': 'Data provider not available'}), 500
    
    status = data_provider.get_provider_status()
    active = data_provider.active_provider[0] if data_provider.active_provider else None
    
    return jsonify({
        'active_provider': active,
        'providers': status,
        'timestamp': datetime.now().isoformat(),
        'api_version': '1.1.0'
    })

@app.route('/api/trends/switch-provider', methods=['POST'])
def switch_provider():
    """Switch to different data provider"""
    try:
        data = request.get_json()
        provider_name = data.get('provider', '').strip()
        
        if not provider_name:
            return jsonify({'error': 'Provider name is required'}), 400
        
        if not data_provider:
            return jsonify({'error': 'Data provider not available'}), 500
        
        success = data_provider.switch_provider(provider_name)
        
        if success:
            return jsonify({
                'success': True,
                'active_provider': data_provider.active_provider[0],
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Provider "{provider_name}" not found',
                'available_providers': [name for name, _ in data_provider.providers]
            }), 400
            
    except Exception as e:
        logger.error(f"Error switching provider: {str(e)}")
        return jsonify({'error': f'Failed to switch provider: {str(e)}'}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found', 'api_version': '1.1.0'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error', 'api_version': '1.1.0'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print("🌍 World Trends Explorer Enhanced API v1.1.0")
    print("=" * 50)
    
    if data_provider:
        provider_status = data_provider.get_provider_status()
        active_provider = data_provider.active_provider[0] if data_provider.active_provider else 'None'
        
        print(f"🎯 Active Provider: {active_provider}")
        print("📊 Provider Status:")
        for name, status in provider_status.items():
            status_emoji = "✅" if status.get('status') == 'healthy' else "⚠️" if status.get('status') == 'degraded' else "❌"
            print(f"   {status_emoji} {name}: {status.get('status', 'unknown')}")
        
        print(f"\n🚀 Server starting on port {port}")
        print(f"🔗 Health check: http://localhost:{port}/api/trends/health")
        print(f"📊 Providers info: http://localhost:{port}/api/trends/providers")
    else:
        print("❌ Failed to initialize data providers")
    
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=port, debug=debug)
