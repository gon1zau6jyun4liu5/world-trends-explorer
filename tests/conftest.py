# tests/conftest.py - Pytest Configuration

import pytest
import os
import sys

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

@pytest.fixture(scope="session")
def test_config():
    """Test configuration fixture"""
    return {
        'TESTING': True,
        'API_BASE_URL': 'http://localhost:5555/api/trends',
        'MOCK_DATA_DIR': os.path.join(os.path.dirname(__file__), 'fixtures'),
        'TIMEOUT': 10
    }

@pytest.fixture
def sample_trends_data():
    """Sample trends data for testing"""
    return {
        'keyword': 'test keyword',
        'geo': 'US',
        'timeframe': 'today 12-m',
        'timestamp': '2025-07-13T10:00:00Z',
        'interest_over_time': [
            {'date': '2025-01-01T00:00:00Z', 'value': 50},
            {'date': '2025-02-01T00:00:00Z', 'value': 75},
            {'date': '2025-03-01T00:00:00Z', 'value': 40}
        ],
        'interest_by_region': [
            {'geoName': 'United States', 'geoCode': 'US', 'value': 100},
            {'geoName': 'Canada', 'geoCode': 'CA', 'value': 75},
            {'geoName': 'United Kingdom', 'geoCode': 'GB', 'value': 60}
        ],
        'related_queries': {
            'top': [
                {'query': 'related query 1', 'value': '100'},
                {'query': 'related query 2', 'value': '50'}
            ],
            'rising': [
                {'query': 'rising query 1', 'value': 'Breakout'},
                {'query': 'rising query 2', 'value': '+300%'}
            ]
        }
    }