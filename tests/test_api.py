# tests/test_api.py - Backend API Unit Tests

import pytest
import json
from unittest.mock import patch, MagicMock
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import app
from mock_server import app as mock_app

@pytest.fixture
def client():
    """Test client for main Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_client():
    """Test client for mock server"""
    mock_app.config['TESTING'] = True
    with mock_app.test_client() as client:
        yield client

class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check_main_app(self, client):
        """Test health endpoint returns 200 and correct structure"""
        response = client.get('/api/trends/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'status' in data
        assert 'timestamp' in data
        assert 'service' in data
        assert data['status'] == 'healthy'
    
    def test_health_check_mock_app(self, mock_client):
        """Test mock server health endpoint"""
        response = mock_client.get('/api/trends/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'Mock Mode' in data['note']

class TestSearchEndpoint:
    """Test search trends endpoint"""
    
    def test_search_without_keyword(self, client):
        """Test search fails without keyword parameter"""
        response = client.get('/api/trends/search')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Keyword parameter is required' in data['error']
    
    def test_search_with_empty_keyword(self, client):
        """Test search fails with empty keyword"""
        response = client.get('/api/trends/search?keyword=')
        assert response.status_code == 400
    
    def test_mock_search_with_keyword(self, mock_client):
        """Test mock server returns proper search structure"""
        response = mock_client.get('/api/trends/search?keyword=artificial intelligence')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        required_fields = ['keyword', 'geo', 'timeframe', 'timestamp', 
                          'interest_over_time', 'interest_by_region', 'related_queries']
        
        for field in required_fields:
            assert field in data
        
        assert data['keyword'] == 'artificial intelligence'
        assert isinstance(data['interest_over_time'], list)
        assert isinstance(data['interest_by_region'], list)
    
    def test_mock_search_with_geo_parameter(self, mock_client):
        """Test search with geo parameter"""
        response = mock_client.get('/api/trends/search?keyword=bitcoin&geo=US')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['geo'] == 'US'

class TestTrendingEndpoint:
    """Test trending searches endpoint"""
    
    def test_mock_trending_default_country(self, mock_client):
        """Test trending searches with default country"""
        response = mock_client.get('/api/trends/trending')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'geo' in data
        assert 'trending_searches' in data
        assert isinstance(data['trending_searches'], list)
        
        if data['trending_searches']:
            first_item = data['trending_searches'][0]
            assert 'rank' in first_item
            assert 'query' in first_item
    
    def test_mock_trending_specific_country(self, mock_client):
        """Test trending searches for specific country"""
        response = mock_client.get('/api/trends/trending?geo=KR')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['geo'] == 'KR'

class TestCountriesEndpoint:
    """Test countries list endpoint"""
    
    def test_countries_list(self, mock_client):
        """Test countries endpoint returns proper structure"""
        response = mock_client.get('/api/trends/countries')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'countries' in data
        assert isinstance(data['countries'], list)
        
        if data['countries']:
            country = data['countries'][0]
            assert 'code' in country
            assert 'name' in country

class TestSuggestionsEndpoint:
    """Test keyword suggestions endpoint"""
    
    def test_suggestions_without_keyword(self, mock_client):
        """Test suggestions without keyword parameter"""
        response = mock_client.get('/api/trends/suggestions')
        assert response.status_code == 400
    
    def test_mock_suggestions_with_keyword(self, mock_client):
        """Test suggestions with keyword"""
        response = mock_client.get('/api/trends/suggestions?keyword=ai')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'keyword' in data
        assert 'suggestions' in data
        assert data['keyword'] == 'ai'

class TestErrorHandling:
    """Test error handling across endpoints"""
    
    def test_404_error(self, mock_client):
        """Test 404 error handling"""
        response = mock_client.get('/api/trends/nonexistent')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert 'error' in data

class TestDataValidation:
    """Test data validation and structure"""
    
    def test_mock_time_series_data_structure(self, mock_client):
        """Test time series data has correct structure"""
        response = mock_client.get('/api/trends/search?keyword=test')
        data = json.loads(response.data)
        
        time_series = data['interest_over_time']
        if time_series:
            item = time_series[0]
            assert 'date' in item
            assert 'value' in item
            assert isinstance(item['value'], int)
            assert 0 <= item['value'] <= 100
    
    def test_mock_regional_data_structure(self, mock_client):
        """Test regional data has correct structure"""
        response = mock_client.get('/api/trends/search?keyword=test')
        data = json.loads(response.data)
        
        regional_data = data['interest_by_region']
        if regional_data:
            item = regional_data[0]
            assert 'geoName' in item
            assert 'geoCode' in item
            assert 'value' in item
            assert isinstance(item['value'], int)
            assert 0 <= item['value'] <= 100
    
    def test_mock_related_queries_structure(self, mock_client):
        """Test related queries have correct structure"""
        response = mock_client.get('/api/trends/search?keyword=test')
        data = json.loads(response.data)
        
        related = data['related_queries']
        assert 'top' in related
        assert 'rising' in related
        assert isinstance(related['top'], list)
        assert isinstance(related['rising'], list)