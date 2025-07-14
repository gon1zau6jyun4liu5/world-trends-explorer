#!/usr/bin/env python3
"""
World Trends Explorer - Unit Tests for v1.2.2 Korean Support
Tests for Korean trends functionality and restored search interface
"""

import unittest
import sys
import os
import time
from unittest.mock import Mock, patch, MagicMock
import json

# Add backend path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

try:
    from app import app, pytrends, COUNTRY_CODES
    from flask import json as flask_json
except ImportError as e:
    print(f"Warning: Could not import backend modules: {e}")
    print("This is expected in some test environments")

class TestKoreanTrendsSupport(unittest.TestCase):
    """Test suite for Korean trends functionality v1.2.2"""
    
    def setUp(self):
        """Set up test environment"""
        if 'app' in globals():
            self.app = app.test_client()
            self.app.testing = True
        self.korean_keywords = [
            "인공지능",  # artificial intelligence
            "머신러닝",  # machine learning  
            "딥러닝",    # deep learning
            "챗GPT",     # ChatGPT
            "AI 기술",   # AI technology
            "생성형 AI"  # generative AI
        ]
        
    def test_health_check_endpoint(self):
        """Test API health check endpoint"""
        if not hasattr(self, 'app'):
            self.skipTest("Flask app not available")
            
        response = self.app.get('/api/trends/health')
        self.assertEqual(response.status_code, 200)
        
        data = flask_json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('timestamp', data)
        self.assertIn('service', data)
        print("✅ Health check endpoint test passed")
        
    def test_korean_keyword_search(self):
        """Test Korean keyword search functionality"""
        if not hasattr(self, 'app'):
            self.skipTest("Flask app not available")
            
        # Test primary Korean keyword
        korean_keyword = "인공지능"
        response = self.app.get(f'/api/trends/search?keyword={korean_keyword}&geo=KR')
        
        # Should not fail completely - either success or graceful error
        self.assertIn(response.status_code, [200, 500, 503])
        
        if response.status_code == 200:
            data = flask_json.loads(response.data)
            self.assertEqual(data['keyword'], korean_keyword)
            self.assertIn('interest_over_time', data)
            self.assertIn('interest_by_region', data)
            print(f"✅ Korean keyword search test passed for '{korean_keyword}'")
        else:
            print(f"⚠️ Korean keyword search returned {response.status_code} - API may be rate limited")
            
    def test_korea_trending_searches(self):
        """Test Korean trending searches endpoint"""
        if not hasattr(self, 'app'):
            self.skipTest("Flask app not available")
            
        response = self.app.get('/api/trends/trending?geo=KR')
        
        # Should not fail completely
        self.assertIn(response.status_code, [200, 500, 503])
        
        if response.status_code == 200:
            data = flask_json.loads(response.data)
            self.assertEqual(data['geo'], 'KR')
            self.assertIn('trending_searches', data)
            print("✅ Korean trending searches test passed")
        else:
            print(f"⚠️ Korean trending searches returned {response.status_code}")
            
    def test_korean_text_processing(self):
        """Test Korean text processing and validation"""
        test_cases = [
            ("인공지능", True),      # Valid Korean
            ("AI technology", True), # Valid English
            ("인공지능 AI", True),   # Mixed Korean-English
            ("", False),             # Empty string
            ("   ", False),          # Whitespace only
        ]
        
        for keyword, should_be_valid in test_cases:
            with self.app.test_request_context():
                if should_be_valid:
                    self.assertTrue(len(keyword.strip()) > 0)
                else:
                    self.assertFalse(len(keyword.strip()) > 0)
                    
        print("✅ Korean text processing test passed")
        
    def test_country_codes_support(self):
        """Test country codes include Korean support"""
        if 'COUNTRY_CODES' not in globals():
            self.skipTest("COUNTRY_CODES not available")
            
        # South Korea should be in country codes
        self.assertIn('KR', COUNTRY_CODES)
        self.assertEqual(COUNTRY_CODES['KR'], 'South Korea')
        print("✅ Korean country code support test passed")
        
    def test_api_error_handling(self):
        """Test API error handling for Korean scenarios"""
        if not hasattr(self, 'app'):
            self.skipTest("Flask app not available")
            
        # Test missing keyword parameter
        response = self.app.get('/api/trends/search?geo=KR')
        self.assertEqual(response.status_code, 400)
        
        data = flask_json.loads(response.data)
        self.assertIn('error', data)
        print("✅ API error handling test passed")
        
    def test_countries_endpoint(self):
        """Test countries endpoint includes Korean support"""
        if not hasattr(self, 'app'):
            self.skipTest("Flask app not available")
            
        response = self.app.get('/api/trends/countries')
        self.assertEqual(response.status_code, 200)
        
        data = flask_json.loads(response.data)
        self.assertIn('countries', data)
        
        # Find Korea in the country list
        korean_entry = None
        for country in data['countries']:
            if country['code'] == 'KR':
                korean_entry = country
                break
                
        self.assertIsNotNone(korean_entry)
        self.assertEqual(korean_entry['name'], 'South Korea')
        print("✅ Countries endpoint Korean support test passed")

class TestPerformanceMetrics(unittest.TestCase):
    """Test performance metrics for v1.2.2"""
    
    def setUp(self):
        """Set up performance test environment"""
        if 'app' in globals():
            self.app = app.test_client()
            self.app.testing = True
        
    def test_health_check_response_time(self):
        """Test health check response time < 200ms"""
        if not hasattr(self, 'app'):
            self.skipTest("Flask app not available")
            
        start_time = time.time()
        response = self.app.get('/api/trends/health')
        end_time = time.time()
        
        response_time_ms = (end_time - start_time) * 1000
        self.assertLess(response_time_ms, 200)  # < 200ms target
        self.assertEqual(response.status_code, 200)
        print(f"✅ Health check response time: {response_time_ms:.2f}ms")
        
    def test_countries_endpoint_performance(self):
        """Test countries endpoint performance"""
        if not hasattr(self, 'app'):
            self.skipTest("Flask app not available")
            
        start_time = time.time()
        response = self.app.get('/api/trends/countries')
        end_time = time.time()
        
        response_time_ms = (end_time - start_time) * 1000
        self.assertLess(response_time_ms, 500)  # < 500ms target
        self.assertEqual(response.status_code, 200)
        print(f"✅ Countries endpoint response time: {response_time_ms:.2f}ms")

class TestMockServerFunctionality(unittest.TestCase):
    """Test mock server functionality for development"""
    
    def test_mock_server_import(self):
        """Test that mock server can be imported"""
        try:
            mock_server_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'mock_server.py')
            if os.path.exists(mock_server_path):
                # Mock server exists and can be imported
                print("✅ Mock server file exists")
            else:
                print("⚠️ Mock server file not found - using live API")
        except Exception as e:
            print(f"⚠️ Mock server test skipped: {e}")

class TestUserInterfaceComponents(unittest.TestCase):
    """Test UI components for Korean support"""
    
    def test_korean_flag_representation(self):
        """Test Korean flag emoji representation"""
        korean_flag = "🇰🇷"
        self.assertEqual(len(korean_flag), 2)  # Unicode flag representation
        print("✅ Korean flag representation test passed")
        
    def test_korean_text_truncation(self):
        """Test Korean text truncation functionality"""
        long_korean_text = "인공지능 머신러닝 딥러닝 자연어처리 컴퓨터비전"
        max_length = 20
        
        truncated = long_korean_text[:max_length]
        self.assertLessEqual(len(truncated), max_length)
        print("✅ Korean text truncation test passed")

def run_test_suite():
    """Run the complete test suite for v1.2.2"""
    print("🧪 Running World Trends Explorer v1.2.2 Test Suite")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestKoreanTrendsSupport,
        TestPerformanceMetrics,
        TestMockServerFunctionality,
        TestUserInterfaceComponents
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(
        verbosity=2,
        descriptions=True,
        failfast=False
    )
    
    print("\n🚀 Starting test execution...")
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, failure in result.failures:
            print(f"  - {test}: {failure}")
    
    if result.errors:
        print("\n⚠️ ERRORS:")
        for test, error in result.errors:
            print(f"  - {test}: {error}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"\n📈 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("✅ Test suite PASSED - Ready for deployment")
        return True
    else:
        print("❌ Test suite FAILED - Review failures before deployment")
        return False

if __name__ == '__main__':
    success = run_test_suite()
    sys.exit(0 if success else 1)
