FROM python:3.13

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /workspace

# 필요한 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    default-mysql-client \
    redis-tools \
    pkg-config \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Poetry 설치
RUN pip install --upgrade pip && pip install poetry

# Poetry 가상환경 끄기
RUN poetry config virtualenvs.create false

# 프로젝트 메타 복사 및 의존성 설치
COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-root

# 전체 소스 복사

COPY . .

COPY ./script/startup.sh /workspace/script/startup.sh
RUN chmod +x /workspace/script/startup.sh

EXPOSE 8000
CMD ["sh", "/workspace/script/startup.sh"]
