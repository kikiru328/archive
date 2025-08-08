#!/bin/bash

# .env 파일에서 환경변수 로드
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

BACKUP_DIR="./backups/redis"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 백업 디렉토리 생성
mkdir -p $BACKUP_DIR

echo "🔴 Creating Redis backup..."

# Redis 컨테이너가 실행 중인지 확인
if ! docker-compose ps redis | grep -q "Up"; then
    echo "❌ Redis container is not running"
    exit 1
fi

# 백업 실행 (환경변수 사용)
if docker-compose exec redis redis-cli -a "${REDIS_PASSWORD}" --rdb /tmp/backup.rdb; then
    # 백업 파일 복사
    docker-compose cp redis:/tmp/backup.rdb "$BACKUP_DIR/redis_backup_$TIMESTAMP.rdb"
    echo "✅ Redis backup saved to: $BACKUP_DIR/redis_backup_$TIMESTAMP.rdb"
    
    # 임시 파일 정리
    docker-compose exec redis rm -f /tmp/backup.rdb
    
    # 백업 파일 크기 확인
    if [ -f "$BACKUP_DIR/redis_backup_$TIMESTAMP.rdb" ]; then
        SIZE=$(du -h "$BACKUP_DIR/redis_backup_$TIMESTAMP.rdb" | cut -f1)
        echo "📊 Backup size: $SIZE"
    fi
else
    echo "❌ Redis backup failed"
    exit 1
fi
