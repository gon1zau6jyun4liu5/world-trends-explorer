# tests/test_serpapi_integration.py - SerpAPI Integration Tests

import pytest
import json
from unittest.mock import patch, MagicMock
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Import the modules to test
try:
    from serpapi_adapter import SerpAPIAdapter, SerpAPIConfig
    from app_enhanced import app, TrendsDataProvider
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import modules: {e}")
    MODULES_AVAILABLE = False

@pytest.fixture
def client():
    """Test client for enhanced Flask app"""
    if not MODULES_AVAILABLE:
        pytest.skip("Required modules not available")
    
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_serpapi_response():
    """Mock SerpAPI response data"""
    return {
        'interest_over_time': {
            'timeline_data': [
                {
                    'date': '2025-01-01',
                    'values': [{'value': 50}]
                },
                {
                    'date': '2025-02-01',
                    'values': [{'value': 75}]
                }
            ]
        },
        'interest_by_region': {
            'geoMapData': [
                {
                    'geoName': 'United States',
                    'geoCode': 'US',
                    'value': [{'value': 100}]
                },
                {
                    'geoName': 'Germany',
                    'geoCode': 'DE',
                    'value': [{'value': 75}]
                }
            ]
        },
        'related_queries': {
            'top': [
                {'query': 'test query 1', 'value': 100},
                {'query': 'test query 2', 'value': 50}
            ],
            'rising': [
                {'query': 'rising query 1', 'value': 'Breakout'},
                {'query': 'rising query 2', 'value': '+300%'}
            ]
        }
    }

@pytest.mark.skipif(not MODULES_AVAILABLE, reason="Required modules not available")
class TestSerpAPIAdapter:
    """Test SerpAPI adapter functionality"""
    
    def test_adapter_initialization(self):
        """Test SerpAPI adapter initialization"""
        adapter = SerpAPIAdapter()
        assert adapter is not None
        assert hasattr(adapter, 'config')
        assert hasattr(adapter, 'country_mapping')
    
    def test_mock_mode_initialization(self):
        """Test adapter initialization in mock mode"""
        adapter = SerpAPIAdapter(api_key=None)
        assert adapter.mock_mode is True
        
        health = adapter.health_check()
        assert health['status'] == 'healthy'
        assert 'Mock' in health['data_source']
    
    def test_config_initialization(self):
        """Test SerpAPI config creation"""
        config = SerpAPIConfig(api_key="test_key")
        assert config.api_key == "test_key"
        assert config.base_url == "https://serpapi.com/search"
        assert config.timeout == 30
    
    @patch('requests.get')
    def test_real_api_request(self, mock_get, mock_serpapi_response):
        """Test real API request (mocked)"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_serpapi_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        adapter = SerpAPIAdapter(api_key="test_key")
        adapter.mock_mode = False  # Force real API mode
        
        result = adapter.search_trends("test keyword", "US")
        
        assert result['keyword'] == "test keyword"
        assert result['geo'] == "US"
        assert result['data_source'] == 'SerpAPI'
        assert len(result['interest_over_time']) == 2
        assert len(result['interest_by_region']) == 2
    
    def test_mock_search_trends(self):
        """Test search trends in mock mode"""
        adapter = SerpAPIAdapter()  # No API key = mock mode
        
        result = adapter.search_trends("artificial intelligence", "US")
        
        assert result['keyword'] == "artificial intelligence"
        assert result['geo'] == "US"
        assert 'interest_over_time' in result
        assert 'interest_by_region' in result
        assert 'related_queries' in result
        assert len(result['interest_over_time']) > 0
    
    def test_mock_trending_searches(self):
        """Test trending searches in mock mode"""
        adapter = SerpAPIAdapter()
        
        result = adapter.get_trending_searches("US")
        
        assert result['geo'] == "US"
        assert 'trending_searches' in result
        assert len(result['trending_searches']) > 0
        assert result['trending_searches'][0]['query'] is not None
    
    def test_mock_suggestions(self):
        """Test suggestions in mock mode"""
        adapter = SerpAPIAdapter()
        
        result = adapter.get_suggestions("AI")
        
        assert result['keyword'] == "AI"
        assert 'suggestions' in result
        assert len(result['suggestions']) > 0
    
    def test_timeframe_conversion(self):
        """Test timeframe conversion"""
        adapter = SerpAPIAdapter()
        
        # Test standard conversions
        assert adapter._convert_timeframe('today 12-m') == 'today 12-m'
        assert adapter._convert_timeframe('now 1-d') == 'now 1-d'
        assert adapter._convert_timeframe('unknown') == 'today 12-m'  # Default
    
    def test_country_mapping(self):
        """Test country code mapping"""
        adapter = SerpAPIAdapter()
        
        assert 'US' in adapter.country_mapping
        assert adapter.country_mapping['US'] == 'United States'
        assert 'GB' in adapter.country_mapping
        assert adapter.country_mapping['GB'] == 'United Kingdom'

@pytest.mark.skipif(not MODULES_AVAILABLE, reason="Required modules not available")
class TestTrendsDataProvider:
    """Test the unified data provider system"""
    
    def test_provider_initialization(self):
        """Test data provider initialization"""
        provider = TrendsDataProvider()
        assert provider is not None
        assert len(provider.providers) > 0
        assert provider.active_provider is not None
    
    def test_provider_switching(self):
        """Test provider switching functionality"""
        provider = TrendsDataProvider()
        
        # Get available providers
        provider_names = [name for name, _ in provider.providers]
        
        if len(provider_names) > 1:
            original_provider = provider.active_provider[0]
            
            # Switch to different provider
            for name in provider_names:
                if name != original_provider:
                    success = provider.switch_provider(name)
                    assert success is True
                    assert provider.active_provider[0] == name
                    break
    
    def test_provider_status(self):
        """Test provider status reporting"""
        provider = TrendsDataProvider()
        
        status = provider.get_provider_status()
        assert isinstance(status, dict)
        assert len(status) > 0
        
        # Check that each provider has a status
        for provider_name, provider_status in status.items():
            assert 'status' in provider_status
            assert provider_status['status'] in ['healthy', 'degraded', 'unhealthy', 'error']
    
    def test_mock_provider_functionality(self):
        """Test mock provider functionality"""
        provider = TrendsDataProvider()
        
        # Get mock provider
        mock_provider = provider.get_provider('Mock')
        assert mock_provider is not None
        
        # Test search
        result = mock_provider.search_trends("test", "US")
        assert result['keyword'] == "test"
        assert 'interest_over_time' in result
        
        # Test trending
        trending = mock_provider.get_trending_searches("US")
        assert 'trending_searches' in trending
        
        # Test suggestions
        suggestions = mock_provider.get_suggestions("test")
        assert 'suggestions' in suggestions

@pytest.mark.skipif(not MODULES_AVAILABLE, reason="Required modules not available")
class TestEnhancedAPIEndpoints:
    """Test enhanced API endpoints"""
    
    def test_health_endpoint_enhanced(self, client):
        """Test enhanced health endpoint"""
        response = client.get('/api/trends/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'status' in data
        assert 'active_provider' in data
        assert 'providers' in data
        assert 'version' in data
        assert data['version'] == '1.1.0'
        assert 'features' in data
    
    def test_providers_endpoint(self, client):
        """Test providers information endpoint"""
        response = client.get('/api/trends/providers')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'active_provider' in data
        assert 'providers' in data
        assert 'api_version' in data
        assert data['api_version'] == '1.1.0'
    
    def test_search_endpoint_enhanced(self, client):
        """Test enhanced search endpoint"""
        response = client.get('/api/trends/search?keyword=artificial intelligence')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['keyword'] == 'artificial intelligence'
        assert 'api_version' in data
        assert 'provider_used' in data
        assert data['api_version'] == '1.1.0'
    
    def test_trending_endpoint_enhanced(self, client):
        """Test enhanced trending endpoint"""
        response = client.get('/api/trends/trending?geo=US')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['geo'] == 'US'
        assert 'api_version' in data
        assert 'provider_used' in data
        assert data['api_version'] == '1.1.0'
    
    def test_suggestions_endpoint_enhanced(self, client):
        """Test enhanced suggestions endpoint"""
        response = client.get('/api/trends/suggestions?keyword=AI')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['keyword'] == 'AI'
        assert 'api_version' in data
        assert 'provider_used' in data
    
    def test_provider_switching_endpoint(self, client):
        """Test provider switching endpoint"""
        # Try to switch to Mock provider
        response = client.post('/api/trends/switch-provider', 
                             json={'provider': 'Mock'})
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'Mock' in data['active_provider']
    
    def test_compare_endpoint_enhanced(self, client):
        """Test enhanced compare endpoint"""
        response = client.post('/api/trends/compare', 
                             json={
                                 'keywords': ['AI', 'Machine Learning'],
                                 'geo': 'US'
                             })
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['keywords'] == ['AI', 'Machine Learning']
        assert 'api_version' in data
        assert 'provider_used' in data
        assert len(data['comparison_data']) == 2

@pytest.mark.skipif(not MODULES_AVAILABLE, reason="Required modules not available")
class TestErrorHandling:
    """Test error handling in enhanced system"""
    
    def test_invalid_provider_switch(self, client):
        """Test switching to invalid provider"""
        response = client.post('/api/trends/switch-provider', 
                             json={'provider': 'NonExistentProvider'})
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data
        assert 'available_providers' in data
    
    def test_missing_keyword_enhanced(self, client):
        """Test missing keyword parameter"""
        response = client.get('/api/trends/search')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Keyword parameter is required' in data['error']
    
    def test_invalid_compare_request(self, client):
        """Test invalid compare request"""
        # Too few keywords
        response = client.post('/api/trends/compare', 
                             json={'keywords': ['AI']})
        assert response.status_code == 400
        
        # Too many keywords
        response = client.post('/api/trends/compare', 
                             json={'keywords': ['AI', 'ML', 'DL', 'NLP', 'CV', 'RL']})
        assert response.status_code == 400

@pytest.mark.skipif(not MODULES_AVAILABLE, reason="Required modules not available")
class TestDataFormatCompatibility:
    """Test data format compatibility between providers"""
    
    def test_serpapi_format_compatibility(self):
        """Test SerpAPI data format matches expected structure"""
        adapter = SerpAPIAdapter()  # Mock mode
        
        result = adapter.search_trends("test", "US")
        
        # Check required fields
        required_fields = [
            'keyword', 'geo', 'timeframe', 'timestamp',
            'interest_over_time', 'interest_by_region', 'related_queries'
        ]
        
        for field in required_fields:
            assert field in result
        
        # Check data structure
        if result['interest_over_time']:
            time_item = result['interest_over_time'][0]
            assert 'date' in time_item
            assert 'value' in time_item
        
        if result['interest_by_region']:
            region_item = result['interest_by_region'][0]
            assert 'geoName' in region_item
            assert 'geoCode' in region_item
            assert 'value' in region_item
        
        # Check related queries structure
        assert 'top' in result['related_queries']
        assert 'rising' in result['related_queries']
    
    def test_cross_provider_consistency(self):
        """Test that different providers return consistent data structure"""
        provider = TrendsDataProvider()
        
        # Test with different providers
        for provider_name, provider_instance in provider.providers:
            result = provider_instance.search_trends("test", "US")
            
            # All providers should return these fields
            assert 'keyword' in result
            assert 'interest_over_time' in result
            assert 'interest_by_region' in result
            assert isinstance(result['interest_over_time'], list)
            assert isinstance(result['interest_by_region'], list)

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
