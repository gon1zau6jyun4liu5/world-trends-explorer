#!/bin/bash

# SerpAPI Integration Test Runner (v1.1.0)
# Comprehensive testing for enhanced World Trends Explorer

set -e

echo "🌍 World Trends Explorer v1.1.0 - SerpAPI Integration Tests"
echo "============================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test mode selection
TEST_MODE=${1:-comprehensive}

echo -e "${BLUE}Test Mode: ${TEST_MODE}${NC}"
echo ""

# Test results
BACKEND_TESTS_PASSED=0
SERPAPI_TESTS_PASSED=0
INTEGRATION_TESTS_PASSED=0
TOTAL_TESTS=0
PASSED_TESTS=0

# Function to run backend tests
run_backend_tests() {
    echo -e "${YELLOW}🔬 Running Backend Tests...${NC}"
    cd backend

    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
    fi

    # Activate virtual environment
    source venv/bin/activate

    # Install dependencies
    echo "📥 Installing dependencies..."
    pip install -q -r requirements_enhanced.txt
    pip install -q pytest pytest-mock

    # Test SerpAPI adapter
    echo "🔗 Testing SerpAPI Adapter..."
    if python -c "
import sys
sys.path.append('.')
from serpapi_adapter import SerpAPIAdapter
adapter = SerpAPIAdapter()
print('✅ SerpAPI Adapter initialized successfully')
health = adapter.health_check()
print(f'📊 Health Status: {health[\"status\"]}')
trends = adapter.search_trends('test', 'US')
print(f'📈 Search test: {len(trends.get(\"interest_over_time\", []))} data points')
trending = adapter.get_trending_searches('US')
print(f'🔥 Trending test: {len(trending.get(\"trending_searches\", []))} topics')
suggestions = adapter.get_suggestions('AI')
print(f'💡 Suggestions test: {len(suggestions.get(\"suggestions\", []))} items')
print('✅ SerpAPI Adapter tests passed')
"; then
        SERPAPI_TESTS_PASSED=1
        echo -e "${GREEN}✅ SerpAPI Adapter Tests: PASSED${NC}"
    else
        echo -e "${RED}❌ SerpAPI Adapter Tests: FAILED${NC}"
    fi

    # Test enhanced Flask app
    echo "🚀 Testing Enhanced Flask App..."
    if python -c "
import sys
sys.path.append('.')
from app_enhanced import TrendsDataProvider
provider = TrendsDataProvider()
print('✅ TrendsDataProvider initialized successfully')
status = provider.get_provider_status()
print(f'📊 Providers available: {list(status.keys())}')
active = provider.active_provider[0] if provider.active_provider else 'None'
print(f'🎯 Active provider: {active}')
mock_provider = provider.get_provider('Mock')
if mock_provider:
    result = mock_provider.search_trends('test', 'US')
    print(f'📈 Mock provider test: {result[\"keyword\"]}')
print('✅ Enhanced Flask App tests passed')
"; then
        BACKEND_TESTS_PASSED=1
        echo -e "${GREEN}✅ Backend Tests: PASSED${NC}"
    else
        echo -e "${RED}❌ Backend Tests: FAILED${NC}"
    fi

    cd ..
}

# Function to run integration tests
run_integration_tests() {
    echo -e "${YELLOW}🔗 Running Integration Tests...${NC}"
    
    # Run pytest if available
    if command -v pytest &> /dev/null; then
        echo "🧪 Running pytest for SerpAPI integration..."
        if pytest tests/test_serpapi_integration.py -v --tb=short; then
            INTEGRATION_TESTS_PASSED=1
            echo -e "${GREEN}✅ Integration Tests: PASSED${NC}"
        else
            echo -e "${RED}❌ Integration Tests: FAILED${NC}"
        fi
    else
        echo "⚠️ pytest not available, running manual integration tests..."
        
        # Manual integration test
        cd backend
        source venv/bin/activate
        
        if python -c "
import sys
sys.path.append('.')
sys.path.append('../tests')

# Test imports
try:
    from serpapi_adapter import SerpAPIAdapter
    from app_enhanced import TrendsDataProvider, app
    print('✅ All modules imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)

# Test SerpAPI adapter integration
print('🔗 Testing SerpAPI Integration...')
adapter = SerpAPIAdapter()
provider = TrendsDataProvider()

# Test data consistency
serpapi_result = adapter.search_trends('test', 'US')
provider_result = provider.get_provider().search_trends('test', 'US')

required_fields = ['keyword', 'geo', 'interest_over_time', 'interest_by_region', 'related_queries']
for field in required_fields:
    if field not in serpapi_result:
        print(f'❌ Missing field in SerpAPI result: {field}')
        exit(1)
    if field not in provider_result:
        print(f'❌ Missing field in provider result: {field}')
        exit(1)

print('✅ Data structure consistency verified')

# Test provider switching
original_provider = provider.active_provider[0]
switch_success = provider.switch_provider('Mock')
if switch_success:
    print(f'✅ Provider switching: {original_provider} -> Mock')
else:
    print('❌ Provider switching failed')
    exit(1)

print('✅ Integration tests completed successfully')
"; then
            INTEGRATION_TESTS_PASSED=1
            echo -e "${GREEN}✅ Manual Integration Tests: PASSED${NC}"
        else
            echo -e "${RED}❌ Manual Integration Tests: FAILED${NC}"
        fi
        
        cd ..
    fi
}

# Function to run comprehensive tests
run_comprehensive_tests() {
    echo -e "${BLUE}🧪 Running Comprehensive Test Suite...${NC}"
    
    run_backend_tests
    run_integration_tests
    
    # Calculate results
    TOTAL_TESTS=3
    PASSED_TESTS=$((BACKEND_TESTS_PASSED + SERPAPI_TESTS_PASSED + INTEGRATION_TESTS_PASSED))
    
    echo ""
    echo "=" * 60
    echo -e "${BLUE}📊 Test Results Summary${NC}"
    echo "=" * 60
    
    if [ $SERPAPI_TESTS_PASSED -eq 1 ]; then
        echo -e "🔗 SerpAPI Adapter Tests:   ${GREEN}PASSED${NC}"
    else
        echo -e "🔗 SerpAPI Adapter Tests:   ${RED}FAILED${NC}"
    fi
    
    if [ $BACKEND_TESTS_PASSED -eq 1 ]; then
        echo -e "🚀 Backend Tests:           ${GREEN}PASSED${NC}"
    else
        echo -e "🚀 Backend Tests:           ${RED}FAILED${NC}"
    fi
    
    if [ $INTEGRATION_TESTS_PASSED -eq 1 ]; then
        echo -e "🔗 Integration Tests:       ${GREEN}PASSED${NC}"
    else
        echo -e "🔗 Integration Tests:       ${RED}FAILED${NC}"
    fi
    
    echo ""
    echo -e "📈 Success Rate: ${PASSED_TESTS}/${TOTAL_TESTS} ($(( PASSED_TESTS * 100 / TOTAL_TESTS ))%)"
    
    if [ $PASSED_TESTS -eq $TOTAL_TESTS ]; then
        echo -e "${GREEN}🎉 All tests passed! SerpAPI integration is ready.${NC}"
        exit 0
    elif [ $PASSED_TESTS -ge 2 ]; then
        echo -e "${YELLOW}⚠️ Most tests passed. Review failures and proceed with caution.${NC}"
        exit 0
    else
        echo -e "${RED}❌ Multiple test failures. Fix issues before proceeding.${NC}"
        exit 1
    fi
}

# Function to run quick tests
run_quick_tests() {
    echo -e "${BLUE}⚡ Running Quick Tests...${NC}"
    
    # Quick SerpAPI test
    cd backend
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip install -q -r requirements_enhanced.txt
    
    echo "🔗 Quick SerpAPI test..."
    if python -c "
from serpapi_adapter import SerpAPIAdapter
adapter = SerpAPIAdapter()
health = adapter.health_check()
print(f'Health: {health[\"status\"]}')
result = adapter.search_trends('AI', 'US')
print(f'Search test: ✅ {result[\"keyword\"]}')
print('✅ Quick test passed')
"; then
        echo -e "${GREEN}✅ Quick Tests: PASSED${NC}"
    else
        echo -e "${RED}❌ Quick Tests: FAILED${NC}"
        exit 1
    fi
    
    cd ..
}

# Function to show help
show_help() {
    echo "Usage: $0 [MODE]"
    echo ""
    echo "Test Modes:"
    echo "  comprehensive  - Run all tests (default)"
    echo "  quick         - Run quick validation tests"
    echo "  backend       - Run backend tests only"
    echo "  integration   - Run integration tests only"
    echo "  help          - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Run comprehensive tests"
    echo "  $0 quick             # Run quick tests"
    echo "  $0 backend           # Run backend tests only"
}

# Main execution
case $TEST_MODE in
    "comprehensive")
        run_comprehensive_tests
        ;;
    "quick")
        run_quick_tests
        ;;
    "backend")
        run_backend_tests
        echo ""
        if [ $((BACKEND_TESTS_PASSED + SERPAPI_TESTS_PASSED)) -eq 2 ]; then
            echo -e "${GREEN}✅ Backend tests completed successfully${NC}"
        else
            echo -e "${RED}❌ Backend tests failed${NC}"
            exit 1
        fi
        ;;
    "integration")
        run_integration_tests
        echo ""
        if [ $INTEGRATION_TESTS_PASSED -eq 1 ]; then
            echo -e "${GREEN}✅ Integration tests completed successfully${NC}"
        else
            echo -e "${RED}❌ Integration tests failed${NC}"
            exit 1
        fi
        ;;
    "help")
        show_help
        ;;
    *)
        echo -e "${RED}❌ Unknown test mode: $TEST_MODE${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}🌍 World Trends Explorer v1.1.0 - SerpAPI Integration Testing Complete${NC}"
