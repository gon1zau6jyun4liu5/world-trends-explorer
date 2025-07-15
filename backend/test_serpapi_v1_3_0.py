#!/usr/bin/env python3
"""
Unit Tests for World Trends Explorer v1.3.0 SerpAPI Integration
Tests the enhanced SerpAPI functionality and data processing
"""

import unittest
import sys
import os
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app, SerpAPIClient, COUNTRY_CODES


class TestSerpAPIClient(unittest.TestCase):
    """Test SerpAPI client functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = SerpAPIClient()
        self.client.api_key = 'test_key'
    
    def test_init(self):
        """Test SerpAPI client initialization"""
        self.assertEqual(self.client.api_key, 'test_key')
        self.assertEqual(self.client.base_url, "https://serpapi.com/search")
        self.assertIsNotNone(self.client.session)
    
    @patch('requests.Session.get')
    def test_make_request_success(self, mock_get):
        """Test successful SerpAPI request"""
        # Mock successful response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {'test': 'data'}
        mock_get.return_value = mock_response
        
        result = self.client.make_request({'query': 'test'})
        
        self.assertEqual(result, {'test': 'data'})
        mock_get.assert_called_once()
    
    @patch('requests.Session.get')
    def test_make_request_timeout(self, mock_get):
        """Test SerpAPI request timeout"""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout()
        
        result = self.client.make_request({'query': 'test'})
        
        self.assertIsNone(result)
    
    @patch('requests.Session.get')
    def test_make_request_error(self, mock_get):
        """Test SerpAPI request error"""
        import requests
        mock_get.side_effect = requests.exceptions.RequestException("API Error")
        
        result = self.client.make_request({'query': 'test'})
        
        self.assertIsNone(result)
    
    def test_generate_time_series(self):
        """Test time series data generation"""
        data = self.client._generate_time_series('artificial intelligence')
        
        self.assertEqual(len(data), 52)  # 52 weeks
        
        for point in data:
            self.assertIn('date', point)
            self.assertIn('value', point)
            self.assertGreaterEqual(point['value'], 1)
            self.assertLessEqual(point['value'], 100)
            
            # Validate date format
            datetime.fromisoformat(point['date'])
    
    def test_generate_time_series_ai_trend(self):
        """Test AI keyword generates higher baseline"""
        ai_data = self.client._generate_time_series('artificial intelligence')
        normal_data = self.client._generate_time_series('random topic')
        
        ai_avg = sum(point['value'] for point in ai_data) / len(ai_data)
        normal_avg = sum(point['value'] for point in normal_data) / len(normal_data)
        
        # AI should have higher average due to base_popularity = 70
        self.assertGreater(ai_avg, normal_avg)
    
    def test_generate_regional_data(self):
        """Test regional data generation"""
        data = self.client._generate_regional_data('artificial intelligence')
        
        self.assertLessEqual(len(data), 25)  # Top 25 regions
        
        for region in data:
            self.assertIn('geoName', region)
            self.assertIn('geoCode', region)
            self.assertIn('value', region)
            self.assertGreaterEqual(region['value'], 1)
            self.assertLessEqual(region['value'], 100)
            
            # Check if country code exists in our mapping
            self.assertIn(region['geoCode'], COUNTRY_CODES)
        
        # Data should be sorted by value descending
        values = [region['value'] for region in data]
        self.assertEqual(values, sorted(values, reverse=True))
    
    def test_generate_regional_data_kpop_boost(self):
        """Test K-pop keyword gives Korea boost"""
        data = self.client._generate_regional_data('k-pop')
        
        # Find Korea in the data
        korea_data = next((item for item in data if item['geoCode'] == 'KR'), None)
        self.assertIsNotNone(korea_data)
        self.assertEqual(korea_data['value'], 100)  # Should be maxed out
    
    def test_generate_related_queries(self):
        """Test related queries generation"""
        queries = self.client._generate_related_queries('artificial intelligence')
        
        self.assertIn('top', queries)
        self.assertIn('rising', queries)
        
        # Check top queries structure
        for query in queries['top']:
            self.assertIn('query', query)
            self.assertIn('value', query)
        
        # Check rising queries structure
        for query in queries['rising']:
            self.assertIn('query', query)
            self.assertIn('value', query)
        
        # AI should have specific enhancements
        ai_queries = [q['query'] for q in queries['top']]
        self.assertTrue(any('machine learning' in q for q in ai_queries))
    
    def test_get_curated_trending(self):
        """Test curated trending data by region"""
        us_trending = self.client._get_curated_trending('US')
        kr_trending = self.client._get_curated_trending('KR')
        
        self.assertEqual(len(us_trending), 10)
        self.assertEqual(len(kr_trending), 10)
        
        # Korea should have Korean content
        self.assertTrue(any('인공지능' in trend for trend in kr_trending))
        self.assertTrue(any('K-pop' in trend for trend in kr_trending))
        
        # US should have English content
        self.assertTrue(any('AI Technology' in trend for trend in us_trending))
    
    @patch.object(SerpAPIClient, 'make_request')
    def test_search_trends(self, mock_request):
        """Test search trends functionality"""
        mock_request.return_value = None  # No real SerpAPI data
        
        result = self.client.search_trends('test keyword', 'US')
        
        self.assertEqual(result['keyword'], 'test keyword')
        self.assertEqual(result['geo'], 'US')
        self.assertEqual(result['country'], 'United States')
        self.assertIn('interest_over_time', result)
        self.assertIn('interest_by_region', result)
        self.assertIn('related_queries', result)
        self.assertFalse(result['serpapi_enhanced'])
    
    @patch.object(SerpAPIClient, 'make_request')
    def test_search_trends_with_serpapi_data(self, mock_request):
        """Test search trends with real SerpAPI data"""
        mock_request.return_value = {
            'timeline_data': [{'date': '2025-01-01', 'value': 50}]
        }
        
        result = self.client.search_trends('test keyword', 'US')
        
        self.assertTrue(result['serpapi_enhanced'])
        self.assertEqual(result['real_data_points'], 1)
    
    @patch.object(SerpAPIClient, 'make_request')
    def test_get_trending_searches(self, mock_request):
        """Test trending searches functionality"""
        mock_request.return_value = None  # No real SerpAPI data
        
        result = self.client.get_trending_searches('US')
        
        self.assertEqual(result['geo'], 'US')
        self.assertEqual(result['country'], 'United States')
        self.assertIn('trending_searches', result)
        self.assertEqual(len(result['trending_searches']), 10)
        self.assertFalse(result['serpapi_enhanced'])


class TestFlaskAPI(unittest.TestCase):
    """Test Flask API endpoints"""
    
    def setUp(self):
        """Set up test client"""
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.ctx = app.app_context()
        self.ctx.push()
    
    def tearDown(self):
        """Clean up test context"""
        self.ctx.pop()
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get('/api/trends/health')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['version'], '1.3.0')
        self.assertEqual(data['data_source'], 'SerpAPI Enhanced')
        self.assertIn('countries_available', data)
        self.assertIn('features', data)
    
    def test_search_trends_missing_keyword(self):
        """Test search trends without keyword"""
        response = self.client.get('/api/trends/search')
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Keyword parameter is required', data['error'])
    
    @patch('app.serpapi_client.search_trends')
    def test_search_trends_success(self, mock_search):
        """Test successful search trends"""
        mock_search.return_value = {
            'keyword': 'test',
            'geo': 'US',
            'interest_over_time': [],
            'interest_by_region': []
        }
        
        response = self.client.get('/api/trends/search?keyword=test')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['keyword'], 'test')
        self.assertEqual(data['version'], '1.3.0')
    
    def test_trending_searches_invalid_country(self):
        """Test trending searches with invalid country"""
        response = self.client.get('/api/trends/trending?geo=INVALID')
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Unsupported country code', data['error'])
    
    @patch('app.serpapi_client.get_trending_searches')
    def test_trending_searches_success(self, mock_trending):
        """Test successful trending searches"""
        mock_trending.return_value = {
            'geo': 'US',
            'trending_searches': []
        }
        
        response = self.client.get('/api/trends/trending?geo=US')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['geo'], 'US')
        self.assertEqual(data['version'], '1.3.0')
    
    def test_suggestions_missing_keyword(self):
        """Test suggestions without keyword"""
        response = self.client.get('/api/trends/suggestions')
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_suggestions_success(self):
        """Test successful suggestions"""
        response = self.client.get('/api/trends/suggestions?keyword=ai')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['keyword'], 'ai')
        self.assertEqual(data['version'], '1.3.0')
        self.assertIn('suggestions', data)
        self.assertIsInstance(data['suggestions'], list)
    
    def test_countries_list(self):
        """Test countries list endpoint"""
        response = self.client.get('/api/trends/countries')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('countries', data)
        self.assertEqual(data['version'], '1.3.0')
        self.assertGreater(data['total_countries'], 40)  # Should have many countries
        
        # Check country structure
        for country in data['countries']:
            self.assertIn('code', country)
            self.assertIn('name', country)
    
    def test_compare_trends_insufficient_keywords(self):
        """Test compare trends with insufficient keywords"""
        payload = {'keywords': ['only_one']}
        
        response = self.client.post('/api/trends/compare', 
                                  json=payload,
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('At least 2 keywords', data['error'])
    
    def test_compare_trends_too_many_keywords(self):
        """Test compare trends with too many keywords"""
        payload = {'keywords': ['one', 'two', 'three', 'four', 'five', 'six']}
        
        response = self.client.post('/api/trends/compare',
                                  json=payload,
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Maximum 5 keywords', data['error'])
    
    def test_compare_trends_success(self):
        """Test successful compare trends"""
        payload = {
            'keywords': ['ai', 'blockchain'],
            'geo': 'US'
        }
        
        response = self.client.post('/api/trends/compare',
                                  json=payload,
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['keywords'], ['ai', 'blockchain'])
        self.assertEqual(data['geo'], 'US')
        self.assertEqual(data['version'], '1.3.0')
        self.assertIn('comparison_data', data)
        self.assertIsInstance(data['comparison_data'], list)
    
    def test_404_error(self):
        """Test 404 error handling"""
        response = self.client.get('/api/trends/nonexistent')
        
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['version'], '1.3.0')


class TestCountryCodes(unittest.TestCase):
    """Test country codes functionality"""
    
    def test_country_codes_structure(self):
        """Test country codes have proper structure"""
        for code, info in COUNTRY_CODES.items():
            self.assertIsInstance(code, str)
            self.assertEqual(len(code), 2)  # ISO 2-letter codes
            
            self.assertIsInstance(info, dict)
            self.assertIn('name', info)
            self.assertIn('hl', info)  # Language
            self.assertIn('gl', info)  # Geographic location
    
    def test_major_countries_present(self):
        """Test major countries are present"""
        major_countries = ['US', 'GB', 'DE', 'FR', 'JP', 'KR', 'CN', 'IN', 'BR']
        
        for country in major_countries:
            self.assertIn(country, COUNTRY_CODES)
            self.assertIsInstance(COUNTRY_CODES[country]['name'], str)
    
    def test_language_codes_valid(self):
        """Test language codes are valid"""
        valid_languages = [
            'en', 'de', 'fr', 'es', 'it', 'ja', 'ko', 'zh', 'pt', 'ru',
            'nl', 'sv', 'no', 'da', 'fi', 'pl', 'cs', 'hu', 'tr', 'he',
            'ar', 'th', 'vi', 'id', 'ms', 'el'
        ]
        
        for country_info in COUNTRY_CODES.values():
            self.assertIn(country_info['hl'], valid_languages)


class TestDataGeneration(unittest.TestCase):
    """Test data generation logic"""
    
    def setUp(self):
        """Set up test client"""
        self.client = SerpAPIClient()
    
    def test_time_series_consistency(self):
        """Test time series data consistency"""
        data1 = self.client._generate_time_series('test')
        data2 = self.client._generate_time_series('test')
        
        # Should have same length
        self.assertEqual(len(data1), len(data2))
        
        # Dates should be consistent (same sequence)
        dates1 = [point['date'] for point in data1]
        dates2 = [point['date'] for point in data2]
        self.assertEqual(dates1, dates2)
    
    def test_regional_data_completeness(self):
        """Test regional data includes all countries"""
        data = self.client._generate_regional_data('test')
        
        # Should include data for all countries (limited to top 25)
        country_codes = [item['geoCode'] for item in data]
        
        # All codes should be valid
        for code in country_codes:
            self.assertIn(code, COUNTRY_CODES)
        
        # Should be limited to 25
        self.assertLessEqual(len(data), 25)
    
    def test_keyword_specific_adjustments(self):
        """Test keyword-specific data adjustments"""
        # Test AI keyword
        ai_data = self.client._generate_regional_data('artificial intelligence')
        ai_countries = ['US', 'KR', 'JP', 'CN']
        
        for country in ai_countries:
            country_data = next((item for item in ai_data if item['geoCode'] == country), None)
            if country_data:
                # AI countries should have higher values on average
                self.assertGreaterEqual(country_data['value'], 20)
        
        # Test Olympics keyword
        olympics_data = self.client._generate_regional_data('olympics')
        olympics_countries = ['FR', 'US', 'JP', 'AU']
        
        for country in olympics_countries:
            country_data = next((item for item in olympics_data if item['geoCode'] == country), None)
            if country_data:
                self.assertGreaterEqual(country_data['value'], 20)


if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestSerpAPIClient,
        TestFlaskAPI,
        TestCountryCodes,
        TestDataGeneration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"🧪 World Trends Explorer v1.3.0 - SerpAPI Tests")
    print(f"{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError: ')[-1].split('\n')[0]}")
    
    if result.errors:
        print(f"\n🔴 Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('\n')[-2]}")
    
    if not result.failures and not result.errors:
        print(f"\n✅ All tests passed! SerpAPI integration is working correctly.")
    
    # Exit with proper code
    exit(0 if result.wasSuccessful() else 1)
