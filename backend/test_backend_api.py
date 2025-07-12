#!/usr/bin/env python3
"""
Backend API Endpoint Tests
백엔드 API 엔드포인트 연결 및 기능 테스트
"""

import requests
import json
import time
import sys
from datetime import datetime
import unittest

class BackendAPITester:
    def __init__(self, base_url='http://localhost:5000'):
        """백엔드 API 테스터 초기화"""
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/api/trends"
        self.session = requests.Session()
        self.session.timeout = 30
        
    def test_health_endpoint(self):
        """헬스 체크 엔드포인트 테스트"""
        try:
            print("🔍 헬스 체크 엔드포인트 테스트...")
            response = self.session.get(f"{self.api_base}/health")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 헬스 체크 성공: {data.get('status', 'unknown')}")
                print(f"   서비스: {data.get('service', 'unknown')}")
                print(f"   타임스탬프: {data.get('timestamp', 'unknown')}")
                return True
            else:
                print(f"❌ 헬스 체크 실패: HTTP {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("❌ 백엔드 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
            return False
        except Exception as e:
            print(f"❌ 헬스 체크 오류: {e}")
            return False
    
    def test_search_endpoint(self, keyword="python", geo="US"):
        """검색 엔드포인트 테스트"""
        try:
            print(f"🔍 검색 엔드포인트 테스트 (키워드: '{keyword}', 지역: {geo})...")
            
            params = {
                'keyword': keyword,
                'geo': geo,
                'timeframe': 'today 3-m'
            }
            
            response = self.session.get(f"{self.api_base}/search", params=params)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 검색 성공")
                print(f"   키워드: {data.get('keyword', 'unknown')}")
                print(f"   지역: {data.get('geo', 'unknown')}")
                print(f"   시간대별 데이터: {len(data.get('interest_over_time', []))} 포인트")
                print(f"   지역별 데이터: {len(data.get('interest_by_region', []))} 지역")
                
                # 관련 검색어 확인
                related = data.get('related_queries', {})
                top_count = len(related.get('top', []))
                rising_count = len(related.get('rising', []))
                print(f"   관련 검색어: 상위 {top_count}개, 급상승 {rising_count}개")
                
                return True
            else:
                print(f"❌ 검색 실패: HTTP {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   오류 메시지: {error_data.get('error', 'unknown')}")
                except:
                    print(f"   응답 내용: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"❌ 검색 엔드포인트 오류: {e}")
            return False
    
    def test_trending_endpoint(self, geo="US"):
        """트렌딩 엔드포인트 테스트"""
        try:
            print(f"🔥 트렌딩 엔드포인트 테스트 (지역: {geo})...")
            
            params = {'geo': geo}
            response = self.session.get(f"{self.api_base}/trending", params=params)
            
            if response.status_code == 200:
                data = response.json()
                trending_searches = data.get('trending_searches', [])
                print(f"✅ 트렌딩 검색어 조회 성공")
                print(f"   지역: {data.get('country', geo)}")
                print(f"   트렌딩 검색어 수: {len(trending_searches)}")
                
                if trending_searches:
                    print("   상위 5개:")
                    for item in trending_searches[:5]:
                        rank = item.get('rank', '?')
                        query = item.get('query', 'unknown')
                        print(f"     {rank}. {query}")
                        
                return True
            else:
                print(f"❌ 트렌딩 조회 실패: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 트렌딩 엔드포인트 오류: {e}")
            return False
    
    def test_countries_endpoint(self):
        """국가 목록 엔드포인트 테스트"""
        try:
            print("🌍 국가 목록 엔드포인트 테스트...")
            
            response = self.session.get(f"{self.api_base}/countries")
            
            if response.status_code == 200:
                data = response.json()
                countries = data.get('countries', [])
                print(f"✅ 국가 목록 조회 성공")
                print(f"   지원 국가 수: {len(countries)}")
                
                if countries:
                    print("   예시 국가들:")
                    for country in countries[:5]:
                        code = country.get('code', '?')
                        name = country.get('name', 'unknown')
                        print(f"     {code}: {name}")
                        
                return True
            else:
                print(f"❌ 국가 목록 조회 실패: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 국가 목록 엔드포인트 오류: {e}")
            return False
    
    def test_suggestions_endpoint(self, keyword="artif"):
        """검색어 제안 엔드포인트 테스트"""
        try:
            print(f"💡 검색어 제안 엔드포인트 테스트 (키워드: '{keyword}')...")
            
            params = {'keyword': keyword}
            response = self.session.get(f"{self.api_base}/suggestions", params=params)
            
            if response.status_code == 200:
                data = response.json()
                suggestions = data.get('suggestions', [])
                print(f"✅ 검색어 제안 조회 성공")
                print(f"   제안 수: {len(suggestions)}")
                
                if suggestions:
                    print("   제안 예시:")
                    for suggestion in suggestions[:3]:
                        title = suggestion.get('title', 'unknown')
                        type_info = suggestion.get('type', '')
                        print(f"     - {title} ({type_info})")
                        
                return True
            else:
                print(f"❌ 검색어 제안 조회 실패: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 검색어 제안 엔드포인트 오류: {e}")
            return False
    
    def test_compare_endpoint(self):
        """비교 엔드포인트 테스트"""
        try:
            print("📊 키워드 비교 엔드포인트 테스트...")
            
            payload = {
                'keywords': ['python', 'java', 'javascript'],
                'geo': 'US',
                'timeframe': 'today 3-m'
            }
            
            response = self.session.post(
                f"{self.api_base}/compare",
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                comparison_data = data.get('comparison_data', [])
                print(f"✅ 키워드 비교 성공")
                print(f"   비교 키워드: {data.get('keywords', [])}")
                print(f"   비교 데이터 포인트: {len(comparison_data)}")
                
                return True
            else:
                print(f"❌ 키워드 비교 실패: HTTP {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   오류 메시지: {error_data.get('error', 'unknown')}")
                except:
                    pass
                return False
                
        except Exception as e:
            print(f"❌ 비교 엔드포인트 오류: {e}")
            return False
    
    def run_comprehensive_test(self):
        """종합 백엔드 API 테스트"""
        print("=" * 60)
        print("🚀 백엔드 API 종합 테스트 시작")
        print(f"🎯 대상 서버: {self.base_url}")
        print("=" * 60)
        
        tests = [
            ("헬스 체크", lambda: self.test_health_endpoint()),
            ("검색 기능", lambda: self.test_search_endpoint()),
            ("트렌딩 검색어", lambda: self.test_trending_endpoint()),
            ("국가 목록", lambda: self.test_countries_endpoint()),
            ("검색어 제안", lambda: self.test_suggestions_endpoint()),
            ("키워드 비교", lambda: self.test_compare_endpoint()),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n📋 {test_name} 테스트 중...")
            try:
                if test_func():
                    passed += 1
                    print(f"✅ {test_name} 테스트 통과")
                else:
                    print(f"❌ {test_name} 테스트 실패")
            except Exception as e:
                print(f"💥 {test_name} 테스트 오류: {e}")
            
            time.sleep(1)  # API 요청 간격
        
        # 결과 요약
        print("\n" + "=" * 60)
        print("📊 백엔드 API 테스트 결과")
        print("=" * 60)
        print(f"총 테스트: {total}")
        print(f"성공: {passed}")
        print(f"실패: {total - passed}")
        print(f"성공률: {(passed/total)*100:.1f}%")
        
        if passed >= total * 0.8:  # 80% 이상 성공
            print("\n🎉 백엔드 API 테스트 결과: 성공")
            return True
        else:
            print("\n💥 백엔드 API 테스트 결과: 실패")
            return False

def main():
    """메인 테스트 실행"""
    import argparse
    
    parser = argparse.ArgumentParser(description='백엔드 API 연결 테스트')
    parser.add_argument('--url', default='http://localhost:5000', 
                       help='백엔드 서버 URL (기본값: http://localhost:5000)')
    parser.add_argument('--endpoint', choices=['health', 'search', 'trending', 'countries', 'suggestions', 'compare'], 
                       help='특정 엔드포인트만 테스트')
    
    args = parser.parse_args()
    
    tester = BackendAPITester(args.url)
    
    if args.endpoint:
        # 특정 엔드포인트만 테스트
        test_methods = {
            'health': tester.test_health_endpoint,
            'search': tester.test_search_endpoint,
            'trending': tester.test_trending_endpoint,
            'countries': tester.test_countries_endpoint,
            'suggestions': tester.test_suggestions_endpoint,
            'compare': tester.test_compare_endpoint,
        }
        
        if args.endpoint in test_methods:
            print(f"🎯 {args.endpoint} 엔드포인트 테스트 중...")
            success = test_methods[args.endpoint]()
            sys.exit(0 if success else 1)
    else:
        # 종합 테스트
        success = tester.run_comprehensive_test()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ 테스트가 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 예상치 못한 오류 발생: {e}")
        sys.exit(1)
