# Makefile (환경변수 지원)
.PHONY: help build up down restart logs clean test redis-cli redis-backup env-check

help: ## 도움말 표시
	@echo "📚 Curriculum Platform - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

env-check: ## 환경변수 설정 확인
	@./script/env-check

setup: ## 초기 설정 (.env 파일 복사)
	@if [ ! -f .env ]; then \
		echo "📋 Creating .env from template..."; \
		cp .env.example .env; \
		echo "✅ .env file created!"; \
		echo "⚠️  Please edit .env file with your settings"; \
		echo "💡 Run 'make env-check' to verify"; \
	else \
		echo "✅ .env file already exists"; \
	fi

build: ## Docker 이미지 빌드
	@echo "🔨 Building Docker images..."
	docker-compose build

up: ## 모든 서비스 시작
	@echo "🚀 Starting all services..."
	@make env-check
	docker-compose up -d
	@echo "⏳ Waiting for services to be ready..."
	@sleep 10
	@echo "✅ Services are running!"
	@echo "   🌐 API: http://localhost:8000"
	@echo "   🔴 Redis Insight: http://localhost:8001"

down: ## 모든 서비스 중지
	@echo "🛑 Stopping all services..."
	docker-compose down

restart: ## 모든 서비스 재시작
	@echo "🔄 Restarting all services..."
	docker-compose restart

logs: ## 전체 로그 보기
	docker-compose logs -f

logs-app: ## 앱 로그만 보기
	docker-compose logs -f app

logs-redis: ## Redis 로그만 보기
	docker-compose logs -f redis

status: ## 서비스 상태 확인
	@echo "📊 Service Status:"
	docker-compose ps

redis-cli: ## Redis CLI 접속
	@echo "🔴 Connecting to Redis..."
	@chmod +x script/redis-cli
	@./script/redis-cli

redis-info: ## Redis 정보 확인
	@echo "🔴 Redis Information:"
	@chmod +x script/redis-info
	@./script/redis-info

redis-monitor: ## Redis 명령어 모니터링
	@echo "🔍 Starting Redis monitor..."
	@chmod +x script/redis-monitor
	@./script/redis-monitor

redis-backup: ## Redis 데이터 백업
	@echo "🔴 Creating Redis backup..."
	@chmod +x script/backup-redis
	@./script/backup-redis

redis-keys: ## Redis 키 목록 확인
	@if [ -f .env ]; then export $$(grep -v '^#' .env | xargs); fi; \
	echo "🔑 Redis keys:"; \
	docker-compose exec redis redis-cli -a "$$REDIS_PASSWORD" keys "*"

redis-flush: ## Redis 데이터 모두 삭제 (주의!)
	@echo "⚠️  This will delete ALL Redis data!"
	@chmod +x script/redis-flush
	@./script/redis-flush

clean: ## 모든 컨테이너, 볼륨 정리
	@echo "🧹 Cleaning up..."
	docker-compose down -v --remove-orphans
	docker-compose rm -f
	docker system prune -f

clean-all: ## 모든 것 정리 (이미지 포함)
	@echo "🧹 Deep cleaning..."
	docker-compose down -v --remove-orphans --rmi all
	docker system prune -af

test: ## 테스트 실행
	@echo "🧪 Running tests..."
	docker-compose exec app python -m pytest

shell: ## 앱 컨테이너에 Shell 접속
	docker-compose exec app bash

db-shell: ## 데이터베이스 Shell 접속  
	@if [ -f .env ]; then export $$(grep -v '^#' .env | xargs); fi; \
	docker-compose exec db mysql -u "$$DATABASE_NAME" -p"$$DATABASE_PASSWORD" "$$MYSQL_DATABASE"

migrate: ## 데이터베이스 마이그레이션
	docker-compose exec app alembic upgrade head

dev: setup up ## 개발환경 시작 (초기 설정 포함)
	@echo "🎉 Development environment is ready!"

# 기본 타겟
all: setup build up
