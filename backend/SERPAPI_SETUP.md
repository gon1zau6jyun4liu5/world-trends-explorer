# 환경 변수 설정 가이드

## SerpAPI 키 설정 (필수!)

World Trends Explorer는 Google Trends 데이터를 가져오기 위해 SerpAPI를 사용합니다.

### 1. SerpAPI 키 얻기
1. https://serpapi.com 에서 회원가입
2. Dashboard에서 API 키 복사

### 2. 환경 변수 설정

#### Linux/Mac:
```bash
export SERPAPI_KEY="your_serpapi_key_here"
```

#### Windows:
```bash
set SERPAPI_KEY=your_serpapi_key_here
```

#### .env 파일 사용 (권장):
```bash
# backend/.env
SERPAPI_KEY=your_serpapi_key_here
FLASK_ENV=production
FLASK_DEBUG=False
```

### 3. 실행
```bash
cd backend
python app.py
```

### 중요
- **SerpAPI 키 없이는 실제 트렌드 데이터를 가져올 수 없습니다**
- 무료 계정은 월 100회 검색 제한
- 키는 절대 GitHub에 커밋하지 마세요
