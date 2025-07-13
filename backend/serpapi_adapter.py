#!/usr/bin/env python3
"""
SerpAPI Adapter for World Trends Explorer
🔍 Alternative data source using SerpAPI for Google Trends functionality
"""

import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import os
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SerpAPIConfig:
    """SerpAPI configuration settings"""
    api_key: str
    base_url: str = "https://serpapi.com/search"
    timeout: int = 30
    max_retries: int = 3

class SerpAPIAdapter:
    """
    SerpAPI adapter for Google Trends functionality
    Provides alternative data source when Pytrends is unavailable
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('SERPAPI_KEY')
        if not self.api_key:
            logger.warning("SerpAPI key not provided. Using mock data mode.")
            self.mock_mode = True
        else:
            self.mock_mode = False
            
        self.config = SerpAPIConfig(
            api_key=self.api_key or "demo_key",
            base_url="https://serpapi.com/search"
        )
        
        # Country mapping for SerpAPI
        self.country_mapping = {
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

    def _make_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP request to SerpAPI"""
        if self.mock_mode:
            return self._generate_mock_response(params)
            
        try:
            params['api_key'] = self.config.api_key
            
            response = requests.get(
                self.config.base_url,
                params=params,
                timeout=self.config.timeout
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"SerpAPI request failed: {e}")
            return self._generate_fallback_response(params)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse SerpAPI response: {e}")
            return self._generate_fallback_response(params)

    def search_trends(self, keyword: str, geo: str = '', timeframe: str = 'today 12-m') -> Dict[str, Any]:
        """
        Search for trends data using SerpAPI Google Trends
        
        Args:
            keyword: Search term
            geo: Country code (e.g., 'US', 'GB')
            timeframe: Time period for data
            
        Returns:
            Trends data in Pytrends-compatible format
        """
        logger.info(f"Searching trends for: {keyword}, geo: {geo}")
        
        # SerpAPI Google Trends parameters
        params = {
            'engine': 'google_trends',
            'q': keyword,
            'data_type': 'TIMESERIES',
            'date': self._convert_timeframe(timeframe)
        }
        
        if geo:
            params['geo'] = geo
            
        # Get main trends data
        response = self._make_request(params)
        
        # Get regional data
        regional_params = params.copy()
        regional_params['data_type'] = 'GEO_MAP'
        regional_response = self._make_request(regional_params)
        
        # Get related queries
        related_params = params.copy()
        related_params['data_type'] = 'RELATED_QUERIES'
        related_response = self._make_request(related_params)
        
        return self._format_trends_response(
            keyword, geo, timeframe, response, regional_response, related_response
        )

    def get_trending_searches(self, geo: str = 'US') -> Dict[str, Any]:
        """
        Get trending searches for a specific country
        
        Args:
            geo: Country code
            
        Returns:
            Trending searches data
        """
        logger.info(f"Getting trending searches for: {geo}")
        
        params = {
            'engine': 'google_trends',
            'data_type': 'TRENDING_SEARCHES',
            'geo': geo,
            'date': 'today'
        }
        
        response = self._make_request(params)
        return self._format_trending_response(geo, response)

    def get_suggestions(self, keyword: str) -> Dict[str, Any]:
        """
        Get keyword suggestions using SerpAPI
        
        Args:
            keyword: Partial keyword for suggestions
            
        Returns:
            Suggestions data
        """
        logger.info(f"Getting suggestions for: {keyword}")
        
        params = {
            'engine': 'google_autocomplete',
            'q': keyword,
            'gl': 'us'
        }
        
        response = self._make_request(params)
        return self._format_suggestions_response(keyword, response)

    def _convert_timeframe(self, timeframe: str) -> str:
        """Convert Pytrends timeframe to SerpAPI format"""
        timeframe_mapping = {
            'now 1-H': 'now 1-H',
            'now 4-H': 'now 4-H', 
            'now 1-d': 'now 1-d',
            'now 7-d': 'now 7-d',
            'today 1-m': 'today 1-m',
            'today 3-m': 'today 3-m',
            'today 12-m': 'today 12-m',
            'today 5-y': 'today 5-y',
            'all': '2004-01-01 ' + datetime.now().strftime('%Y-%m-%d')
        }
        
        return timeframe_mapping.get(timeframe, 'today 12-m')

    def _format_trends_response(self, keyword: str, geo: str, timeframe: str, 
                              main_response: Dict, regional_response: Dict, 
                              related_response: Dict) -> Dict[str, Any]:
        """Format SerpAPI response to match Pytrends structure"""
        
        # Extract time series data
        interest_over_time = []
        if 'interest_over_time' in main_response:
            for item in main_response['interest_over_time'].get('timeline_data', []):
                interest_over_time.append({
                    'date': item.get('date', ''),
                    'value': item.get('values', [{}])[0].get('value', 0)
                })
        
        # Extract regional data
        interest_by_region = []
        if 'interest_by_region' in regional_response:
            for item in regional_response['interest_by_region'].get('geoMapData', []):
                interest_by_region.append({
                    'geoName': item.get('geoName', ''),
                    'geoCode': item.get('geoCode', ''),
                    'value': item.get('value', [{}])[0].get('value', 0) if item.get('value') else 0
                })
        
        # Extract related queries
        related_queries = {'top': [], 'rising': []}
        if 'related_queries' in related_response:
            related_data = related_response['related_queries']
            
            # Top queries
            if 'top' in related_data:
                for item in related_data['top']:
                    related_queries['top'].append({
                        'query': item.get('query', ''),
                        'value': str(item.get('value', ''))
                    })
            
            # Rising queries  
            if 'rising' in related_data:
                for item in related_data['rising']:
                    related_queries['rising'].append({
                        'query': item.get('query', ''),
                        'value': item.get('value', 'Breakout')
                    })
        
        return {
            'keyword': keyword,
            'geo': geo,
            'timeframe': timeframe,
            'timestamp': datetime.now().isoformat(),
            'interest_over_time': interest_over_time,
            'interest_by_region': interest_by_region,
            'related_queries': related_queries,
            'data_source': 'SerpAPI',
            'note': 'Data provided by SerpAPI Google Trends'
        }

    def _format_trending_response(self, geo: str, response: Dict) -> Dict[str, Any]:
        """Format trending searches response"""
        trending_searches = []
        
        if 'trending_searches' in response:
            for i, item in enumerate(response['trending_searches'], 1):
                trending_searches.append({
                    'rank': i,
                    'query': item.get('query', '')
                })
        
        return {
            'geo': geo,
            'country': self.country_mapping.get(geo, geo),
            'timestamp': datetime.now().isoformat(),
            'trending_searches': trending_searches,
            'data_source': 'SerpAPI'
        }

    def _format_suggestions_response(self, keyword: str, response: Dict) -> Dict[str, Any]:
        """Format suggestions response"""
        suggestions = []
        
        if 'suggestions' in response:
            for item in response['suggestions']:
                suggestions.append({
                    'mid': f'/m/{keyword}_{len(suggestions)}',
                    'title': item.get('value', ''),
                    'type': 'Topic'
                })
        
        return {
            'keyword': keyword,
            'suggestions': suggestions,
            'timestamp': datetime.now().isoformat(),
            'data_source': 'SerpAPI'
        }

    def _generate_mock_response(self, params: Dict) -> Dict[str, Any]:
        """Generate mock response when API key is not available"""
        logger.info("Generating mock SerpAPI response")
        
        engine = params.get('engine', 'google_trends')
        data_type = params.get('data_type', 'TIMESERIES')
        query = params.get('q', 'sample')
        
        if engine == 'google_trends':
            if data_type == 'TIMESERIES':
                return self._mock_timeseries_data(query)
            elif data_type == 'GEO_MAP':
                return self._mock_regional_data(query)
            elif data_type == 'RELATED_QUERIES':
                return self._mock_related_data(query)
            elif data_type == 'TRENDING_SEARCHES':
                return self._mock_trending_data()
        elif engine == 'google_autocomplete':
            return self._mock_suggestions_data(query)
        
        return {}

    def _mock_timeseries_data(self, query: str) -> Dict:
        """Generate mock time series data"""
        timeline_data = []
        start_date = datetime.now() - timedelta(days=365)
        
        for i in range(52):  # 52 weeks
            date = start_date + timedelta(weeks=i)
            value = max(10, min(100, 50 + (i % 20) - 10 + hash(query) % 30))
            
            timeline_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'values': [{'value': value}]
            })
        
        return {
            'interest_over_time': {
                'timeline_data': timeline_data
            }
        }

    def _mock_regional_data(self, query: str) -> Dict:
        """Generate mock regional data"""
        geo_data = []
        
        for code, name in list(self.country_mapping.items())[:15]:
            value = max(10, min(100, hash(f"{query}_{code}") % 100))
            geo_data.append({
                'geoName': name,
                'geoCode': code,
                'value': [{'value': value}]
            })
        
        return {
            'interest_by_region': {
                'geoMapData': geo_data
            }
        }

    def _mock_related_data(self, query: str) -> Dict:
        """Generate mock related queries data"""
        return {
            'related_queries': {
                'top': [
                    {'query': f'{query} tutorial', 'value': 100},
                    {'query': f'{query} guide', 'value': 80},
                    {'query': f'{query} examples', 'value': 60},
                    {'query': f'{query} tips', 'value': 40},
                    {'query': f'{query} tricks', 'value': 20}
                ],
                'rising': [
                    {'query': f'{query} 2025', 'value': 'Breakout'},
                    {'query': f'{query} new', 'value': '+500%'},
                    {'query': f'{query} latest', 'value': '+300%'},
                    {'query': f'{query} update', 'value': '+200%'},
                    {'query': f'{query} news', 'value': '+150%'}
                ]
            }
        }

    def _mock_trending_data(self) -> Dict:
        """Generate mock trending searches"""
        trending_searches = [
            {'query': 'ChatGPT'},
            {'query': 'AI Technology'},
            {'query': 'Climate Change'},
            {'query': 'Electric Vehicles'},
            {'query': 'Cryptocurrency'},
            {'query': 'Space Exploration'},
            {'query': 'Renewable Energy'},
            {'query': 'Machine Learning'},
            {'query': 'Remote Work'},
            {'query': 'Sustainable Living'}
        ]
        
        return {'trending_searches': trending_searches}

    def _mock_suggestions_data(self, query: str) -> Dict:
        """Generate mock suggestions"""
        suggestions = [
            {'value': f'{query} tutorial'},
            {'value': f'{query} examples'},
            {'value': f'{query} guide'},
            {'value': f'{query} tips'},
            {'value': f'{query} course'}
        ]
        
        return {'suggestions': suggestions}

    def _generate_fallback_response(self, params: Dict) -> Dict[str, Any]:
        """Generate fallback response when SerpAPI fails"""
        logger.warning("Using fallback response due to API failure")
        return self._generate_mock_response(params)

    def health_check(self) -> Dict[str, Any]:
        """Check SerpAPI connection health"""
        if self.mock_mode:
            return {
                'status': 'healthy',
                'data_source': 'SerpAPI Mock',
                'timestamp': datetime.now().isoformat(),
                'note': 'Running in mock mode - no API key provided'
            }
        
        try:
            # Simple test request
            params = {
                'engine': 'google_trends',
                'q': 'test',
                'data_type': 'TIMESERIES',
                'api_key': self.config.api_key
            }
            
            response = requests.get(
                self.config.base_url,
                params=params,
                timeout=5
            )
            
            if response.status_code == 200:
                return {
                    'status': 'healthy',
                    'data_source': 'SerpAPI',
                    'timestamp': datetime.now().isoformat(),
                    'note': 'SerpAPI connection successful'
                }
            else:
                return {
                    'status': 'degraded',
                    'data_source': 'SerpAPI',
                    'timestamp': datetime.now().isoformat(),
                    'note': f'SerpAPI returned status {response.status_code}'
                }
                
        except Exception as e:
            return {
                'status': 'unhealthy',
                'data_source': 'SerpAPI',
                'timestamp': datetime.now().isoformat(),
                'note': f'SerpAPI connection failed: {str(e)}'
            }

# Usage example
if __name__ == "__main__":
    # Test SerpAPI adapter
    adapter = SerpAPIAdapter()
    
    print("🔍 Testing SerpAPI Adapter...")
    
    # Health check
    health = adapter.health_check()
    print(f"Health: {health}")
    
    # Search trends
    trends = adapter.search_trends("artificial intelligence", "US")
    print(f"Trends found: {len(trends.get('interest_over_time', []))} data points")
    
    # Trending searches
    trending = adapter.get_trending_searches("US")
    print(f"Trending searches: {len(trending.get('trending_searches', []))}")
    
    # Suggestions
    suggestions = adapter.get_suggestions("AI")
    print(f"Suggestions: {len(suggestions.get('suggestions', []))}")
    
    print("✅ SerpAPI Adapter test completed")
