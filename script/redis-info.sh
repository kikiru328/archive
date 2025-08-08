#!/bin/bash

# .env 파일에서 환경변수 로드
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

echo "🔴 Redis Server Information:"
echo "================================="

# 기본 정보
echo "📊 Server Info:"
docker-compose exec redis redis-cli -a "${REDIS_PASSWORD}" info server | head -10

echo ""
echo "💾 Memory Info:"
docker-compose exec redis redis-cli -a "${REDIS_PASSWORD}" info memory | grep -E "(used_memory_human|maxmemory_human)"

echo ""
echo "🔗 Clients Info:"
docker-compose exec redis redis-cli -a "${REDIS_PASSWORD}" info clients

echo ""
echo "📈 Stats:"
docker-compose exec redis redis-cli -a "${REDIS_PASSWORD}" info stats | head -5

echo ""
echo "🗂️ Keyspace Info:"
docker-compose exec redis redis-cli -a "${REDIS_PASSWORD}" info keyspace
