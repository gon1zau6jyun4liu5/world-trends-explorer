#!/usr/bin/env python3
"""
Unit Tests for Backend API Service v1.2.4
Tests for Issue #31 - API Service Unavailable Fix
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

try:
    from app import app, initialize_pytrends, handle_api_errors, retry_on_failure
    APP_AVAILABLE = True
except ImportError:
    APP_AVAILABLE = False
    print("Warning: Could not import app module for testing")

class TestAPIServiceReliability(unittest.TestCase):
    """Test suite for Issue #31 - API Service Unavailable"""
    
    def setUp(self):
        """Set up test fixtures"""
        if not APP_AVAILABLE:
            self.skipTest("App module not available")
            
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Mock pytrends globally
        self.pytrends_mock = Mock()
        self.pytrends_patcher = patch('app.pytrends', self.pytrends_mock)
        self.pytrends_patcher.start()
    
    def tearDown(self):
        """Clean up after tests"""
        if hasattr(self, 'pytrends_patcher'):
            self.pytrends_patcher.stop()
    
    def test_health_check_endpoint_availability(self):
        """Test that health check endpoint is accessible"""
        response = self.client.get('/api/trends/health')
        
        self.assertIn(response.status_code, [200, 503])  # Should respond, even if degraded
        
        data = json.loads(response.data)
        self.assertIn('status', data)
        self.assertIn('timestamp', data)
        self.assertIn('service', data)
        self.assertIn('v1.2.4', data['service'])
    
    def test_health_check_with_pytrends_disconnected(self):
        """Test health check when pytrends is unavailable"""
        with patch('app.pytrends', None):
            response = self.client.get('/api/trends/health')
            
            data = json.loads(response.data)
            self.assertEqual(data['checks']['pytrends'], 'disconnected')
            self.assertEqual(data['status'], 'degraded')
    
    def test_health_check_with_no_internet(self):
        """Test health check when internet is unavailable"""
        with patch('socket.create_connection', side_effect=OSError("No internet")):
            response = self.client.get('/api/trends/health')
            
            data = json.loads(response.data)
            self.assertEqual(data['checks']['internet'], 'disconnected')
            self.assertEqual(data['status'], 'degraded')
    
    @patch('app.pytrends')
    def test_trending_endpoint_with_retry_success(self, mock_pytrends):
        """Test trending endpoint with successful retry after initial failure"""
        # First call fails, second succeeds
        mock_instance = Mock()
        mock_trending_data = Mock()
        mock_trending_data.empty = False
        mock_trending_data.__getitem__.return_value.tolist.return_value = [
            'trending topic 1', 'trending topic 2', 'trending topic 3'
        ]
        
        mock_instance.trending_searches.side_effect = [
            Exception("Connection failed"),  # First attempt fails
            mock_trending_data  # Second attempt succeeds
        ]
        
        with patch('app.initialize_pytrends', return_value=mock_instance):
            response = self.client.get('/api/trends/trending?geo=US')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertEqual(data['geo'], 'US')
        self.assertIn('trending_searches', data)
        self.assertGreater(len(data['trending_searches']), 0)
    
    @patch('app.pytrends')
    def test_trending_endpoint_complete_failure(self, mock_pytrends):
        """Test trending endpoint when all retries fail"""
        with patch('app.initialize_pytrends', return_value=None):
            response = self.client.get('/api/trends/trending?geo=US')
        
        self.assertEqual(response.status_code, 503)
        data = json.loads(response.data)
        
        self.assertIn('error', data)
        self.assertIn('Service temporarily unavailable', data['error'])
        self.assertIn('suggestion', data)
    
    @patch('app.pytrends')
    def test_search_endpoint_with_pytrends_failure(self, mock_pytrends):
        """Test search endpoint handles pytrends failures gracefully"""
        mock_instance = Mock()
        mock_instance.build_payload.side_effect = Exception("Pytrends connection failed")
        
        with patch('app.initialize_pytrends', return_value=mock_instance):
            response = self.client.get('/api/trends/search?keyword=test')
        
        # Should return error but not crash
        self.assertIn(response.status_code, [500, 503, 504])
        data = json.loads(response.data)
        
        self.assertIn('error', data)
        self.assertIn('error_type', data)
        self.assertIn('suggestion', data)
    
    def test_search_endpoint_validation(self):
        """Test search endpoint input validation"""
        # Test missing keyword
        response = self.client.get('/api/trends/search')
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('Keyword parameter is required', data['error'])
        
        # Test short keyword
        response = self.client.get('/api/trends/search?keyword=a')
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('at least 2 characters', data['error'])
    
    @patch('app.pytrends')
    def test_search_endpoint_partial_data_success(self, mock_pytrends):
        """Test search endpoint handles partial data gracefully"""
        mock_instance = Mock()
        
        # Mock successful build_payload
        mock_instance.build_payload.return_value = None
        
        # Mock partial failures in data retrieval
        mock_instance.interest_over_time.side_effect = Exception("Timeline data failed")
        mock_instance.interest_by_region.return_value = Mock(empty=True)
        mock_instance.related_queries.side_effect = Exception("Related queries failed")
        
        with patch('app.initialize_pytrends', return_value=mock_instance):
            response = self.client.get('/api/trends/search?keyword=test')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Should return structure even with partial failures
        self.assertEqual(data['keyword'], 'test')
        self.assertEqual(data['interest_over_time'], [])
        self.assertEqual(data['interest_by_region'], [])
        self.assertEqual(data['related_queries'], {'top': [], 'rising': []})
    
    def test_compare_endpoint_validation(self):
        """Test compare endpoint input validation"""
        # Test missing body
        response = self.client.post('/api/trends/compare')
        self.assertEqual(response.status_code, 400)
        
        # Test insufficient keywords
        response = self.client.post('/api/trends/compare',
                                  data=json.dumps({'keywords': ['test']}),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)
        
        # Test too many keywords
        response = self.client.post('/api/trends/compare',
                                  data=json.dumps({'keywords': ['a', 'b', 'c', 'd', 'e', 'f']}),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)
    
    def test_countries_endpoint(self):
        """Test countries endpoint availability"""
        response = self.client.get('/api/trends/countries')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('countries', data)
        self.assertIn('total', data)
        self.assertGreater(data['total'], 0)
        
        # Check structure of country data
        if data['countries']:
            country = data['countries'][0]
            self.assertIn('code', country)
            self.assertIn('name', country)
    
    def test_error_handler_consistency(self):
        """Test that error handlers return consistent format"""
        # Test 404 error
        response = self.client.get('/api/trends/nonexistent')
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('timestamp', data)
        self.assertIn('service', data)
        self.assertIn('available_endpoints', data)


class TestRetryMechanism(unittest.TestCase):
    """Test the retry mechanism decorator"""
    
    def test_retry_decorator_success_on_first_attempt(self):
        """Test retry decorator when function succeeds on first attempt"""
        @retry_on_failure(max_retries=3, delay=0.01)
        def successful_function():
            return "success"
        
        result = successful_function()
        self.assertEqual(result, "success")
    
    def test_retry_decorator_success_on_retry(self):
        """Test retry decorator when function succeeds on retry"""
        call_count = 0
        
        @retry_on_failure(max_retries=3, delay=0.01)
        def function_succeeds_on_retry():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success after retry"
        
        result = function_succeeds_on_retry()
        self.assertEqual(result, "success after retry")
        self.assertEqual(call_count, 3)
    
    def test_retry_decorator_max_retries_exceeded(self):
        """Test retry decorator when max retries are exceeded"""
        @retry_on_failure(max_retries=2, delay=0.01)
        def always_failing_function():
            raise Exception("Always fails")
        
        with self.assertRaises(Exception) as context:
            always_failing_function()
        
        self.assertIn("Always fails", str(context.exception))


class TestPytrendsInitialization(unittest.TestCase):
    """Test Pytrends initialization logic"""
    
    @patch('app.TrendReq')
    def test_successful_pytrends_initialization(self, mock_trend_req):
        """Test successful Pytrends initialization"""
        mock_instance = Mock()
        mock_trend_req.return_value = mock_instance
        
        result = initialize_pytrends()
        
        self.assertIsNotNone(result)
        mock_trend_req.assert_called_once_with(
            hl='en-US',
            tz=360,
            timeout=(10, 20),
            retries=2,
            backoff_factor=0.1
        )
    
    @patch('app.TrendReq')
    def test_failed_pytrends_initialization(self, mock_trend_req):
        """Test failed Pytrends initialization"""
        mock_trend_req.side_effect = Exception("Connection failed")
        
        result = initialize_pytrends()
        
        self.assertIsNone(result)


class TestErrorHandlerDecorator(unittest.TestCase):
    """Test the error handler decorator"""
    
    def test_error_handler_with_timeout_error(self):
        """Test error handler categorizes timeout errors correctly"""
        @handle_api_errors
        def timeout_function():
            raise Exception("Connection timeout occurred")
        
        from flask import Flask
        test_app = Flask(__name__)
        
        with test_app.app_context():
            response, status_code = timeout_function()
            
        self.assertEqual(status_code, 504)  # Gateway Timeout
        response_data = json.loads(response.data)
        self.assertIn('Service temporarily unavailable', response_data['error'])
        self.assertIn('suggestion', response_data)
    
    def test_error_handler_with_connection_error(self):
        """Test error handler categorizes connection errors correctly"""
        @handle_api_errors
        def connection_function():
            raise Exception("Connection refused")
        
        from flask import Flask
        test_app = Flask(__name__)
        
        with test_app.app_context():
            response, status_code = connection_function()
            
        self.assertEqual(status_code, 503)  # Service Unavailable
        response_data = json.loads(response.data)
        self.assertIn('Service temporarily unavailable', response_data['error'])


if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestAPIServiceReliability,
        TestRetryMechanism,
        TestPytrendsInitialization,
        TestErrorHandlerDecorator
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with error code if tests failed
    if not result.wasSuccessful():
        exit(1)
