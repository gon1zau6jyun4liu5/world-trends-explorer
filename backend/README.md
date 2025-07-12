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
# 서버: http://localhost:5555
```

## 🔧 각 서버의 용도

### app.py (메인 서버)
- **실제 Google Trends API** 연동
- **프로덕션 환경**에서 사용
- 실시간 트렌드 데이터 제공
- API 요청 제한 있음

### mock_server.py (테스트 서버)  
- **가짜 데이터** 제공 (현실적인 패턴)
- **개발/테스트** 환경에서 사용
- API 제한 없이 무제한 테스트 가능
- 일관된 테스트 결과 보장
- 네트워크 연결 불필요

## 💡 사용 시나리오

### 개발 중일 때
```bash
# Mock 서버로 빠른 개발
python mock_server.py
```

### 실제 데이터 확인할 때
```bash
# 실제 API로 데이터 검증
python app.py
```

### 데모/프레젠테이션
```bash
# 안정적인 Mock 데이터로 시연
python mock_server.py
```

## 🔄 프론트엔드 연결

프론트엔드에서 API URL 변경:

### 실제 API 사용
```javascript
// frontend/js/api.js
const baseURL = 'http://localhost:5000/api/trends';
```

### Mock API 사용  
```javascript
// frontend/js/api.js
const baseURL = 'http://localhost:5555/api/trends';
```

## 🐛 문제 해결

### Google Trends API 에러 시
1. Mock 서버로 전환: `python mock_server.py`
2. 프론트엔드 URL을 `:5555`로 변경
3. 정상 작동 확인

### 개발 속도가 느릴 때
- Mock 서버 사용으로 API 제한 없이 개발
- 최종 테스트만 실제 API로 검증

---
**권장사항**: 두 서버 모두 유지하여 개발 유연성 확보