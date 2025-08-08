echo "🔍 Environment Variables Check"
echo "=============================="

if [ -f .env ]; then
    echo "✅ .env file found"
    
    # 필수 환경변수 확인
    REQUIRED_VARS=(
        "APP_NAME"
        "MYSQL_DATABASE" 
        "DATABASE_NAME"
        "DATABASE_PASSWORD"
        "REDIS_PASSWORD"
        "SECRET_KEY"
    )
    
    echo ""
    echo "📋 Required Variables:"
    
    for var in "${REQUIRED_VARS[@]}"; do
        if grep -q "^${var}=" .env; then
            # 비밀번호는 마스킹해서 표시
            if [[ $var == *"PASSWORD"* ]] || [[ $var == *"SECRET"* ]]; then
                echo "  ✅ $var=***masked***"
            else
                value=$(grep "^${var}=" .env | cut -d'=' -f2)
                echo "  ✅ $var=$value"
            fi
        else
            echo "  ❌ $var=NOT SET"
        fi
    done
    
    echo ""
    echo "🔧 Optional Variables:"
    OPTIONAL_VARS=("LLM_API_KEY" "LOG_LEVEL" "ENVIRONMENT")
    
    for var in "${OPTIONAL_VARS[@]}"; do
        if grep -q "^${var}=" .env; then
            if [[ $var == *"KEY"* ]]; then
                echo "  ✅ $var=***masked***"
            else
                value=$(grep "^${var}=" .env | cut -d'=' -f2)
                echo "  ✅ $var=$value"
            fi
        else
            echo "  ⚠️  $var=not set (using default)"
        fi
    done
    
else
    echo "❌ .env file not found!"
    echo "💡 Copy .env.example to .env and configure it"
fi
