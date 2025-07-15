# SerpAPI 설정 가이드

## 개요
World Trends Explorer는 Google Trends 데이터를 가져오기 위해 SerpAPI를 사용합니다.

## 1. SerpAPI 계정 생성

1. https://serpapi.com/ 방문
2. 무료 계정 생성 (월 100회 무료 검색 제공)
3. Dashboard에서 API Key 복사

## 2. API Key 설정 방법

### 방법 1: .env 파일 사용 (권장)

```bash
# backend 디렉토리로 이동
cd backend

# .env.example을 .env로 복사
cp .env.example .env

# .env 파일 편집
nano .env  # 또는 원하는 텍스트 에디터 사용
```

`.env` 파일 내용:
```
SERPAPI_API_KEY=your-actual-api-key-here
FLASK_ENV=development
FLASK_DEBUG=True
```

### 방법 2: 환경 변수 설정

#### macOS/Linux:
```bash
# 터미널에서 임시 설정 (현재 세션만)
export SERPAPI_API_KEY="your-api-key-here"

# 영구 설정 (~/.zshrc 또는 ~/.bashrc에 추가)
echo 'export SERPAPI_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

#### Windows:
```bash
# Command Prompt에서
setx SERPAPI_API_KEY "your-api-key-here"

# PowerShell에서
[Environment]::SetEnvironmentVariable("SERPAPI_API_KEY", "your-api-key-here", "User")
```

## 3. 서버 실행

```bash
# backend 디렉토리에서
cd backend

# 가상환경 활성화
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate  # Windows

# SerpAPI 버전 서버 실행
python app_serpapi.py
```

## 4. 확인 방법

1. 서버 시작 시 메시지 확인:
   - ✅ "SERPAPI_API_KEY configured" - 정상 설정됨
   - ⚠️ "WARNING: SERPAPI_API_KEY not found" - 설정 필요

2. Health check API 호출:
   ```bash
   curl http://localhost:5000/api/trends/health
   ```
   응답에서 `"api_key_configured": true` 확인

## 5. 문제 해결

### API Key가 인식되지 않는 경우

1. `.env` 파일이 `backend` 디렉토리에 있는지 확인
2. `.env` 파일의 내용이 올바른지 확인 (공백, 따옴표 주의)
3. 서버를 재시작

### Mock 데이터가 표시되는 경우

- API Key가 설정되지 않았거나 잘못된 경우 자동으로 Mock 데이터 표시
- 응답에 `"note": "Mock data - Configure SERPAPI_API_KEY for real data"` 포함

## 6. 보안 주의사항

- `.env` 파일을 절대 Git에 커밋하지 마세요
- API Key를 공개 저장소에 노출하지 마세요
- `.gitignore`에 `.env`가 포함되어 있는지 확인

## 7. API 사용량 관리

- 무료 계정: 월 100회 검색
- 검색 결과는 자동으로 5분간 캐시됨
- https://serpapi.com/dashboard 에서 사용량 확인 가능
