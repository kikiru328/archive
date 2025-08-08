#!/bin/bash

# .env 파일에서 환경변수 로드
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

echo "🔴 Connecting to Redis CLI..."

# Docker Compose가 실행 중인지 확인
if ! docker-compose ps redis | grep -q "Up"; then
    echo "❌ Redis container is not running"
    echo "💡 Start with: docker-compose up -d redis"
    exit 1
fi

# Redis CLI 접속 (환경변수 사용)
docker-compose exec redis redis-cli -a "${REDIS_PASSWORD}"
