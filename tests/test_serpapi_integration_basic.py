#!/usr/bin/env python3
"""
SerpAPI Integration Tests for World Trends Explorer v1.1.0
"""

import unittest
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

print("🧪 SerpAPI Integration Test Suite v1.1.0")
print("=" * 50)

# Test imports
try:
    from serpapi_adapter import SerpAPIAdapter
    print("✅ SerpAPI adapter imported successfully")
except ImportError as e:
    print(f"❌ Failed to import SerpAPI adapter: {e}")
    sys.exit(1)

try:
    from app_enhanced import TrendsDataProvider
    print("✅ Enhanced app imported successfully")
except ImportError as e:
    print(f"❌ Failed to import enhanced app: {e}")
    sys.exit(1)

class TestSerpAPIAdapter(unittest.TestCase):
    """Test SerpAPI adapter"""
    
    def setUp(self):
        self.adapter = SerpAPIAdapter()
    
    def test_health_check(self):
        """Test health check"""
        health = self.adapter.health_check()
        self.assertIsInstance(health, dict)
        self.assertIn('status', health)
        print(f"✅ Health check: {health['status']}")
    
    def test_search_trends(self):
        """Test search functionality"""
        result = self.adapter.search_trends("AI", "US")
        self.assertIsInstance(result, dict)
        self.assertIn('keyword', result)
        self.assertEqual(result['keyword'], "AI")
        print(f"✅ Search test: {result['keyword']}")
    
    def test_trending_searches(self):
        """Test trending searches"""
        result = self.adapter.get_trending_searches("US")
        self.assertIsInstance(result, dict)
        self.assertIn('trending_searches', result)
        print(f"✅ Trending test: {len(result['trending_searches'])} topics")

class TestTrendsDataProvider(unittest.TestCase):
    """Test data provider"""
    
    def setUp(self):
        self.provider = TrendsDataProvider()
    
    def test_initialization(self):
        """Test provider initialization"""
        self.assertIsNotNone(self.provider)
        self.assertGreater(len(self.provider.providers), 0)
        print(f"✅ Provider init: {len(self.provider.providers)} providers")
    
    def test_provider_switching(self):
        """Test provider switching"""
        success = self.provider.switch_provider('Mock')
        self.assertTrue(success)
        print("✅ Provider switching works")
    
    def test_provider_status(self):
        """Test provider status"""
        status = self.provider.get_provider_status()
        self.assertIsInstance(status, dict)
        print(f"✅ Provider status: {list(status.keys())}")

if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "=" * 50)
    print("🎉 SerpAPI Integration Tests Completed")
    print("Ready for comprehensive testing!")
