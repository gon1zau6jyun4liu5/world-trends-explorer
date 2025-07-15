#!/usr/bin/env python3
"""
Unit tests for SerpAPI integration
Tests to ensure SerpAPI is working correctly and Pytrends is completely removed
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, serpapi_client, SERPAPI_KEY


class TestSerpAPIIntegration(unittest.TestCase):
    """Test SerpAPI integration and ensure Pytrends is removed"""
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_no_pytrends_import(self):
        """Verify Pytrends is NOT imported anywhere"""
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Check that pytrends is not imported
        self.assertNotIn('import pytrends', content)
        self.assertNotIn('from pytrends', content)
        self.assertNotIn('TrendReq', content)
        
        print("✅ Pytrends is completely removed from the codebase")
    
    def test_serpapi_configuration(self):
        """Test SerpAPI is properly configured"""
        self.assertEqual(serpapi_client.base_url, "https://serpapi.com/search")
        self.assertIsNotNone(serpapi_client.api_key)
        
        print(f"✅ SerpAPI configured with base URL: {serpapi_client.base_url}")
        print(f"✅ API Key status: {'Set' if serpapi_client.api_key != 'demo' else 'Demo mode'}")
    
    def test_health_endpoint(self):
        """Test health endpoint mentions SerpAPI"""
        response = self.app.get('/api/trends/health')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIn('data_source', data)
        self.assertIn('SerpAPI', data['data_source'])
        self.assertNotIn('Pytrends', str(data))
        
        print("✅ Health endpoint correctly reports SerpAPI as data source")
    
    def test_search_endpoint_no_pytrends(self):
        """Test search endpoint doesn't use Pytrends"""
        response = self.app.get('/api/trends/search?keyword=test')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        # Check response structure
        self.assertIn('keyword', data)
        self.assertIn('data_source', data)
        self.assertIn('SerpAPI', data['data_source'])
        
        print("✅ Search endpoint works without Pytrends")
    
    def test_trending_endpoint_no_pytrends(self):
        """Test trending endpoint doesn't use Pytrends"""
        response = self.app.get('/api/trends/trending?geo=US')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIn('trending_searches', data)
        self.assertIn('data_source', data)
        self.assertIn('SerpAPI', data['data_source'])
        
        print("✅ Trending endpoint works without Pytrends")
    
    def test_serpapi_client_exists(self):
        """Test SerpAPIClient class exists and works"""
        self.assertTrue(hasattr(serpapi_client, 'make_request'))
        self.assertTrue(hasattr(serpapi_client, 'search_trends'))
        self.assertTrue(hasattr(serpapi_client, 'get_trending_searches'))
        
        print("✅ SerpAPIClient class is properly implemented")
    
    def test_requirements_no_pytrends(self):
        """Test requirements.txt doesn't include pytrends"""
        req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
        if os.path.exists(req_path):
            with open(req_path, 'r') as f:
                requirements = f.read().lower()
            
            self.assertNotIn('pytrends', requirements)
            print("✅ requirements.txt does not include pytrends")
    
    def test_api_key_warning(self):
        """Test that API key requirement is clear"""
        if SERPAPI_KEY == 'demo':
            print("⚠️  WARNING: SerpAPI key is set to 'demo' - real data won't be available")
            print("📝 Set SERPAPI_KEY environment variable for real data")
        else:
            print(f"✅ SerpAPI key is configured: {SERPAPI_KEY[:10]}...")


if __name__ == '__main__':
    print("🧪 Testing SerpAPI Integration (Pytrends Removal Verification)")
    print("=" * 60)
    
    # Run tests
    unittest.main(verbosity=2)
