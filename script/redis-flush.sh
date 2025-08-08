#!/bin/bash

# .env 파일에서 환경변수 로드
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

echo "⚠️  WARNING: This will delete ALL Redis data!"
echo "🗑️  This action cannot be undone!"
echo ""
read -p "Are you absolutely sure? Type 'DELETE ALL' to continue: " confirm

if [ "$confirm" = "DELETE ALL" ]; then
    echo "🔴 Flushing all Redis data..."
    docker-compose exec redis redis-cli -a "${REDIS_PASSWORD}" flushall
    echo "✅ All Redis data has been deleted"
else
    echo "❌ Operation cancelled"
fi
