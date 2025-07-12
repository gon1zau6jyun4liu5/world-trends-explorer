#!/usr/bin/env python3
"""
Google Trends API 연결 상태 확인 및 검증
실제 API 연결 테스트를 수행합니다.
"""

import sys
import os
import subprocess
import importlib.util
from datetime import datetime

def check_dependencies():
    """필요한 Python 패키지 확인"""
    required_packages = [
        'pytrends',
        'pandas', 
        'requests',
        'flask'
    ]
    
    print("🔍 필수 패키지 확인 중...")
    
    missing_packages = []
    for package in required_packages:
        spec = importlib.util.find_spec(package)
        if spec is None:
            missing_packages.append(package)
        else:
            print(f"✅ {package} 설치됨")
    
    if missing_packages:
        print(f"❌ 누락된 패키지: {', '.join(missing_packages)}")
        print("다음 명령어로 설치하세요:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ 모든 필수 패키지가 설치되어 있습니다.")
    return True

def run_quick_api_test():
    """빠른 API 연결 테스트"""
    print("\n⚡ 빠른 Google Trends API 연결 테스트...")
    
    try:
        from pytrends.request import TrendReq
        
        # API 연결 초기화
        print("🔄 API 연결 초기화 중...")
        pytrends = TrendReq(hl='en-US', tz=360)
        
        # 간단한 테스트 검색
        print("🔍 테스트 검색 수행 중...")
        pytrends.build_payload(['python'], cat=0, timeframe='today 1-m', geo='US')
        
        # 데이터 조회
        interest_over_time = pytrends.interest_over_time()
        
        if not interest_over_time.empty:
            print(f"✅ API 연결 성공! 데이터 포인트: {len(interest_over_time)}개")
            print(f"   테스트 키워드: python")
            print(f"   데이터 범위: {interest_over_time.index.min()} ~ {interest_over_time.index.max()}")
            return True
        else:
            print("⚠️ API 연결은 되었으나 데이터가 없습니다.")
            return False
            
    except ImportError as e:
        print(f"❌ 패키지 임포트 실패: {e}")
        return False
    except Exception as e:
        print(f"❌ API 연결 실패: {e}")
        print("💡 가능한 원인:")
        print("  - 인터넷 연결 문제")
        print("  - Google Trends 서비스 일시 불가")
        print("  - 요청 빈도 제한")
        return False

def test_trending_searches():
    """트렌딩 검색어 테스트"""
    print("\n🔥 트렌딩 검색어 조회 테스트...")
    
    try:
        from pytrends.request import TrendReq
        
        pytrends = TrendReq(hl='en-US', tz=360)
        
        # 미국 트렌딩 검색어 조회
        trending_searches = pytrends.trending_searches(pn='US')
        
        if not trending_searches.empty:
            print(f"✅ 트렌딩 검색어 조회 성공! {len(trending_searches)}개 검색어")
            print("상위 5개 트렌딩 검색어:")
            for i, query in enumerate(trending_searches[0].head().values, 1):
                print(f"  {i}. {query}")
            return True
        else:
            print("⚠️ 트렌딩 검색어 데이터가 없습니다.")
            return False
            
    except Exception as e:
        print(f"❌ 트렌딩 검색어 조회 실패: {e}")
        return False

def test_regional_data():
    """지역별 데이터 테스트"""
    print("\n🌍 지역별 관심도 데이터 테스트...")
    
    try:
        from pytrends.request import TrendReq
        
        pytrends = TrendReq(hl='en-US', tz=360)
        pytrends.build_payload(['covid'], cat=0, timeframe='today 3-m', geo='')
        
        # 지역별 관심도 조회
        interest_by_region = pytrends.interest_by_region(resolution='COUNTRY', inc_geo_code=True)
        
        if not interest_by_region.empty:
            print(f"✅ 지역별 데이터 조회 성공! {len(interest_by_region)}개 국가")
            
            # 상위 5개 국가 표시
            top_regions = interest_by_region.sort_values('covid', ascending=False).head()
            print("상위 5개 국가:")
            for region, row in top_regions.iterrows():
                print(f"  {region}: {row['covid']}")
            return True
        else:
            print("⚠️ 지역별 데이터가 없습니다.")
            return False
            
    except Exception as e:
        print(f"❌ 지역별 데이터 조회 실패: {e}")
        return False

def main():
    """메인 API 연결 확인"""
    print("=" * 60)
    print("🌍 Google Trends API 연결 상태 확인")
    print(f"📅 테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 의존성 확인
    if not check_dependencies():
        print("\n💥 의존성 문제로 테스트를 중단합니다.")
        return False
    
    # 2. 빠른 API 테스트
    api_connection = run_quick_api_test()
    
    # 3. 추가 기능 테스트 (API 연결이 성공한 경우)
    trending_success = False
    regional_success = False
    
    if api_connection:
        trending_success = test_trending_searches()
        regional_success = test_regional_data()
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 API 연결 테스트 결과 요약")
    print("=" * 60)
    
    tests = [
        ("기본 API 연결", api_connection),
        ("트렌딩 검색어", trending_success),
        ("지역별 데이터", regional_success),
    ]
    
    passed = sum(1 for _, success in tests if success)
    total = len(tests)
    
    for test_name, success in tests:
        status = "✅ 성공" if success else "❌ 실패"
        print(f"{test_name}: {status}")
    
    print(f"\n📈 성공률: {passed}/{total} ({(passed/total)*100:.1f}%)")
    
    if passed >= 2:  # 기본 연결 + 1개 이상 추가 기능
        print("\n🎉 Google Trends API 연결이 정상적으로 작동합니다!")
        print("✅ 애플리케이션을 사용할 수 있습니다.")
        return True
    elif passed >= 1:  # 기본 연결만 성공
        print("\n⚠️ 기본 API 연결은 되지만 일부 기능에 제한이 있습니다.")
        print("💡 네트워크 상태나 API 제한 사항을 확인해주세요.")
        return True
    else:
        print("\n💥 Google Trends API 연결에 문제가 있습니다.")
        print("🔧 다음 사항을 확인해주세요:")
        print("  1. 인터넷 연결 상태")
        print("  2. 방화벽 설정")
        print("  3. VPN 또는 프록시 설정")
        print("  4. Google Trends 서비스 상태")
        return False

if __name__ == "__main__":
    try:
        success = main()
        
        print(f"\n📄 상세한 테스트를 원하시면 다음 명령어를 사용하세요:")
        print(f"  python test_api_connection.py")
        print(f"  python test_api_unit.py")
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⏹️ 테스트가 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 예상치 못한 오류: {e}")
        sys.exit(1)
