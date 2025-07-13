# World Trends Explorer - Test Directory

This directory contains test files for the World Trends Explorer project.

## Test Files

- `test_serpapi_integration.py` - Comprehensive SerpAPI integration tests
- `test_results_*.log` - Test execution logs (generated)

## Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python tests/test_serpapi_integration.py

# Run with the test script
./test_serpapi_integration.sh comprehensive
```

## Test Coverage

- SerpAPI adapter functionality
- Multi-provider data integration  
- Flask API endpoints
- Error handling and validation
- Performance and concurrent requests
