# .env 파일에서 환경변수 로드
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

echo "🔍 Starting Redis monitor..."
echo "📝 All Redis commands will be displayed in real-time"
echo "🛑 Press Ctrl+C to stop monitoring"
echo ""

docker-compose exec redis redis-cli -a "${REDIS_PASSWORD}" monitor
