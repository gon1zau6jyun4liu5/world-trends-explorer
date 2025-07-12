# Docker 설정 가이드

## 개요

World Trends Explorer를 Docker 컨테이너로 실행하는 방법을 설명합니다.

## Docker Compose 설정

### docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - FLASK_DEBUG=False
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - trends-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - trends-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - trends-network

volumes:
  redis_data:

networks:
  trends-network:
    driver: bridge
```

## Dockerfile 설정

### 백엔드 Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 로그 디렉토리 생성
RUN mkdir -p logs

# 포트 노출
EXPOSE 5000

# 헬스체크 추가
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/trends/health || exit 1

# 애플리케이션 실행
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5000", "backend_server:app"]
```

### 프론트엔드 Dockerfile

```dockerfile
# frontend/Dockerfile
FROM nginx:alpine

# 기본 nginx 설정 제거
RUN rm /etc/nginx/conf.d/default.conf

# 애플리케이션 파일 복사
COPY . /usr/share/nginx/html

# nginx 설정 복사
COPY nginx.conf /etc/nginx/conf.d/

# 포트 노출
EXPOSE 80

# nginx 시작
CMD ["nginx", "-g", "daemon off;"]
```

### nginx.conf

```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip 압축 활성화
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # 정적 파일 캐싱
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # HTML 파일은 캐싱하지 않음
    location ~* \.html$ {
        expires -1;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }

    # API 요청을 백엔드로 프록시
    location /api/ {
        proxy_pass http://backend:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # SPA를 위한 fallback
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

## 실행 방법

### 1. 전체 스택 실행

```bash
# 백그라운드에서 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 특정 서비스 로그 확인
docker-compose logs -f backend
```

### 2. 개별 서비스 실행

```bash
# 백엔드만 실행
docker-compose up backend redis

# 프론트엔드만 실행
docker-compose up frontend
```

### 3. 빌드 및 실행

```bash
# 이미지 다시 빌드
docker-compose build

# 빌드 후 실행
docker-compose up --build
```

## 개발 환경 설정

### docker-compose.dev.yml

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=development
      - FLASK_DEBUG=True
    volumes:
      - ./backend:/app
      - ./logs:/app/logs
    restart: unless-stopped

  frontend:
    image: nginx:alpine
    ports:
      - "8000:80"
    volumes:
      - ./frontend:/usr/share/nginx/html
    restart: unless-stopped
```

### 개발 환경 실행

```bash
docker-compose -f docker-compose.dev.yml up
```

## 프로덕션 최적화

### 멀티 스테이지 빌드

```dockerfile
# 프로덕션용 최적화된 Dockerfile
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

# 사용자 생성
RUN useradd --create-home --shell /bin/bash app

# 빌드된 패키지 복사
COPY --from=builder /root/.local /home/app/.local

# 애플리케이션 코드 복사
COPY . .
RUN chown -R app:app /app

# 사용자 변경
USER app

# PATH 업데이트
ENV PATH=/home/app/.local/bin:$PATH

EXPOSE 5000

CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5000", "backend_server:app"]
```

## 모니터링 설정

### docker-compose.monitoring.yml

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    networks:
      - trends-network

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    networks:
      - trends-network

volumes:
  grafana_data:

networks:
  trends-network:
    external: true
```

## 유용한 명령어

### 관리 명령어

```bash
# 모든 컨테이너 중지
docker-compose down

# 볼륨까지 삭제
docker-compose down -v

# 사용하지 않는 이미지 정리
docker image prune -f

# 컨테이너 내부 접속
docker-compose exec backend bash
docker-compose exec frontend sh

# 로그 확인
docker-compose logs --tail=100 backend

# 리소스 사용량 확인
docker stats
```

### 백업 및 복원

```bash
# Redis 데이터 백업
docker-compose exec redis redis-cli BGSAVE

# 볼륨 백업
docker run --rm -v trends_redis_data:/data -v $(pwd):/backup alpine tar czf /backup/redis_backup.tar.gz -C /data .

# 볼륨 복원
docker run --rm -v trends_redis_data:/data -v $(pwd):/backup alpine tar xzf /backup/redis_backup.tar.gz -C /data
```

## 트러블슈팅

### 일반적인 문제

1. **포트 충돌**
   ```bash
   # 포트 사용 확인
   netstat -tulpn | grep :5000
   
   # 포트 변경
   docker-compose -p custom_name up
   ```

2. **권한 문제**
   ```bash
   # 로그 디렉토리 권한 설정
   chmod 755 logs/
   chown -R 1000:1000 logs/
   ```

3. **메모리 부족**
   ```bash
   # 메모리 제한 설정
   docker-compose up --memory=1g
   ```

### 로그 분석

```bash
# 에러 로그만 확인
docker-compose logs backend | grep ERROR

# 실시간 로그 모니터링
docker-compose logs -f --tail=0

# 특정 시간 이후 로그
docker-compose logs --since="2025-07-12T10:00:00"
```