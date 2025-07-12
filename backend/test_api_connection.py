#!/usr/bin/env python3
"""
Google Trends API Connection Test Script
구글 트렌드 API 연결 상태 및 데이터 취득 테스트
"""

import pytrends
from pytrends.request import TrendReq
import pandas as pd
import logging
import time
import sys
from datetime import datetime, timedelta
import requests

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GoogleTrendsAPITester:
    def __init__(self):
        """Google Trends API 테스터 초기화"""
        self.pytrends = None
        self.test_results = {
            'connection': False,
            'search': False,
            'regional': False,
            'trending': False,
            'related_queries': False,
            'errors': []
        }
        
    def initialize_connection(self):
        """Pytrends 연결 초기화"""
        try:
            logger.info("🔄 Google Trends API 연결 초기화 중...")
            
            # 다양한 설정으로 초기화 시도
            configs = [
                {'hl': 'en-US', 'tz': 360},
                {'hl': 'ko-KR', 'tz': 540},
                {'hl': 'en-US', 'tz': 360, 'timeout': (20, 25)},
            ]
            
            for i, config in enumerate(configs):
                try:
                    logger.info(f"설정 {i+1} 시도: {config}")
                    self.pytrends = TrendReq(**config)
                    
                    # 간단한 테스트 쿼리로 연결 확인
                    self.pytrends.build_payload(['python'], cat=0, timeframe='today 1-m', geo='US')
                    test_data = self.pytrends.interest_over_time()
                    
                    logger.info("✅ Google Trends API 연결 성공!")
                    self.test_results['connection'] = True
                    return True
                    
                except Exception as e:
                    logger.warning(f"설정 {i+1} 실패: {str(e)}")
                    if i == len(configs) - 1:
                        raise e
                    time.sleep(2)
                    
        except Exception as e:
            error_msg = f"Google Trends API 연결 실패: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.test_results['errors'].append(error_msg)
            return False

    def test_search_functionality(self):
        """검색 기능 테스트"""
        try:
            logger.info("🔍 검색 기능 테스트 중...")
            
            test_keywords = ['python', 'artificial intelligence', 'olympics']
            
            for keyword in test_keywords:
                logger.info(f"키워드 테스트: '{keyword}'")
                
                # 페이로드 빌드
                self.pytrends.build_payload([keyword], cat=0, timeframe='today 3-m', geo='US')
                
                # 시간대별 관심도 데이터
                interest_over_time = self.pytrends.interest_over_time()
                
                if not interest_over_time.empty:
                    logger.info(f"✅ '{keyword}' 시간대별 데이터: {len(interest_over_time)} 포인트")
                    logger.info(f"   데이터 범위: {interest_over_time.index.min()} ~ {interest_over_time.index.max()}")
                    logger.info(f"   평균 관심도: {interest_over_time[keyword].mean():.2f}")
                else:
                    logger.warning(f"⚠️ '{keyword}' 시간대별 데이터 없음")
                
                time.sleep(1)  # API 레이트 리미트 방지
                
            self.test_results['search'] = True
            logger.info("✅ 검색 기능 테스트 성공")
            return True
            
        except Exception as e:
            error_msg = f"검색 기능 테스트 실패: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.test_results['errors'].append(error_msg)
            return False

    def test_regional_data(self):
        """지역별 데이터 테스트"""
        try:
            logger.info("🌍 지역별 데이터 테스트 중...")
            
            # 인기 키워드로 테스트
            self.pytrends.build_payload(['covid'], cat=0, timeframe='today 3-m', geo='')
            
            # 지역별 관심도
            interest_by_region = self.pytrends.interest_by_region(resolution='COUNTRY', inc_low_vol=True, inc_geo_code=True)
            
            if not interest_by_region.empty:
                logger.info(f"✅ 지역별 데이터: {len(interest_by_region)} 국가")
                
                # 상위 10개 국가 표시
                top_regions = interest_by_region.sort_values('covid', ascending=False).head(10)
                logger.info("상위 10개 국가:")
                for idx, (region, row) in enumerate(top_regions.iterrows(), 1):
                    logger.info(f"   {idx}. {region}: {row['covid']}")
                    
                self.test_results['regional'] = True
                return True
            else:
                logger.warning("⚠️ 지역별 데이터 없음")
                return False
                
        except Exception as e:
            error_msg = f"지역별 데이터 테스트 실패: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.test_results['errors'].append(error_msg)
            return False

    def test_trending_searches(self):
        """트렌딩 검색어 테스트"""
        try:
            logger.info("🔥 트렌딩 검색어 테스트 중...")
            
            test_countries = ['US', 'KR', 'JP', 'GB']
            
            for country in test_countries:
                try:
                    logger.info(f"국가별 트렌딩 테스트: {country}")
                    
                    trending_searches = self.pytrends.trending_searches(pn=country)
                    
                    if not trending_searches.empty:
                        logger.info(f"✅ {country} 트렌딩 검색어: {len(trending_searches)} 개")
                        logger.info(f"   상위 5개: {trending_searches[0].head().tolist()}")
                    else:
                        logger.warning(f"⚠️ {country} 트렌딩 데이터 없음")
                        
                    time.sleep(2)  # API 레이트 리미트 방지
                    
                except Exception as e:
                    logger.warning(f"⚠️ {country} 트렌딩 검색어 실패: {str(e)}")
                    continue
                    
            self.test_results['trending'] = True
            logger.info("✅ 트렌딩 검색어 테스트 완료")
            return True
            
        except Exception as e:
            error_msg = f"트렌딩 검색어 테스트 실패: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.test_results['errors'].append(error_msg)
            return False

    def test_related_queries(self):
        """관련 검색어 테스트"""
        try:
            logger.info("🔗 관련 검색어 테스트 중...")
            
            # 인기 키워드로 테스트
            self.pytrends.build_payload(['bitcoin'], cat=0, timeframe='today 3-m', geo='US')
            
            related_queries = self.pytrends.related_queries()
            
            if related_queries and 'bitcoin' in related_queries:
                bitcoin_queries = related_queries['bitcoin']
                
                if bitcoin_queries['top'] is not None:
                    logger.info(f"✅ 상위 관련 검색어: {len(bitcoin_queries['top'])} 개")
                    logger.info(f"   예시: {bitcoin_queries['top']['query'].head(3).tolist()}")
                
                if bitcoin_queries['rising'] is not None:
                    logger.info(f"✅ 급상승 관련 검색어: {len(bitcoin_queries['rising'])} 개")
                    logger.info(f"   예시: {bitcoin_queries['rising']['query'].head(3).tolist()}")
                
                self.test_results['related_queries'] = True
                return True
            else:
                logger.warning("⚠️ 관련 검색어 데이터 없음")
                return False
                
        except Exception as e:
            error_msg = f"관련 검색어 테스트 실패: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.test_results['errors'].append(error_msg)
            return False

    def test_api_rate_limits(self):
        """API 레이트 리미트 테스트"""
        try:
            logger.info("⏱️ API 레이트 리미트 테스트 중...")
            
            start_time = time.time()
            successful_requests = 0
            
            # 10개의 연속 요청 시도
            for i in range(10):
                try:
                    self.pytrends.build_payload([f'test{i}'], cat=0, timeframe='today 1-m', geo='US')
                    data = self.pytrends.interest_over_time()
                    successful_requests += 1
                    time.sleep(0.5)  # 0.5초 대기
                except Exception as e:
                    logger.warning(f"요청 {i+1} 실패: {str(e)}")
                    break
                    
            elapsed_time = time.time() - start_time
            logger.info(f"✅ {successful_requests}/10 요청 성공 (소요시간: {elapsed_time:.2f}초)")
            
            return successful_requests >= 5  # 50% 이상 성공하면 OK
            
        except Exception as e:
            error_msg = f"레이트 리미트 테스트 실패: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.test_results['errors'].append(error_msg)
            return False

    def test_network_connectivity(self):
        """네트워크 연결 테스트"""
        try:
            logger.info("🌐 네트워크 연결 테스트 중...")
            
            # Google Trends 엔드포인트 테스트
            test_urls = [
                'https://trends.google.com',
                'https://trends.google.com/trends/api/explore',
                'https://www.google.com'
            ]
            
            for url in test_urls:
                try:
                    response = requests.get(url, timeout=10)
                    logger.info(f"✅ {url}: {response.status_code}")
                except Exception as e:
                    logger.warning(f"⚠️ {url}: {str(e)}")
                    
            return True
            
        except Exception as e:
            error_msg = f"네트워크 연결 테스트 실패: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.test_results['errors'].append(error_msg)
            return False

    def run_comprehensive_test(self):
        """종합 테스트 실행"""
        logger.info("=" * 60)
        logger.info("🚀 Google Trends API 종합 테스트 시작")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        
        # 테스트 실행
        tests = [
            ("네트워크 연결", self.test_network_connectivity),
            ("API 연결 초기화", self.initialize_connection),
            ("검색 기능", self.test_search_functionality),
            ("지역별 데이터", self.test_regional_data),
            ("트렌딩 검색어", self.test_trending_searches),
            ("관련 검색어", self.test_related_queries),
            ("레이트 리미트", self.test_api_rate_limits),
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            logger.info(f"\n📋 {test_name} 테스트 중...")
            try:
                if test_func():
                    passed_tests += 1
                    logger.info(f"✅ {test_name} 테스트 통과")
                else:
                    logger.error(f"❌ {test_name} 테스트 실패")
            except Exception as e:
                logger.error(f"❌ {test_name} 테스트 오류: {str(e)}")
            
            time.sleep(1)  # 테스트 간 대기
        
        # 결과 요약
        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info("\n" + "=" * 60)
        logger.info("📊 테스트 결과 요약")
        logger.info("=" * 60)
        logger.info(f"총 테스트: {total_tests}")
        logger.info(f"성공: {passed_tests}")
        logger.info(f"실패: {total_tests - passed_tests}")
        logger.info(f"성공률: {(passed_tests/total_tests)*100:.1f}%")
        logger.info(f"소요시간: {duration.total_seconds():.2f}초")
        
        if self.test_results['errors']:
            logger.info("\n🚨 발생한 오류들:")
            for i, error in enumerate(self.test_results['errors'], 1):
                logger.info(f"  {i}. {error}")
        
        # 전체 결과 판정
        if passed_tests >= total_tests * 0.7:  # 70% 이상 성공
            logger.info("\n🎉 전체 테스트 결과: 성공 (API 연결 정상)")
            return True
        else:
            logger.info("\n💥 전체 테스트 결과: 실패 (API 연결 문제)")
            return False

    def generate_test_report(self):
        """테스트 리포트 생성"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'test_results': self.test_results,
            'summary': {
                'connection_status': 'OK' if self.test_results['connection'] else 'FAILED',
                'api_functionality': 'OK' if sum(self.test_results.values()) >= 3 else 'PARTIAL',
                'errors_count': len(self.test_results['errors'])
            }
        }
        
        return report

def main():
    """메인 테스트 실행"""
    tester = GoogleTrendsAPITester()
    
    try:
        # 종합 테스트 실행
        success = tester.run_comprehensive_test()
        
        # 테스트 리포트 생성
        report = tester.generate_test_report()
        
        # 결과를 JSON 파일로 저장
        import json
        with open('api_test_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n📄 테스트 리포트가 api_test_report.json에 저장되었습니다.")
        
        # 종료 코드 설정
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        logger.info("\n\n⏹️ 테스트가 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n💥 예상치 못한 오류 발생: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
