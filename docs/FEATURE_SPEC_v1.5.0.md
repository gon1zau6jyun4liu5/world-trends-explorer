# World Trends Explorer - 기능 사양서

## 버전: v1.5.0

### 변경 이력
- v1.0.0 - 초기 릴리즈 (pytrends 기반)
- v1.1.0 - Mock 서버 추가
- v1.2.0 - Docker 지원 추가
- v1.3.0 - 대화형 세계 지도 기능 추가
- v1.4.0 - 프론트엔드 UI 개선
- **v1.5.0 - SerpAPI 통합 (현재)**

## 주요 기능

### 1. 백엔드 서버 (Flask)

#### 1.1 기존 구현 (app.py)
- **라이브러리**: pytrends (Google Trends 비공식 API)
- **엔드포인트**:
  - `GET /api/trends/health` - 헬스 체크
  - `GET /api/trends/search` - 키워드 검색
  - `GET /api/trends/trending` - 국가별 트렌드
  - `GET /api/trends/suggestions` - 키워드 제안
  - `GET /api/trends/countries` - 지원 국가 목록
  - `POST /api/trends/compare` - 키워드 비교

#### 1.2 SerpAPI 구현 (app_serpapi.py) - **NEW in v1.5.0**
- **라이브러리**: SerpAPI (공식 Google 검색 API)
- **장점**:
  - 더 안정적인 데이터 수집
  - 공식 API로 제한 사항 명확
  - Mock 모드 자동 전환
- **환경 설정**:
  - `.env` 파일을 통한 API 키 관리
  - 환경 변수 자동 로드
  - API 키 없을 시 Mock 데이터 제공

#### 1.3 Mock 서버 (mock_server.py)
- 포트: 5001 (기본 서버와 분리)
- 실제와 유사한 테스트 데이터 제공
- API 제한 없이 개발/테스트 가능

### 2. 프론트엔드 (Vanilla JavaScript)

#### 2.1 핵심 컴포넌트
- **api.js**: API 통신 모듈
  - 캐싱 기능 (5분)
  - 에러 처리
  - 타임아웃 관리 (30초)
  
- **worldmap.js**: D3.js 기반 세계 지도
  - TopoJSON 데이터 사용
  - 국가별 색상 코딩
  - 인터랙티브 툴팁
  - 클릭 이벤트 처리
  
- **chart.js**: Chart.js 기반 차트
  - 시계열 라인 차트
  - 지역별 막대 차트
  - 비교 차트 (최대 5개 키워드)
  
- **app.js**: 메인 애플리케이션 로직
  - 컴포넌트 조정
  - 이벤트 처리
  - 상태 관리

#### 2.2 사용자 인터페이스
- **반응형 디자인**: 모바일, 태블릿, 데스크톱 지원
- **다크 모드**: 그라데이션 배경
- **애니메이션**: 부드러운 전환 효과
- **접근성**: ARIA 레이블, 키보드 네비게이션

### 3. 데이터 시각화

#### 3.1 세계 지도 시각화
- 국가별 관심도를 색상 강도로 표현
- 6단계 색상 스케일 (연한 파랑 → 진한 파랑)
- 호버 효과 및 클릭 상호작용
- 실시간 데이터 업데이트

#### 3.2 차트 시각화
- **시계열 차트**: 최대 12개월 데이터
- **지역별 차트**: 상위 10개 지역
- **비교 차트**: 여러 키워드 동시 표시

### 4. API 통합

#### 4.1 Google Trends 데이터
- **pytrends 버전**: 비공식 API, 제한 없음
- **SerpAPI 버전**: 공식 API, 월 100회 무료

#### 4.2 캐싱 전략
- 프론트엔드: 5분 캐시
- 검색 결과별 개별 캐싱
- 수동 캐시 클리어 기능

### 5. 배포 옵션

#### 5.1 로컬 개발
- `start.sh`: pytrends 서버 시작
- `start_serpapi.sh`: SerpAPI 서버 시작 - **NEW in v1.5.0**
- 개발 서버 자동 리로드

#### 5.2 Docker 배포
- `docker-compose.yml`: 전체 스택
- `docker-compose.dev.yml`: 개발 환경
- 자동 헬스 체크

### 6. 보안 및 설정

#### 6.1 환경 변수 - **ENHANCED in v1.5.0**
- `.env` 파일을 통한 설정 관리
- `.env.example` 템플릿 제공
- Git 제외 (.gitignore)

#### 6.2 API 키 관리
- SerpAPI 키 안전한 저장
- 환경별 설정 분리
- Mock 모드 자동 전환

### 7. 테스트

#### 7.1 유닛 테스트 - **NEW in v1.5.0**
- `test_serpapi_backend.py`: SerpAPI 백엔드 테스트
- Mock 데이터 테스트
- 에러 처리 테스트

#### 7.2 테스트 실행
- `run_tests.sh`: 자동 테스트 스크립트
- pytest 또는 unittest 사용

### 8. 문서화

#### 8.1 사용자 문서
- `README.md`: 프로젝트 개요
- `SERPAPI_QUICK_SETUP_KR.md`: 한국어 빠른 설정 가이드 - **NEW in v1.5.0**

#### 8.2 기술 문서
- `docs/API.md`: API 명세
- `docs/DOCKER.md`: Docker 설정
- `docs/SERPAPI_SETUP.md`: SerpAPI 설정 가이드 - **NEW in v1.5.0**

## 시스템 요구사항

### 백엔드
- Python 3.8+
- Flask 3.0.0
- pytrends 4.9.2 또는 SerpAPI

### 프론트엔드
- 모던 웹 브라우저 (Chrome, Firefox, Safari, Edge)
- JavaScript ES6+ 지원

### 선택사항
- Docker & Docker Compose
- Redis (캐싱용)

## 향후 계획

### v1.6.0 (예정)
- [ ] 실시간 업데이트 (WebSocket)
- [ ] 다국어 지원
- [ ] 데이터 내보내기 기능

### v2.0.0 (예정)
- [ ] 사용자 인증
- [ ] 검색 기록 저장
- [ ] 대시보드 커스터마이징
