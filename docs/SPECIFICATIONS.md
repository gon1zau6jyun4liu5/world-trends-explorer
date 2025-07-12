# 🌍 World Trends Explorer - 기능사양서 v1.0.4

## 📋 개요

**프로젝트명**: World Trends Explorer  
**버전**: v1.0.4  
**릴리즈 일자**: 2025-07-13  
**주요 변경사항**: 포트 충돌 해결, 실제 API(5000) + Mock API(5001)  

## 🔧 포트 구성 (v1.0.4)

### 서버 포트 할당
- **실제 Google Trends API**: `http://localhost:5000`
- **Mock 테스트 서버**: `http://localhost:5001`
- **프론트엔드**: `http://localhost:8000` (권장)

### API 전환 기능
```javascript
// 브라우저 콘솔에서 API 전환 가능
trendsAPI.switchToRealAPI();  // 포트 5000
trendsAPI.switchToMockAPI();  // 포트 5001
trendsAPI.getCurrentMode();   // 현재 모드 확인
```

## 🎯 주요 기능

### 1. 🗺️ 인터랙티브 세계지도 (주요 기능)
- **D3.js 기반 SVG 세계지도**: TopoJSON 데이터 활용
- **국가별 클릭 인터랙션**: 실시간 트렌드 데이터 표시
- **지역별 관심도 시각화**: 색상 강도로 데이터 표현
- **지도 컨트롤**: 줌인/줌아웃, 리셋 기능
- **툴팁 표시**: 마우스 오버 시 국가 정보 표시

### 2. 🔍 트렌드 검색 기능
- **키워드 검색**: Google Trends API 활용
- **지역 선택**: 16개 주요 국가 지원
- **시계열 차트**: Chart.js 기반 인터랙티브 차트
- **지역별 순위**: 상위 15개 지역 표시
- **연관 검색어**: 인기/급상승 검색어 제공

### 3. 📊 데이터 시각화
- **시계열 차트**: 관심도 변화 추이
- **지역별 바차트**: 국가별 관심도 순위
- **반응형 차트**: 모바일 친화적 디자인
- **실시간 업데이트**: 캐시 기반 효율적 로딩

### 4. 🔥 글로벌 트렌딩 토픽
- **실시간 인기 검색어**: 국가별 상위 20개
- **인터랙티브 그리드**: 클릭으로 상세 검색
- **다국가 지원**: 8개 주요 국가
- **자동 새로고침**: 주기적 데이터 업데이트

## 🏗️ 기술 아키텍처

### Backend (이중 서버 구조)
- **실제 API 서버** (`app.py`): Python Flask + Pytrends
  - 포트: 5000
  - 실제 Google Trends 데이터
  - 프로덕션 환경용
- **Mock 테스트 서버** (`mock_server.py`): Python Flask + 가짜 데이터
  - 포트: 5001
  - 개발/테스트용 안정적 데이터
  - API 제한 없음

### Frontend
- **HTML5**: 시맨틱 마크업, 접근성 고려
- **CSS3**: Flexbox/Grid, 반응형 디자인
- **JavaScript ES6+**: 모듈화된 구조, API 전환 기능
- **Chart.js**: 차트 렌더링
- **D3.js v7**: 지도 시각화
- **TopoJSON**: 지리 데이터 처리

## 📁 파일 구조

```
world-trends-explorer/
├── 🐍 backend/
│   ├── app.py              # 실제 API 서버 (포트 5000)
│   ├── mock_server.py      # Mock 테스트 서버 (포트 5001)
│   ├── requirements.txt    # Python 의존성
│   ├── README.md          # 백엔드 가이드
│   └── Dockerfile         # Docker 설정
├── 🌐 frontend/
│   ├── index.html         # 메인 HTML (v1.0.4)
│   ├── css/
│   │   └── styles.css     # 메인 스타일시트 (v1.0.4)
│   └── js/
│       ├── api.js         # API 통신 + 전환 기능
│       ├── worldmap.js    # 세계지도 컴포넌트
│       ├── chart.js       # 차트 컴포넌트
│       └── app.js         # 메인 애플리케이션 로직
├── 🧪 tests/
│   └── unit-tests-v1.0.4.html  # 유닛 테스트
├── 📚 docs/
│   ├── DOCKER.md          # Docker 가이드
│   └── SPECIFICATIONS.md  # 기능사양서 (이 문서)
├── 🔧 scripts/
│   └── deploy.sh          # 배포 스크립트
├── start.sh               # 빠른 시작 스크립트 (서버 선택 가능)
└── README.md              # 프로젝트 README
```

## 🔄 버전 히스토리

### v1.0.4 (2025-07-13) - 현재 버전
**🔧 포트 충돌 해결**
- ✅ **포트 분리**: 실제 API(5000) + Mock API(5001)
- ✅ **동시 실행 가능**: 두 서버를 함께 실행 가능
- ✅ **API 전환 기능**: 브라우저에서 실시간 API 전환
- ✅ **향상된 start.sh**: 서버 선택 옵션 추가
- ✅ **문서 업데이트**: 백엔드 가이드 및 사양서 갱신

**📊 이전 수정사항**
- ✅ Worldmap 로딩 이슈 수정 (v1.0.4)
- ✅ 검색 섹션 복원 (v1.0.4)
- ✅ 버전 일관성 (v1.0.4)
- ✅ 유닛 테스트 추가 (v1.0.4)

## 🔌 API 엔드포인트

### 실제 API (포트 5000)
| 엔드포인트 | URL | 설명 |
|-----------|-----|------|
| Health Check | `http://localhost:5000/api/trends/health` | 실제 Google Trends 연결 상태 |
| 키워드 검색 | `http://localhost:5000/api/trends/search` | 실제 트렌드 데이터 |
| 인기 검색어 | `http://localhost:5000/api/trends/trending` | 실제 트렌딩 토픽 |

### Mock API (포트 5001)
| 엔드포인트 | URL | 설명 |
|-----------|-----|------|
| Health Check | `http://localhost:5001/api/trends/health` | Mock 서버 상태 |
| 키워드 검색 | `http://localhost:5001/api/trends/search` | 테스트용 가짜 데이터 |
| 인기 검색어 | `http://localhost:5001/api/trends/trending` | 테스트용 트렌딩 토픽 |

### 공통 엔드포인트
- `/api/trends/suggestions` - 키워드 제안
- `/api/trends/countries` - 지원 국가 목록
- `/api/trends/compare` - 키워드 비교 (POST)

## 🚀 실행 가이드

### 1. 빠른 시작 (권장)
```bash
./start.sh
# 서버 선택:
# 1. 실제 API (포트 5000)
# 2. Mock API (포트 5001)
```

### 2. 수동 실행
```bash
# 실제 API 서버
cd backend && python app.py

# Mock API 서버 (별도 터미널)
cd backend && python mock_server.py

# 프론트엔드
cd frontend && python -m http.server 8000
```

### 3. API 전환
```javascript
// 브라우저 콘솔에서
trendsAPI.switchToRealAPI();  // 실제 데이터
trendsAPI.switchToMockAPI();  // 테스트 데이터
```

## 🧪 테스트 전략

### 이중 서버 테스트
1. **실제 API 테스트**: `curl http://localhost:5000/api/trends/health`
2. **Mock API 테스트**: `curl http://localhost:5001/api/trends/health`
3. **프론트엔드 전환 테스트**: 브라우저에서 API 모드 전환

### 유닛 테스트 v1.0.4
- 파일: `tests/unit-tests-v1.0.4.html`
- 포트 충돌 해결 검증
- API 전환 기능 테스트
- 17개 테스트 통과 확인

## 💡 사용 시나리오

### 개발 단계
```bash
# Mock API로 빠른 개발
python mock_server.py
# 브라우저: trendsAPI.switchToMockAPI()
```

### 테스트 단계
```bash
# 실제 API로 데이터 검증
python app.py
# 브라우저: trendsAPI.switchToRealAPI()
```

### 프로덕션 배포
- 실제 API (포트 5000)만 배포
- Mock API는 개발 환경에서만 사용

## 🐛 문제 해결

### 포트 충돌 (해결됨 ✅)
- 실제 API: 5000번 포트
- Mock API: 5001번 포트
- 동시 실행 가능

### Google Trends API 에러 시
1. Mock API로 전환: `trendsAPI.switchToMockAPI()`
2. 개발 계속 진행
3. API 복구 후 실제 API로 복귀

### 개발 속도 향상
- Mock API 사용으로 API 제한 없이 개발
- 캐시 기능으로 중복 요청 방지
- 브라우저에서 실시간 API 전환

---

**📝 문서 정보**
- **최종 업데이트**: 2025-07-13
- **문서 버전**: v1.0.4 - 포트 충돌 해결
- **주요 개선**: 이중 서버 구조, API 전환 기능

**🔄 변경 이력**
- v1.0.4: 포트 충돌 해결, 이중 서버 구조 도입
- v1.0.4: 지도 로딩 이슈 수정, 검색 섹션 복원
- v1.0.3: 세계지도 중심 디자인
- v1.0.2: 기본 세계지도 기능
- v1.0.1: 초기 프로토타입