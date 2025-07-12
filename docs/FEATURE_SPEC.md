# World Trends Explorer - 기능사양서

## 프로젝트 정보
- **프로젝트명**: World Trends Explorer
- **버전**: v1.0.5
- **최종 업데이트**: 2025-07-12
- **개발 환경**: Python 3.8+, JavaScript ES6+, Flask, D3.js

## 시스템 개요
Google Trends API를 활용한 실시간 트렌드 분석 및 시각화 시스템입니다. 사용자는 키워드를 검색하여 전 세계의 관심도 변화를 확인하고, 인터랙티브한 세계 지도를 통해 지역별 트렌드를 탐색할 수 있습니다.

## 핵심 기능

### 1. 트렌드 검색 기능
- **기능 ID**: F001
- **설명**: 키워드 기반 Google Trends 데이터 검색
- **입력**: 
  - 키워드 (필수, 최대 100자)
  - 지역 코드 (선택사항, 기본값: 전세계)
  - 기간 (선택사항, 기본값: 최근 12개월)
- **출력**:
  - 시간대별 관심도 변화 그래프
  - 지역별 관심도 데이터
  - 관련 검색어 (상위/급상승)
- **API 엔드포인트**: `GET /api/trends/search`

### 2. 인터랙티브 세계 지도
- **기능 ID**: F002
- **설명**: D3.js 기반 실시간 데이터 시각화 지도
- **특징**:
  - 국가별 클릭 가능
  - 관심도에 따른 색상 구분
  - 툴팁을 통한 상세 정보 표시
  - 확대/축소 및 리셋 기능
- **데이터 소스**: TopoJSON 세계 지도 데이터

### 3. 트렌딩 검색어 조회
- **기능 ID**: F003
- **설명**: 국가별 실시간 인기 검색어 제공
- **입력**: 국가 코드
- **출력**: 순위별 트렌딩 검색어 목록 (최대 20개)
- **API 엔드포인트**: `GET /api/trends/trending`

### 4. 키워드 비교 분석
- **기능 ID**: F004
- **설명**: 최대 5개 키워드 동시 비교
- **입력**: 키워드 배열 (2-5개)
- **출력**: 키워드별 시간대별 관심도 비교 차트
- **API 엔드포인트**: `POST /api/trends/compare`

### 5. 검색어 자동완성
- **기능 ID**: F005
- **설명**: 입력 키워드 기반 검색어 제안
- **입력**: 부분 키워드 (최소 3자)
- **출력**: 관련 검색어 제안 목록
- **API 엔드포인트**: `GET /api/trends/suggestions`

### 6. API 연결 테스트 (v1.0.5 신규)
- **기능 ID**: F006
- **설명**: Google Trends API 연결 상태 검증 및 진단
- **구성 요소**:
  - 종합 API 테스트 (`test_api_connection.py`)
  - 빠른 API 확인 (`verify_api.py`)
  - 유닛 테스트 (`test_api_unit.py`)
  - 백엔드 엔드포인트 테스트 (`test_backend_api.py`)
- **기능**:
  - 네트워크 연결성 확인
  - API 초기화 및 인증 테스트
  - 모든 API 기능 검증
  - 에러 진단 및 해결 가이드 제공

## API 명세

### 기본 정보
- **Base URL**: `http://localhost:5000/api/trends`
- **Content-Type**: `application/json`
- **타임아웃**: 30초
- **레이트 리미트**: 분당 60회 요청

### 엔드포인트 목록

#### 1. 헬스 체크
```
GET /api/trends/health
```
**응답**:
```json
{
  "status": "healthy",
  "timestamp": "2025-07-12T18:00:00Z",
  "service": "World Trends Explorer API"
}
```

#### 2. 트렌드 검색
```
GET /api/trends/search?keyword={keyword}&geo={geo}&timeframe={timeframe}
```
**파라미터**:
- `keyword` (필수): 검색 키워드
- `geo` (선택): 국가 코드 (예: US, KR, JP)
- `timeframe` (선택): 기간 (기본값: today 12-m)

**응답**:
```json
{
  "keyword": "python",
  "geo": "US",
  "timeframe": "today 12-m",
  "timestamp": "2025-07-12T18:00:00Z",
  "interest_over_time": [
    {"date": "2025-01-01T00:00:00Z", "value": 75}
  ],
  "interest_by_region": [
    {"geoName": "United States", "geoCode": "US", "value": 100}
  ],
  "related_queries": {
    "top": [{"query": "python programming", "value": "100"}],
    "rising": [{"query": "python tutorial", "value": "+500%"}]
  }
}
```

## 테스트 사양 (v1.0.5 신규)

### API 연결 테스트
- **파일**: `backend/test_api_connection.py`
- **목적**: Google Trends API 연결 상태 종합 확인
- **테스트 항목**:
  - 네트워크 연결성
  - API 초기화
  - 검색 기능
  - 지역별 데이터
  - 트렌딩 검색어
  - 관련 검색어
  - 레이트 리미트 확인

### 유닛 테스트
- **파일**: `backend/test_api_unit.py`
- **목적**: 개별 기능 단위 테스트
- **테스트 항목**:
  - API 연결 초기화
  - 검색 기능 정상 동작
  - 지역별 데이터 수집
  - 트렌딩 검색어 조회
  - 에러 처리
  - 데이터 구조 검증
  - Mock API 테스트

### 백엔드 API 테스트
- **파일**: `backend/test_backend_api.py`
- **목적**: Flask 서버 엔드포인트 테스트
- **테스트 항목**:
  - 헬스 체크 엔드포인트
  - 검색 엔드포인트
  - 트렌딩 엔드포인트
  - 국가 목록 엔드포인트
  - 검색어 제안 엔드포인트
  - 키워드 비교 엔드포인트

### 테스트 실행 방법
```bash
# 빠른 API 연결 확인
cd backend
python verify_api.py

# 종합 테스트 실행
chmod +x run_api_test.sh
./run_api_test.sh comprehensive

# 유닛 테스트
./run_api_test.sh unit

# 백엔드 서버 테스트 (서버 실행 필요)
python test_backend_api.py

# 특정 엔드포인트 테스트
python test_backend_api.py --endpoint health
```

### 테스트 결과 해석
- **70% 이상 성공**: ✅ API 정상 작동
- **50-70% 성공**: ⚠️ 부분적 기능, 일부 제한
- **50% 미만 성공**: ❌ 연결 문제, 네트워크/설정 확인 필요

## 변경 이력

### v1.0.5 (2025-07-12) 🧪
**주요 기능: Google Trends API 연결 테스트 및 검증 시스템 추가**

- **새로운 기능**:
  - 종합 API 연결 테스트 시스템 (`test_api_connection.py`)
  - 빠른 API 검증 스크립트 (`verify_api.py`)
  - 유닛 테스트 프레임워크 (`test_api_unit.py`)
  - 백엔드 엔드포인트 테스트 (`test_backend_api.py`)
  - 테스트 자동화 스크립트 (`run_api_test.sh`)
  - 상세한 릴리즈 노트 (`RELEASE_NOTES.md`)

- **개선사항**:
  - Google Trends API 연결 안정성 향상
  - 에러 처리 및 로깅 강화
  - 개발자 경험 개선 (디버깅 도구)
  - 문서화 체계 구축

- **테스트 커버리지**:
  - API 연결성 테스트 (7개 항목)
  - 유닛 테스트 (8개 테스트 케이스)
  - 백엔드 엔드포인트 테스트 (6개 API)
  - Mock API 테스트 지원

### v1.0.4 (2025-07-12)
- 기본 World Trends Explorer 애플리케이션
- 인터랙티브 세계 지도 구현
- Google Trends API 연동
- 실시간 트렌드 검색 및 시각화

### v1.0.3 (2025-07-11)
- 프론트엔드 UI/UX 개선
- 지도 렌더링 버그 수정
- 모바일 반응형 최적화

### v1.0.2 (2025-07-11)
- API 에러 처리 개선
- 차트 성능 최적화
- 추가 국가 지원

### v1.0.1 (2025-07-11)
- 초기 버그 수정
- 문서화 개선

### v1.0.0 (2025-07-11)
- 초기 릴리즈
- 기본 세계 지도 구현
- Google Trends 검색 기능

## 알려진 제한사항
1. **Google Trends API 제한**:
   - 요청 횟수 제한 (분당 약 60회)
   - 일부 키워드 검색 결과 없음
   - 지역별 데이터 가용성 차이

2. **브라우저 호환성**:
   - Internet Explorer 지원 안함
   - 모던 브라우저 필수 (Chrome, Firefox, Safari, Edge)

3. **데이터 정확성**:
   - Google Trends 데이터는 샘플링 기반
   - 실시간 데이터가 아닌 지연된 데이터
   - 검색량이 적은 키워드는 데이터 없음

## API 연결 상태 확인 방법 (v1.0.5)

### 1. 빠른 연결 테스트
```bash
cd backend
python verify_api.py
```

### 2. 종합 테스트
```bash
./run_api_test.sh comprehensive
```

### 3. 개별 기능 테스트
```bash
# Google Trends API 직접 테스트
python test_api_connection.py

# 유닛 테스트 실행
python test_api_unit.py

# 백엔드 서버 테스트 (서버 실행 후)
python test_backend_api.py
```

## 트러블슈팅 가이드

### API 연결 실패 시
1. **인터넷 연결 확인**
2. **방화벽 설정 점검**
3. **Google Trends 서비스 상태 확인**
4. **요청 빈도 조절** (너무 많은 요청으로 인한 일시적 제한)
5. **테스트 도구 활용**: `python verify_api.py`

### 검색 결과 없음
1. **다른 키워드로 시도**
2. **지역 설정 변경**
3. **검색 기간 조정**

### 성능 최적화
1. **캐싱 활용** (5분간 결과 캐시)
2. **요청 빈도 조절**
3. **배치 처리 고려**

---

**문서 작성자**: World Trends Explorer 개발팀  
**문서 버전**: 1.0.5  
**최종 수정일**: 2025-07-12  
**크로스 체크**: RELEASE_NOTES.md v1.0.5와 일치 확인 ✅