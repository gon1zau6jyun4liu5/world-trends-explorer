#!/bin/bash

# World Trends Explorer 배포 스크립트

set -e

echo "🚀 World Trends Explorer 배포를 시작합니다..."

# 환경 변수 설정
ENV=${1:-production}
echo "배포 환경: $ENV"

# 빌드 디렉토리 생성
mkdir -p dist

# 프론트엔드 빌드
echo "📦 프론트엔드 빌드 중..."
cp -r frontend/* dist/

# 환경별 설정
if [ "$ENV" = "production" ]; then
    # 프로덕션 API URL로 변경
    sed -i 's|http://localhost:5000/api/trends|https://your-api-domain.com/api/trends|g' dist/js/api.js
fi

# Docker 빌드 (선택사항)
read -p "Docker 이미지를 빌드하시겠습니까? (y/N): " build_docker
if [[ $build_docker =~ ^[Yy]$ ]]; then
    echo "🐳 Docker 이미지 빌드 중..."
    docker-compose build
fi

echo "✅ 배포 준비가 완료되었습니다!"
echo "📁 빌드 파일: dist/"
echo "🌐 프로덕션 배포 가이드는 docs/DEPLOYMENT.md를 참조하세요."