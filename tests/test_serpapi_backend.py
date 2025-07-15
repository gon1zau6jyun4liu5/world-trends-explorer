#!/usr/bin/env python3
"""
Unit tests for SerpAPI backend implementation
"""

import unittest
import json
import os
from unittest.mock import patch, MagicMock
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app_serpapi import app

class TestSerpAPIBackend(unittest.TestCase):
    """Test cases for SerpAPI backend"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
        
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get('/api/trends/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('timestamp', data)
        self.assertIn('api_key_configured', data)
        
    def test_get_countries(self):
        """Test countries endpoint"""
        response = self.client.get('/api/trends/countries')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('countries', data)
        self.assertIsInstance(data['countries'], list)
        self.assertGreater(len(data['countries']), 0)
        
        # Check country structure
        country = data['countries'][0]
        self.assertIn('code', country)
        self.assertIn('name', country)
        
    def test_search_without_keyword(self):
        """Test search endpoint without keyword"""
        response = self.client.get('/api/trends/search')
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Keyword parameter is required')
        
    @patch('backend.app_serpapi.make_serpapi_request')
    def test_search_with_mock_data(self, mock_serpapi):
        """Test search endpoint with mocked SerpAPI response"""
        # Mock SerpAPI response
        mock_serpapi.return_value = {
            'interest_over_time': {
                'timeline_data': [
                    {'date': '2024-01-01', 'values': [{'value': 50}]},
                    {'date': '2024-01-08', 'values': [{'value': 75}]}
                ]
            },
            'interest_by_region': [
                {'location': 'United States', 'geo': 'us', 'value': 100},
                {'location': 'Germany', 'geo': 'de', 'value': 80}
            ],
            'related_queries': {
                'top': [
                    {'query': 'test query 1', 'value': 100},
                    {'query': 'test query 2', 'value': 85}
                ],
                'rising': [
                    {'query': 'rising query 1', 'value': 'Breakout'},
                    {'query': 'rising query 2', 'value': '+500%'}
                ]
            }
        }
        
        # Set API key for test
        with patch.dict(os.environ, {'SERPAPI_API_KEY': 'test-key'}):
            response = self.client.get('/api/trends/search?keyword=test&geo=US')
            
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Verify response structure
        self.assertEqual(data['keyword'], 'test')
        self.assertEqual(data['geo'], 'US')
        self.assertIn('interest_over_time', data)
        self.assertIn('interest_by_region', data)
        self.assertIn('related_queries', data)
        
        # Verify data processing
        self.assertEqual(len(data['interest_over_time']), 2)
        self.assertEqual(data['interest_over_time'][0]['value'], 50)
        self.assertEqual(len(data['interest_by_region']), 2)
        self.assertEqual(data['interest_by_region'][0]['geoCode'], 'US')
        
    def test_search_without_api_key(self):
        """Test search endpoint without API key"""
        # Clear API key
        with patch.dict(os.environ, {'SERPAPI_API_KEY': ''}):
            response = self.client.get('/api/trends/search?keyword=test')
            
        self.assertEqual(response.status_code, 200)  # Returns mock data
        data = json.loads(response.data)
        self.assertIn('note', data)
        self.assertIn('Mock data', data['note'])
        
    @patch('backend.app_serpapi.make_serpapi_request')
    def test_trending_searches(self, mock_serpapi):
        """Test trending searches endpoint"""
        # Mock SerpAPI response
        mock_serpapi.return_value = {
            'trending_searches': [
                {'title': 'Trending 1'},
                {'title': 'Trending 2'},
                {'title': 'Trending 3'}
            ]
        }
        
        with patch.dict(os.environ, {'SERPAPI_API_KEY': 'test-key'}):
            response = self.client.get('/api/trends/trending?geo=US')
            
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertEqual(data['geo'], 'US')
        self.assertIn('trending_searches', data)
        self.assertEqual(len(data['trending_searches']), 3)
        self.assertEqual(data['trending_searches'][0]['rank'], 1)
        self.assertEqual(data['trending_searches'][0]['query'], 'Trending 1')
        
    def test_404_error(self):
        """Test 404 error handling"""
        response = self.client.get('/api/invalid/endpoint')
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Endpoint not found')
        
    @patch('backend.app_serpapi.make_serpapi_request')
    def test_serpapi_error_handling(self, mock_serpapi):
        """Test error handling when SerpAPI fails"""
        # Mock SerpAPI to raise an exception
        mock_serpapi.side_effect = Exception('SerpAPI error')
        
        with patch.dict(os.environ, {'SERPAPI_API_KEY': 'test-key'}):
            response = self.client.get('/api/trends/search?keyword=test')
            
        # Should return mock data instead of error
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('note', data)
        self.assertIn('Mock data', data['note'])

if __name__ == '__main__':
    unittest.main()
