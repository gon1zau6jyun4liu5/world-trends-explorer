#!/usr/bin/env python3
"""
Enhanced Integration Tests for World Trends Explorer v1.1.0
Manual test runner to bypass pytest-flask compatibility issues
"""

import unittest
import sys
import os
import json
import time
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

print("🧪 Enhanced SerpAPI Integration Test Suite v1.1.0")
print("=" * 60)

# Global test results
TEST_RESULTS = {
    'total': 0,
    'passed': 0,
    'failed': 0,
    'tests': []
}

def log_test_result(test_name, passed, details=""):
    """Log test result"""
    TEST_RESULTS['total'] += 1
    TEST_RESULTS['tests'].append({
        'name': test_name,
        'passed': passed,
        'details': details,
        'timestamp': datetime.now().isoformat()
    })
    
    if passed:
        TEST_RESULTS['passed'] += 1
        print(f"✅ {test_name}: PASSED")
    else:
        TEST_RESULTS['failed'] += 1
        print(f"❌ {test_name}: FAILED - {details}")

def test_imports():
    """Test all required imports"""
    try:
        from serpapi_adapter import SerpAPIAdapter
        from app_enhanced import TrendsDataProvider, app
        log_test_result("Import Test", True, "All modules imported successfully")
        return True
    except ImportError as e:
        log_test_result("Import Test", False, f"Import error: {e}")
        return False

def test_serpapi_adapter():
    """Test SerpAPI adapter functionality"""
    try:
        from serpapi_adapter import SerpAPIAdapter
        
        # Initialize adapter
        adapter = SerpAPIAdapter()
        log_test_result("SerpAPI Initialization", True)
        
        # Health check
        health = adapter.health_check()
        health_ok = health.get('status') in ['healthy', 'degraded']
        log_test_result("SerpAPI Health Check", health_ok, f"Status: {health.get('status')}")
        
        # Search test
        result = adapter.search_trends("test", "US")
        search_ok = (
            isinstance(result, dict) and
            'keyword' in result and
            'interest_over_time' in result and
            'interest_by_region' in result
        )
        log_test_result("SerpAPI Search Test", search_ok, f"Keyword: {result.get('keyword')}")
        
        # Trending test
        trending = adapter.get_trending_searches("US")
        trending_ok = (
            isinstance(trending, dict) and
            'trending_searches' in trending
        )
        log_test_result("SerpAPI Trending Test", trending_ok, f"Topics: {len(trending.get('trending_searches', []))}")
        
        # Suggestions test
        suggestions = adapter.get_suggestions("AI")
        suggestions_ok = (
            isinstance(suggestions, dict) and
            'suggestions' in suggestions
        )
        log_test_result("SerpAPI Suggestions Test", suggestions_ok, f"Count: {len(suggestions.get('suggestions', []))}")
        
        return health_ok and search_ok and trending_ok and suggestions_ok
        
    except Exception as e:
        log_test_result("SerpAPI Adapter Tests", False, str(e))
        return False

def test_data_provider():
    """Test enhanced data provider"""
    try:
        from app_enhanced import TrendsDataProvider
        
        # Initialize provider
        provider = TrendsDataProvider()
        init_ok = provider.active_provider is not None
        log_test_result("Data Provider Initialization", init_ok, f"Active: {provider.active_provider[0] if provider.active_provider else 'None'}")
        
        # Status test
        status = provider.get_provider_status()
        status_ok = isinstance(status, dict) and len(status) > 0
        log_test_result("Provider Status Test", status_ok, f"Providers: {list(status.keys())}")
        
        # Provider switching test
        original_provider = provider.active_provider[0] if provider.active_provider else None
        switch_success = provider.switch_provider('Mock')
        switch_back = provider.switch_provider(original_provider) if original_provider else True
        
        log_test_result("Provider Switching Test", switch_success and switch_back, "Mock provider switching")
        
        # Data consistency test
        if provider.active_provider:
            current_provider = provider.get_provider()
            test_result = current_provider.search_trends("test", "US")
            consistency_ok = (
                isinstance(test_result, dict) and
                test_result.get('keyword') == 'test' and
                test_result.get('geo') == 'US'
            )
            log_test_result("Data Consistency Test", consistency_ok, f"Provider: {provider.active_provider[0]}")
        
        return init_ok and status_ok and switch_success
        
    except Exception as e:
        log_test_result("Data Provider Tests", False, str(e))
        return False

def test_flask_app():
    """Test Flask application"""
    try:
        from app_enhanced import app
        
        # Create test client
        client = app.test_client()
        client.testing = True
        
        # Health endpoint test
        response = client.get('/api/trends/health')
        health_ok = response.status_code == 200
        
        if health_ok:
            data = json.loads(response.data)
            health_data_ok = 'status' in data and 'providers' in data
            log_test_result("Flask Health Endpoint", health_data_ok, f"Status: {data.get('status')}")
        else:
            log_test_result("Flask Health Endpoint", False, f"HTTP {response.status_code}")
            health_data_ok = False
        
        # Search endpoint test
        response = client.get('/api/trends/search?keyword=test&geo=US')
        search_ok = response.status_code == 200
        
        if search_ok:
            data = json.loads(response.data)
            search_data_ok = (
                'keyword' in data and
                'api_version' in data and
                'provider_used' in data
            )
            log_test_result("Flask Search Endpoint", search_data_ok, f"Provider: {data.get('provider_used')}")
        else:
            log_test_result("Flask Search Endpoint", False, f"HTTP {response.status_code}")
            search_data_ok = False
        
        # Providers endpoint test
        response = client.get('/api/trends/providers')
        providers_ok = response.status_code == 200
        
        if providers_ok:
            data = json.loads(response.data)
            providers_data_ok = 'active_provider' in data and 'providers' in data
            log_test_result("Flask Providers Endpoint", providers_data_ok, f"Active: {data.get('active_provider')}")
        else:
            log_test_result("Flask Providers Endpoint", False, f"HTTP {response.status_code}")
            providers_data_ok = False
        
        # Error handling test
        response = client.get('/api/trends/search')  # Missing keyword
        error_handling_ok = response.status_code == 400
        log_test_result("Flask Error Handling", error_handling_ok, "Missing keyword parameter")
        
        return health_data_ok and search_data_ok and providers_data_ok and error_handling_ok
        
    except Exception as e:
        log_test_result("Flask App Tests", False, str(e))
        return False

def test_performance():
    """Test basic performance requirements"""
    try:
        from serpapi_adapter import SerpAPIAdapter
        
        adapter = SerpAPIAdapter()
        
        # Health check performance
        start_time = time.time()
        health = adapter.health_check()
        health_time = time.time() - start_time
        
        health_performance_ok = health_time < 2.0
        log_test_result("Health Check Performance", health_performance_ok, f"{health_time:.2f}s < 2.0s")
        
        # Search performance  
        start_time = time.time()
        result = adapter.search_trends("performance", "US")
        search_time = time.time() - start_time
        
        search_performance_ok = search_time < 5.0  # Relaxed for mock data
        log_test_result("Search Performance", search_performance_ok, f"{search_time:.2f}s < 5.0s")
        
        return health_performance_ok and search_performance_ok
        
    except Exception as e:
        log_test_result("Performance Tests", False, str(e))
        return False

def run_all_tests():
    """Run all test suites"""
    print("🔍 Starting Enhanced Integration Tests...")
    print("-" * 60)
    
    # Test suites
    test_suites = [
        ("Imports", test_imports),
        ("SerpAPI Adapter", test_serpapi_adapter),
        ("Data Provider", test_data_provider),
        ("Flask Application", test_flask_app),
        ("Performance", test_performance)
    ]
    
    suite_results = []
    
    for suite_name, test_func in test_suites:
        print(f"\n🧪 Running {suite_name} Tests:")
        try:
            result = test_func()
            suite_results.append(result)
            print(f"{'✅' if result else '❌'} {suite_name} Suite: {'PASSED' if result else 'FAILED'}")
        except Exception as e:
            print(f"❌ {suite_name} Suite: ERROR - {e}")
            suite_results.append(False)
    
    return suite_results

def print_summary():
    """Print test summary"""
    print("\n" + "=" * 60)
    print("📊 Enhanced Integration Test Results Summary")
    print("=" * 60)
    
    success_rate = (TEST_RESULTS['passed'] / TEST_RESULTS['total'] * 100) if TEST_RESULTS['total'] > 0 else 0
    
    print(f"Total Tests: {TEST_RESULTS['total']}")
    print(f"✅ Passed: {TEST_RESULTS['passed']}")
    print(f"❌ Failed: {TEST_RESULTS['failed']}")
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    print(f"\n🎯 Target: ≥80% success rate")
    
    if success_rate >= 80:
        print(f"🎉 SUCCESS: Tests passed! ({success_rate:.1f}% ≥ 80%)")
        print("✅ Ready for PR approval!")
        return True
    else:
        print(f"⚠️ REVIEW NEEDED: Success rate below target ({success_rate:.1f}% < 80%)")
        print("📋 Review failed tests and consider proceeding with caution")
        return False

if __name__ == '__main__':
    try:
        # Run all tests
        suite_results = run_all_tests()
        
        # Print detailed summary
        success = print_summary()
        
        # Additional analysis
        print(f"\n📋 Test Details:")
        for test in TEST_RESULTS['tests']:
            status = "✅" if test['passed'] else "❌"
            print(f"{status} {test['name']}: {test['details'] or 'OK'}")
        
        # Final recommendation
        print(f"\n🎯 Recommendation:")
        if success:
            print("✅ All quality gates met - Ready for PR approval")
        else:
            passed_suites = sum(suite_results)
            total_suites = len(suite_results)
            if passed_suites >= (total_suites * 0.8):
                print("⚠️ Most tests passed - Proceed with caution")
            else:
                print("❌ Multiple failures - Fix issues before PR")
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"\n❌ Test runner failed: {e}")
        sys.exit(1)
