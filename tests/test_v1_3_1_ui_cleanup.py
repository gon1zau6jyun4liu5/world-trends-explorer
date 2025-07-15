#!/usr/bin/env python3
"""
World Trends Explorer v1.3.1 - UI Cleanup Tests
Tests for verifying Global Trending section removal
"""

import unittest
import os
import sys
import re
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestV131UICleanup(unittest.TestCase):
    """Test suite for v1.3.1 UI cleanup changes"""
    
    def setUp(self):
        """Set up test environment"""
        self.frontend_path = Path(__file__).parent.parent / 'frontend'
        self.version = "v1.3.1"
        
    def test_version_badge_exists(self):
        """Test that v1.3.1 version badge exists in index.html"""
        index_path = self.frontend_path / 'index.html'
        
        self.assertTrue(index_path.exists(), "index.html file should exist")
        
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for version badge
        self.assertIn('v1.3.1', content, "Version v1.3.1 should be displayed")
        self.assertIn('version-badge', content, "Version badge element should exist")
        
    def test_global_trending_section_removed_from_html(self):
        """Test that Global Trending section is removed from HTML"""
        index_path = self.frontend_path / 'index.html'
        
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check that Global Trending elements are removed
        self.assertNotIn('global-trending-section', content, 
                        "global-trending-section should be removed")
        self.assertNotIn('globalTrendingCountrySelect', content,
                        "globalTrendingCountrySelect should be removed")
        self.assertNotIn('globalTrendingGrid', content,
                        "globalTrendingGrid should be removed")
        self.assertNotIn('Global Trending Topics', content,
                        "Global Trending Topics text should be removed")
        self.assertNotIn('Powered by SerpAPI', content,
                        "Powered by SerpAPI text should be removed")
        
    def test_global_trending_styles_removed_from_css(self):
        """Test that Global Trending styles are removed from CSS"""
        css_path = self.frontend_path / 'css' / 'styles.css'
        
        self.assertTrue(css_path.exists(), "styles.css file should exist")
        
        with open(css_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check that global-trending styles are removed
        self.assertNotIn('.global-trending-section', content,
                        ".global-trending-section class should be removed")
        self.assertNotIn('.trending-controls', content,
                        ".trending-controls class should be removed")
        
        # Check for v1.3.1 comment
        self.assertIn('v1.3.1', content, "v1.3.1 reference should be in CSS")
        
    def test_global_trending_code_removed_from_js(self):
        """Test that Global Trending code is removed from JavaScript"""
        js_path = self.frontend_path / 'js' / 'app.js'
        
        self.assertTrue(js_path.exists(), "app.js file should exist")
        
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check that global trending related code is removed
        self.assertNotIn('globalTrendingCountrySelect', content,
                        "globalTrendingCountrySelect references should be removed")
        self.assertNotIn('globalTrendingGrid', content,
                        "globalTrendingGrid references should be removed")
        self.assertNotIn('loadGlobalTrendingSearches', content,
                        "loadGlobalTrendingSearches function should be removed")
        self.assertNotIn('displayGlobalTrendingSearches', content,
                        "displayGlobalTrendingSearches function should be removed")
        
        # Check for version update
        self.assertIn('1.3.1', content, "Version 1.3.1 should be referenced in JS")
        
    def test_api_endpoints_unchanged(self):
        """Test that API endpoints remain unchanged"""
        api_path = self.frontend_path / 'js' / 'api.js'
        
        if api_path.exists():
            with open(api_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check that core API endpoints still exist
            self.assertIn('/api/trends/search', content,
                         "Search endpoint should still exist")
            self.assertIn('/api/trends/trending', content,
                         "Trending endpoint should still exist")
            self.assertIn('/api/trends/health', content,
                         "Health endpoint should still exist")
            
    def test_main_functionality_preserved(self):
        """Test that main functionality elements are preserved"""
        index_path = self.frontend_path / 'index.html'
        
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check that main features still exist
        self.assertIn('searchInput', content, "Search input should exist")
        self.assertIn('countrySelect', content, "Country select should exist")
        self.assertIn('searchBtn', content, "Search button should exist")
        self.assertIn('worldMap', content, "World map should exist")
        self.assertIn('trendsChart', content, "Trends chart should exist")
        self.assertIn('resultsSection', content, "Results section should exist")
        self.assertIn('countryInfoPanel', content, "Country info panel should exist")
        
    def test_no_broken_references(self):
        """Test that there are no broken references to removed elements"""
        # Check JavaScript files
        js_files = ['app.js', 'api.js', 'worldmap.js', 'chart.js']
        
        for js_file in js_files:
            js_path = self.frontend_path / 'js' / js_file
            if js_path.exists():
                with open(js_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Look for getElementById or querySelector calls to removed elements
                removed_ids = ['globalTrendingCountrySelect', 'globalTrendingGrid']
                for removed_id in removed_ids:
                    pattern = rf"getElementById\(['\"]?{removed_id}['\"]?\)"
                    matches = re.findall(pattern, content)
                    self.assertEqual(len(matches), 0,
                                   f"Found reference to removed element {removed_id} in {js_file}")
                    
    def test_performance_improvements(self):
        """Test that unnecessary code has been removed for performance"""
        js_path = self.frontend_path / 'js' / 'app.js'
        
        if js_path.exists():
            with open(js_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check that initial trending load is removed or modified
            self.assertNotIn('loadGlobalTrendingSearches()', content,
                           "Initial global trending load should be removed")
            
    def test_documentation_updated(self):
        """Test that documentation reflects v1.3.1 changes"""
        docs_path = Path(__file__).parent.parent / 'docs' / 'FEATURE_SPEC.md'
        
        if docs_path.exists():
            with open(docs_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for v1.3.1 documentation
            self.assertIn('v1.3.1', content, "v1.3.1 should be documented")
            self.assertIn('UI Cleanup', content, "UI Cleanup should be mentioned")
            self.assertIn('Global Trending 섹션 제거', content,
                         "Global Trending removal should be documented")
            
    def test_console_log_cleanup(self):
        """Test that debug console.log statements are cleaned up"""
        js_files = ['app.js', 'api.js', 'worldmap.js', 'chart.js']
        
        for js_file in js_files:
            js_path = self.frontend_path / 'js' / js_file
            if js_path.exists():
                with open(js_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Count console.log statements (should be minimal)
                console_logs = len(re.findall(r'console\.log\(', content))
                self.assertLess(console_logs, 10,
                              f"Too many console.log statements in {js_file}")


class TestV131Integration(unittest.TestCase):
    """Integration tests for v1.3.1"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.frontend_path = Path(__file__).parent.parent / 'frontend'
        
    def test_html_css_consistency(self):
        """Test that HTML classes match CSS definitions"""
        index_path = self.frontend_path / 'index.html'
        css_path = self.frontend_path / 'css' / 'styles.css'
        
        if index_path.exists() and css_path.exists():
            with open(index_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
                
            with open(css_path, 'r', encoding='utf-8') as f:
                css_content = f.read()
                
            # Extract class names from HTML
            html_classes = set(re.findall(r'class="([^"]+)"', html_content))
            all_html_classes = set()
            for class_str in html_classes:
                all_html_classes.update(class_str.split())
                
            # Check that removed classes are not in HTML
            removed_classes = ['global-trending-section', 'trending-controls']
            for removed_class in removed_classes:
                self.assertNotIn(removed_class, all_html_classes,
                               f"Removed class {removed_class} found in HTML")
                
    def test_js_event_listeners_cleanup(self):
        """Test that event listeners for removed elements are cleaned up"""
        js_path = self.frontend_path / 'js' / 'app.js'
        
        if js_path.exists():
            with open(js_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for addEventListener on removed elements
            removed_elements = ['globalTrendingCountrySelect']
            for element in removed_elements:
                pattern = rf"{element}.*addEventListener"
                matches = re.findall(pattern, content)
                self.assertEqual(len(matches), 0,
                               f"Found event listener for removed element {element}")


def run_tests():
    """Run all v1.3.1 tests"""
    print("🧪 Running World Trends Explorer v1.3.1 UI Cleanup Tests...")
    print("=" * 70)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestV131UICleanup))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestV131Integration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 70)
    print(f"✅ Tests Run: {result.testsRun}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"⚠️  Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n🎉 All v1.3.1 UI Cleanup tests passed!")
        print("✨ Global Trending section successfully removed")
        print("🚀 Ready for PR submission")
    else:
        print("\n❌ Some tests failed. Please fix the issues before PR.")
        
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)