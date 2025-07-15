# SerpAPI 빠른 설정 가이드

World Trends Explorer에서 실제 Google Trends 데이터를 사용하려면 SerpAPI를 설정해야 합니다.

## 🚀 5분 안에 설정하기

### 1. SerpAPI 무료 계정 만들기
1. https://serpapi.com/ 방문
2. "Sign Up" 클릭
3. 이메일로 가입 (무료, 신용카드 불필요)
4. Dashboard에서 API Key 복사

### 2. API Key 설정하기

#### 방법 A: .env 파일 사용 (권장) ✅
```bash
cd backend
cp .env.example .env
# .env 파일을 열어서 SERPAPI_API_KEY를 실제 키로 변경
```

#### 방법 B: 터미널에서 직접 설정
```bash
# macOS/Linux
export SERPAPI_API_KEY="your-api-key-here"

# Windows
set SERPAPI_API_KEY=your-api-key-here
```

### 3. 서버 실행하기
```bash
# 루트 디렉토리에서
chmod +x start_serpapi.sh
./start_serpapi.sh
```

## ❓ 자주 묻는 질문

### Q: 매번 export를 실행해야 하나요?
A: 아니요! `.env` 파일을 사용하면 한 번만 설정하면 됩니다.

### Q: API Key를 어디서 찾나요?
A: SerpAPI 로그인 후 https://serpapi.com/manage-api-key 에서 확인

### Q: 무료로 얼마나 사용할 수 있나요?
A: 월 100회 검색 무료 (충분히 테스트 가능)

### Q: Mock 데이터가 계속 나와요
A: API Key가 제대로 설정되지 않은 경우입니다. `.env` 파일을 확인하세요.

## 🔧 문제 해결

1. **".env 파일을 찾을 수 없음" 오류**
   ```bash
   cd backend
   ls -la  # .env 파일이 있는지 확인
   ```

2. **"API key not configured" 오류**
   - `.env` 파일의 API 키가 정확한지 확인
   - 따옴표 없이 입력: `SERPAPI_API_KEY=abc123` (O)
   - `SERPAPI_API_KEY="abc123"` (X)

3. **서버가 시작되지 않음**
   ```bash
   cd backend
   pip install python-dotenv requests
   ```

## 📝 전체 예시

```bash
# 1. 프로젝트 클론
git clone https://github.com/yourusername/world-trends-explorer.git
cd world-trends-explorer

# 2. 브랜치 변경
git checkout feature/serpapi-integration

# 3. .env 파일 설정
cd backend
cp .env.example .env
nano .env  # SERPAPI_API_KEY 수정

# 4. 서버 실행
cd ..
./start_serpapi.sh

# 5. 브라우저에서 frontend/index.html 열기
```

## 🎯 확인 방법

서버 시작 시:
- ✅ "SERPAPI_API_KEY configured" → 성공!
- ⚠️ "WARNING: SERPAPI_API_KEY not found" → 설정 필요

브라우저에서:
- http://localhost:5000/api/trends/health 접속
- `"api_key_configured": true` 확인

---

더 자세한 내용은 [docs/SERPAPI_SETUP.md](docs/SERPAPI_SETUP.md) 참조
