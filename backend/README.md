# 🌍 World Trends Explorer - Backend Guide

## 🚀 서버 실행 방법

### 1. 실제 Google Trends API 서버 (기본)
```bash
# 실제 Google Trends 데이터 사용
cd backend
python app.py
# 서버: http://localhost:5000
```

### 2. Mock 테스트 서버 (개발용)
```bash
# 테스트/개발용 가짜 데이터 사용
cd backend  
python mock_server.py
# 서버: http://localhost:5001
```

## 🔧 각 서버의 용도

### app.py (메인 서버) - 포트 5000
- **실제 Google Trends API** 연동
- **프로덕션 환경**에서 사용
- 실시간 트렌드 데이터 제공
- API 요청 제한 있음
- 인터넷 연결 필요

### mock_server.py (테스트 서버) - 포트 5001
- **가짜 데이터** 제공 (현실적인 패턴)
- **개발/테스트** 환경에서 사용
- API 제한 없이 무제한 테스트 가능
- 일관된 테스트 결과 보장
- 네트워크 연결 불필요

## 💡 사용 시나리오

### 개발 중일 때
```bash
# Mock 서버로 빠른 개발 (포트 5001)
python mock_server.py
```

### 실제 데이터 확인할 때
```bash
# 실제 API로 데이터 검증 (포트 5000)
python app.py
```

### 데모/프레젠테이션
```bash
# 안정적인 Mock 데이터로 시연 (포트 5001)
python mock_server.py
```

### 두 서버 동시 실행
```bash
# 터미널 1: 실제 API
cd backend && python app.py

# 터미널 2: Mock API
cd backend && python mock_server.py

# 이제 두 서버가 동시에 실행됩니다!
# 실제 API: http://localhost:5000
# Mock API: http://localhost:5001
```

## 🔄 프론트엔드 연결

프론트엔드에서 API 전환:

### 브라우저 콘솔에서 API 전환
```javascript
// 실제 API 사용 (기본)
trendsAPI.switchToRealAPI();

// Mock API로 전환  
trendsAPI.switchToMockAPI();

// 현재 모드 확인
console.log('Current mode:', trendsAPI.getCurrentMode());
```

### 수동으로 API URL 변경
```javascript
// frontend/js/api.js에서 직접 변경

// 실제 API 사용
const baseURL = 'http://localhost:5000/api/trends';

// Mock API 사용  
const baseURL = 'http://localhost:5001/api/trends';
```

## 🐛 문제 해결

### Google Trends API 에러 시
1. Mock 서버로 전환: `python mock_server.py`
2. 브라우저에서: `trendsAPI.switchToMockAPI()`
3. 정상 작동 확인

### 개발 속도가 느릴 때
- Mock 서버 사용으로 API 제한 없이 개발
- 최종 테스트만 실제 API로 검증

### 포트 충돌 해결됨 ✅
- **실제 API**: 포트 5000
- **Mock API**: 포트 5001
- 이제 두 서버를 동시에 실행 가능!

## 📊 서버 상태 확인

```bash
# 실제 API 상태 확인
curl http://localhost:5000/api/trends/health

# Mock API 상태 확인
curl http://localhost:5001/api/trends/health

# 키워드 검색 테스트
curl "http://localhost:5000/api/trends/search?keyword=cryptocurrency&geo=US"
curl "http://localhost:5001/api/trends/search?keyword=cryptocurrency&geo=US"
```

## 🎯 권장 워크플로우

1. **개발 단계**: Mock API (5001) 사용으로 빠른 개발
2. **테스트 단계**: 실제 API (5000)로 실제 데이터 검증
3. **데모 단계**: Mock API (5001)로 안정적인 시연
4. **프로덕션**: 실제 API (5000)로 배포

---
**권장사항**: 두 서버 모두 유지하여 개발 유연성 확보 🚀