# 🌍 World Trends Explorer - 기능사양서 v1.0.4

## 📋 개요

**프로젝트명**: World Trends Explorer  
**버전**: v1.0.4  
**릴리즈 일자**: 2025-07-13  
**주요 변경사항**: Worldmap 로딩 이슈 수정, 검색 섹션 복원  

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

### Frontend
- **HTML5**: 시맨틱 마크업, 접근성 고려
- **CSS3**: Flexbox/Grid, 반응형 디자인
- **JavaScript ES6+**: 모듈화된 구조
- **Chart.js**: 차트 렌더링
- **D3.js v7**: 지도 시각화
- **TopoJSON**: 지리 데이터 처리

### Backend
- **Python 3.11+**: 서버 언어
- **Flask**: 웹 프레임워크
- **Pytrends**: Google Trends API 래퍼
- **Pandas**: 데이터 처리
- **Flask-CORS**: CORS 지원

### 데이터 소스
- **Google Trends API**: 트렌드 데이터
- **Natural Earth**: 세계지도 데이터
- **CDN**: 외부 라이브러리

## 📁 파일 구조

```
world-trends-explorer/
├── 🐍 backend/
│   ├── app.py              # 메인 Flask 애플리케이션
│   ├── mock_server.py      # 테스트용 Mock 서버
│   ├── requirements.txt    # Python 의존성
│   └── Dockerfile         # Docker 설정
├── 🌐 frontend/
│   ├── index.html         # 메인 HTML (v1.0.4)
│   ├── css/
│   │   └── styles.css     # 메인 스타일시트 (v1.0.4)
│   └── js/
│       ├── api.js         # API 통신 모듈
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
├── start.sh               # 빠른 시작 스크립트
└── README.md              # 프로젝트 README
```

## 🔄 버전 히스토리

### v1.0.4 (2025-07-13) - 현재 버전
**🔧 버그 수정**
- ✅ **Worldmap 로딩 이슈 수정**: `app_worldmap_focused.js` → `app.js` 파일 참조 수정
- ✅ **검색 섹션 복원**: 누락된 검색 UI 섹션 다시 추가
- ✅ **버전 일관성**: 모든 파일에 v1.0.4 버전 표시
- ✅ **CSS 스타일 개선**: 검색 섹션 스타일 추가
- ✅ **유닛 테스트 추가**: 포괄적인 테스트 스위트 구현

**📊 개선사항**
- 향상된 모바일 반응성
- 더 나은 에러 처리
- 개선된 로딩 상태 표시

### v1.0.3 (이전 버전)
- 세계지도 포커스 디자인
- 국가별 트렌딩 토픽
- 향상된 UI/UX

### v1.0.2 (이전 버전)
- 기본 세계지도 기능
- 트렌드 검색 구현

### v1.0.1 (이전 버전)
- 초기 프로토타입
- 기본 API 연동

## 🔌 API 엔드포인트

### 핵심 엔드포인트
| 엔드포인트 | 메서드 | 설명 | 매개변수 |
|-----------|--------|------|----------|
| `/api/trends/health` | GET | 서버 상태 확인 | - |
| `/api/trends/search` | GET | 키워드 트렌드 검색 | keyword, geo, timeframe |
| `/api/trends/trending` | GET | 인기 검색어 목록 | geo |
| `/api/trends/suggestions` | GET | 키워드 제안 | keyword |
| `/api/trends/countries` | GET | 지원 국가 목록 | - |
| `/api/trends/compare` | POST | 키워드 비교 | keywords[], geo, timeframe |

### 응답 형식
```json
{
  "keyword": "cryptocurrency",
  "geo": "US",
  "timeframe": "today 12-m",
  "timestamp": "2025-07-13T02:16:34Z",
  "interest_over_time": [
    {"date": "2024-07-01", "value": 85},
    {"date": "2024-08-01", "value": 92}
  ],
  "interest_by_region": [
    {"geoName": "United States", "geoCode": "US", "value": 100},
    {"geoName": "Germany", "geoCode": "DE", "value": 85}
  ],
  "related_queries": {
    "top": [{"query": "bitcoin", "value": "100"}],
    "rising": [{"query": "crypto news", "value": "Breakout"}]
  }
}
```

## 🎨 사용자 인터페이스

### 레이아웃 구성
1. **헤더**: 제목, 버전, 부제목
2. **검색 섹션**: 키워드 입력, 국가 선택, 검색 버튼
3. **세계지도 섹션**: 인터랙티브 D3.js 지도
4. **결과 섹션**: 차트, 지역 데이터, 연관 검색어
5. **트렌딩 섹션**: 글로벌 인기 토픽
6. **푸터**: 저작권, 버전 정보

### 색상 팔레트
- **주 색상**: #667eea (파란 보라)
- **보조 색상**: #764ba2 (진한 보라)
- **배경**: 그라디언트 (135deg, #667eea 0%, #764ba2 100%)
- **텍스트**: #333 (진한 회색)
- **강조**: #ff6b6b (빨강), #28a745 (초록)

### 반응형 브레이크포인트
- **Desktop**: 1200px+
- **Tablet**: 768px - 1199px
- **Mobile**: < 768px

## 🔧 설정 및 환경변수

### 환경변수
```bash
# 백엔드 설정
FLASK_ENV=production          # 실행 환경
FLASK_DEBUG=False            # 디버그 모드
PORT=5000                    # 서버 포트

# 프론트엔드 설정
API_BASE_URL=http://localhost:5000/api/trends  # API 기본 URL
```

### 의존성 관리
- **Python**: requirements.txt
- **JavaScript**: CDN 라이브러리 (Chart.js, D3.js, TopoJSON)

## 🧪 테스트 전략

### 유닛 테스트 v1.0.4
- **외부 의존성 테스트**: Chart.js, D3.js, TopoJSON 로딩 확인
- **API 모듈 테스트**: Mock API로 기능 검증
- **HTML 구조 테스트**: 버전 일관성, DOM 요소 존재
- **버그 수정 검증**: 파일 참조, 검색 섹션 복원
- **에러 처리 테스트**: 예외 상황 대응

### 테스트 실행
```bash
# 브라우저에서 테스트 실행
open tests/unit-tests-v1.0.4.html

# 또는 로컬 서버로 실행
cd tests && python -m http.server 8080
```

## 🚀 배포 가이드

### 로컬 개발 환경
```bash
# 1. 저장소 클론
git clone https://github.com/gon1zau6jyun4liu5/world-trends-explorer.git
cd world-trends-explorer

# 2. 백엔드 시작
./start.sh

# 3. 프론트엔드 실행
cd frontend
python -m http.server 8000
```

### Docker 배포
```bash
# 전체 스택 실행
docker-compose up --build

# 개발 환경 실행
docker-compose -f docker-compose.dev.yml up
```

### 프로덕션 배포
```bash
# 배포 스크립트 실행
./scripts/deploy.sh production

# 또는 수동 빌드
cd frontend
# API URL 수정
sed -i 's|http://localhost:5000|https://your-api-domain.com|g' js/api.js
```

## 🔒 보안 고려사항

### API 보안
- **CORS 설정**: 허용된 도메인만 접근 가능
- **Rate Limiting**: API 남용 방지 (계획됨)
- **Input Validation**: 사용자 입력 검증
- **Error Handling**: 민감한 정보 노출 방지

### 클라이언트 보안
- **XSS 방지**: 사용자 입력 이스케이프 처리
- **CSP 헤더**: Content Security Policy 적용 권장
- **HTTPS**: 프로덕션 환경에서 SSL/TLS 사용

## 📊 성능 최적화

### 캐싱 전략
- **브라우저 캐시**: 정적 파일 캐싱 (5분)
- **API 캐시**: 트렌드 데이터 캐싱 (5-15분)
- **CDN 활용**: 외부 라이브러리 빠른 로딩

### 최적화 기법
- **이미지 최적화**: SVG 아이콘 사용
- **코드 압축**: 프로덕션 빌드 시 minification
- **Lazy Loading**: 차트/지도 데이터 지연 로딩
- **Debouncing**: 검색 입력 최적화

## 📱 접근성 (Accessibility)

### WCAG 2.1 준수
- **키보드 네비게이션**: 모든 기능 키보드로 접근 가능
- **스크린 리더 지원**: ARIA 라벨, semantic HTML
- **색상 대비**: 4.5:1 이상 명암비 유지
- **반응형 디자인**: 다양한 화면 크기 지원

### 사용성 개선
- **로딩 인디케이터**: 사용자 피드백 제공
- **에러 메시지**: 명확한 오류 안내
- **툴팁**: 추가 정보 제공
- **모바일 최적화**: 터치 친화적 인터페이스

## 🐛 알려진 이슈 및 제한사항

### 해결된 이슈 (v1.0.4)
- ✅ **지도 로딩 실패**: 잘못된 JavaScript 파일 참조 수정
- ✅ **검색 기능 누락**: 검색 UI 섹션 복원
- ✅ **버전 불일치**: 모든 파일 버전 동기화

### 현재 제한사항
- **Google Trends API**: 일일 요청 제한 존재
- **실시간 데이터**: 15분 지연 가능
- **지역 제한**: 일부 국가 데이터 제한적
- **언어 지원**: 현재 영어만 지원

### 계획된 개선사항
- 🔄 **다국어 지원**: 한국어, 일본어 추가
- 📊 **더 많은 차트 타입**: 히트맵, 버블 차트
- 🔔 **알림 기능**: 트렌드 변화 알림
- 📱 **PWA 지원**: 오프라인 기능

## 👥 기여 가이드라인

### 개발 워크플로우
1. **브랜치 생성**: `feature/new-feature` 또는 `fix/bug-description`
2. **코드 작성**: 일관된 코딩 스타일 유지
3. **테스트 추가**: 새 기능에 대한 테스트 작성
4. **문서 업데이트**: 기능사양서, README 갱신
5. **PR 생성**: 상세한 설명과 함께 풀 리퀘스트

### 코딩 스타일
- **JavaScript**: ES6+ 문법, 모듈화
- **CSS**: BEM 방법론, 모바일 우선
- **Python**: PEP 8 준수, 타입 힌트 사용
- **HTML**: 시맨틱 마크업, 접근성 고려

## 📞 지원 및 문의

### 문제 해결
- **GitHub Issues**: 버그 리포트, 기능 요청
- **Documentation**: README.md, 이 기능사양서 참조
- **테스트**: unit-tests-v1.0.4.html 실행

### 연락처
- **프로젝트 저장소**: https://github.com/gon1zau6jyun4liu5/world-trends-explorer
- **이슈 트래커**: GitHub Issues 사용
- **문서**: docs/ 폴더 참조

---

**📝 문서 정보**
- **최종 업데이트**: 2025-07-13
- **문서 버전**: v1.0.4
- **작성자**: World Trends Explorer Team
- **검토자**: Development Team

**🔄 변경 이력**
- v1.0.4: 지도 로딩 이슈 수정, 검색 섹션 복원, 유닛 테스트 추가
- v1.0.3: 세계지도 중심 디자인, 국가별 패널 추가
- v1.0.2: 기본 세계지도 기능 구현
- v1.0.1: 초기 프로토타입 완성