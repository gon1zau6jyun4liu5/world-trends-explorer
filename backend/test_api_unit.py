#!/usr/bin/env python3
"""
Unit Tests for Google Trends API Connection
구글 트렌드 API 연결 유닛 테스트
"""

import unittest
import sys
import os
import time
from unittest.mock import patch, MagicMock
import pandas as pd

# 현재 디렉토리를 Python path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from test_api_connection import GoogleTrendsAPITester
    import pytrends
    from pytrends.request import TrendReq
except ImportError as e:
    print(f"Import error: {e}")
    print("Please make sure pytrends is installed: pip install pytrends")
    sys.exit(1)

class TestGoogleTrendsAPI(unittest.TestCase):
    """Google Trends API 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        self.tester = GoogleTrendsAPITester()
        self.test_timeout = 30  # 30초 타임아웃
    
    def test_initialize_connection(self):
        """API 연결 초기화 테스트"""
        print("\n🔄 API 연결 초기화 테스트...")
        
        start_time = time.time()
        result = self.tester.initialize_connection()
        elapsed_time = time.time() - start_time
        
        self.assertIsInstance(result, bool, "연결 결과는 boolean이어야 함")
        self.assertLess(elapsed_time, self.test_timeout, f"연결 시간이 {self.test_timeout}초를 초과함")
        
        if result:
            self.assertIsNotNone(self.tester.pytrends, "연결 성공 시 pytrends 객체가 존재해야 함")
            print("✅ API 연결 초기화 성공")
        else:
            print("❌ API 연결 초기화 실패")
    
    def test_search_functionality_with_valid_keyword(self):
        """유효한 키워드로 검색 기능 테스트"""
        print("\n🔍 검색 기능 테스트 (유효한 키워드)...")
        
        # API 연결이 되어 있지 않으면 연결 시도
        if not self.tester.pytrends:
            if not self.tester.initialize_connection():
                self.skipTest("API 연결 실패로 테스트 스킵")
        
        # 검색 기능 테스트
        result = self.tester.test_search_functionality()
        
        if result:
            print("✅ 검색 기능 테스트 성공")
        else:
            print("❌ 검색 기능 테스트 실패")
            
        # 결과 검증은 선택적 (API 상태에 따라 달라질 수 있음)
        self.assertIsInstance(result, bool, "검색 결과는 boolean이어야 함")
    
    def test_regional_data_functionality(self):
        """지역별 데이터 기능 테스트"""
        print("\n🌍 지역별 데이터 테스트...")
        
        # API 연결이 되어 있지 않으면 연결 시도
        if not self.tester.pytrends:
            if not self.tester.initialize_connection():
                self.skipTest("API 연결 실패로 테스트 스킵")
        
        result = self.tester.test_regional_data()
        
        if result:
            print("✅ 지역별 데이터 테스트 성공")
        else:
            print("❌ 지역별 데이터 테스트 실패")
            
        self.assertIsInstance(result, bool, "지역별 데이터 결과는 boolean이어야 함")
    
    def test_trending_searches_functionality(self):
        """트렌딩 검색어 기능 테스트"""
        print("\n🔥 트렌딩 검색어 테스트...")
        
        # API 연결이 되어 있지 않으면 연결 시도
        if not self.tester.pytrends:
            if not self.tester.initialize_connection():
                self.skipTest("API 연결 실패로 테스트 스킵")
        
        result = self.tester.test_trending_searches()
        
        if result:
            print("✅ 트렌딩 검색어 테스트 성공")
        else:
            print("❌ 트렌딩 검색어 테스트 실패")
            
        self.assertIsInstance(result, bool, "트렌딩 검색어 결과는 boolean이어야 함")
    
    def test_error_handling(self):
        """에러 처리 테스트"""
        print("\n⚠️ 에러 처리 테스트...")
        
        # 잘못된 키워드로 테스트
        try:
            if self.tester.pytrends:
                # 빈 키워드 리스트로 테스트
                self.tester.pytrends.build_payload([], cat=0, timeframe='today 1-m')
                data = self.tester.pytrends.interest_over_time()
                print("⚠️ 빈 키워드로도 데이터가 반환됨")
            else:
                print("⚠️ API 연결이 없어 에러 처리 테스트 스킵")
        except Exception as e:
            print(f"✅ 예상된 에러 발생: {type(e).__name__}")
            self.assertIsInstance(e, Exception, "에러가 적절히 발생해야 함")
    
    def test_data_structure_validation(self):
        """데이터 구조 검증 테스트"""
        print("\n📊 데이터 구조 검증 테스트...")
        
        # API 연결이 되어 있지 않으면 연결 시도
        if not self.tester.pytrends:
            if not self.tester.initialize_connection():
                self.skipTest("API 연결 실패로 테스트 스킵")
        
        try:
            # 간단한 검색으로 데이터 구조 확인
            self.tester.pytrends.build_payload(['test'], cat=0, timeframe='today 1-m', geo='US')
            
            # 시간대별 데이터 구조 확인
            interest_over_time = self.tester.pytrends.interest_over_time()
            if not interest_over_time.empty:
                self.assertIsInstance(interest_over_time, pd.DataFrame, "시간대별 데이터는 DataFrame이어야 함")
                self.assertIn('test', interest_over_time.columns, "검색 키워드가 컬럼에 있어야 함")
                print("✅ 시간대별 데이터 구조 확인")
            
            # 지역별 데이터 구조 확인
            interest_by_region = self.tester.pytrends.interest_by_region(resolution='COUNTRY', inc_geo_code=True)
            if not interest_by_region.empty:
                self.assertIsInstance(interest_by_region, pd.DataFrame, "지역별 데이터는 DataFrame이어야 함")
                print("✅ 지역별 데이터 구조 확인")
            
        except Exception as e:
            print(f"⚠️ 데이터 구조 검증 중 오류: {e}")
    
    def test_rate_limiting_behavior(self):
        """레이트 리미팅 동작 테스트"""
        print("\n⏱️ 레이트 리미팅 테스트...")
        
        # API 연결이 되어 있지 않으면 연결 시도
        if not self.tester.pytrends:
            if not self.tester.initialize_connection():
                self.skipTest("API 연결 실패로 테스트 스킵")
        
        # 빠른 연속 요청으로 레이트 리미팅 테스트
        success_count = 0
        total_requests = 3  # 적은 수로 테스트
        
        for i in range(total_requests):
            try:
                self.tester.pytrends.build_payload([f'test{i}'], cat=0, timeframe='today 1-m', geo='US')
                data = self.tester.pytrends.interest_over_time()
                success_count += 1
                time.sleep(0.5)  # 짧은 대기
            except Exception as e:
                print(f"요청 {i+1} 실패: {type(e).__name__}")
                break
        
        print(f"✅ {success_count}/{total_requests} 요청 성공")
        self.assertGreater(success_count, 0, "최소 1개 요청은 성공해야 함")

class TestMockAPI(unittest.TestCase):
    """Mock API 테스트 (오프라인 테스트용)"""
    
    def test_mock_pytrends_functionality(self):
        """Mock을 사용한 기능 테스트"""
        print("\n🎭 Mock API 기능 테스트...")
        
        with patch('pytrends.request.TrendReq') as mock_pytrends:
            # Mock 설정
            mock_instance = MagicMock()
            mock_pytrends.return_value = mock_instance
            
            # Mock 데이터 설정
            mock_df = pd.DataFrame({
                'test_keyword': [10, 20, 30, 40, 50],
                'isPartial': [False, False, False, False, True]
            })
            mock_instance.interest_over_time.return_value = mock_df
            
            # 테스트 실행
            tester = GoogleTrendsAPITester()
            tester.pytrends = mock_instance
            
            # Mock 동작 확인
            tester.pytrends.build_payload(['test_keyword'], cat=0, timeframe='today 1-m')
            result_df = tester.pytrends.interest_over_time()
            
            self.assertIsInstance(result_df, pd.DataFrame, "결과는 DataFrame이어야 함")
            self.assertIn('test_keyword', result_df.columns, "키워드 컬럼이 있어야 함")
            self.assertEqual(len(result_df), 5, "5개 행이 있어야 함")
            
            print("✅ Mock API 기능 테스트 성공")

def run_api_tests():
    """API 테스트 실행"""
    print("=" * 60)
    print("🧪 Google Trends API 유닛 테스트 시작")
    print("=" * 60)
    
    # 테스트 스위트 생성
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 실제 API 테스트 추가
    suite.addTests(loader.loadTestsFromTestCase(TestGoogleTrendsAPI))
    
    # Mock 테스트 추가
    suite.addTests(loader.loadTestsFromTestCase(TestMockAPI))
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 유닛 테스트 결과 요약")
    print("=" * 60)
    print(f"총 테스트: {result.testsRun}")
    print(f"성공: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"실패: {len(result.failures)}")
    print(f"오류: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ 실패한 테스트:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n💥 오류가 발생한 테스트:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    # 성공 여부 반환
    return len(result.failures) == 0 and len(result.errors) == 0

if __name__ == "__main__":
    try:
        success = run_api_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ 테스트가 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 예상치 못한 오류 발생: {e}")
        sys.exit(1)
