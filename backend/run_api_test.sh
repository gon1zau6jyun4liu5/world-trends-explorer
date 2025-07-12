#!/bin/bash

# Google Trends API 연결 테스트 스크립트

set -e

echo "🌍 Google Trends API 연결 테스트 시작"
echo "=================================="

# 현재 디렉토리 확인
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR"

echo "📁 Backend 디렉토리: $BACKEND_DIR"

# Python 가상환경 확인 및 생성
if [ ! -d "venv" ]; then
    echo "📦 Python 가상환경 생성 중..."
    python3 -m venv venv
fi

# 가상환경 활성화
echo "🔄 가상환경 활성화 중..."
source venv/bin/activate

# 종속성 설치
echo "📥 Python 종속성 설치 중..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# 추가 테스트 종속성 설치
echo "📥 테스트 종속성 설치 중..."
pip install -q requests

echo ""
echo "🧪 API 연결 테스트 옵션:"
echo "1. 종합 테스트 (comprehensive)"
echo "2. 유닛 테스트 (unit)"
echo "3. 빠른 테스트 (quick)"
echo ""

# 테스트 타입 선택
TEST_TYPE=${1:-"comprehensive"}

case $TEST_TYPE in
    "comprehensive"|"comp"|"c")
        echo "🚀 종합 API 연결 테스트 실행..."
        python3 test_api_connection.py
        ;;
    "unit"|"u")
        echo "🧪 유닛 테스트 실행..."
        python3 test_api_unit.py
        ;;
    "quick"|"q")
        echo "⚡ 빠른 API 연결 테스트..."
        python3 -c "
from test_api_connection import GoogleTrendsAPITester
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

tester = GoogleTrendsAPITester()
print('🔄 API 연결 테스트 중...')

if tester.initialize_connection():
    print('✅ Google Trends API 연결 성공!')
    
    # 간단한 검색 테스트
    if tester.test_search_functionality():
        print('✅ 검색 기능 정상 작동!')
    else:
        print('❌ 검색 기능 문제 발생')
        
    # 트렌딩 검색어 테스트
    if tester.test_trending_searches():
        print('✅ 트렌딩 검색어 기능 정상!')
    else:
        print('❌ 트렌딩 검색어 기능 문제')
        
    print('🎉 빠른 테스트 완료 - API 연결 정상!')
else:
    print('❌ Google Trends API 연결 실패!')
    print('💡 네트워크 연결 또는 API 제한 사항을 확인해주세요.')
    exit(1)
"
        ;;
    "both"|"all")
        echo "🎯 모든 테스트 실행..."
        echo ""
        echo "1️⃣ 종합 테스트 실행..."
        python3 test_api_connection.py
        echo ""
        echo "2️⃣ 유닛 테스트 실행..."
        python3 test_api_unit.py
        ;;
    *)
        echo "❌ 알 수 없는 테스트 타입: $TEST_TYPE"
        echo "사용법: $0 [comprehensive|unit|quick|all]"
        exit 1
        ;;
esac

echo ""
echo "📊 테스트 결과 파일:"
if [ -f "api_test_report.json" ]; then
    echo "  - api_test_report.json (상세 리포트)"
fi

echo ""
echo "✅ API 연결 테스트 완료!"
echo ""
echo "💡 문제가 발생한 경우:"
echo "  1. 인터넷 연결 상태 확인"
echo "  2. 방화벽 설정 확인"
echo "  3. Google Trends 서비스 상태 확인"
echo "  4. 너무 많은 요청으로 인한 일시적 제한 가능성"
echo ""
echo "🔧 디버깅을 위해 다음 명령어로 자세한 로그 확인:"
echo "  python3 test_api_connection.py 2>&1 | tee api_test.log"
