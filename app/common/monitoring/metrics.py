from prometheus_client import Counter, Gauge, Histogram, start_http_server
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# 사용자 메트릭
user_registrations_total = Counter(
    "user_registrations_total", "Total number of user registrations"
)

total_users_gauge = Gauge("total_users", "Total number of users in the system")

active_users_gauge = Gauge("active_users", "Number of currently active users")

# 커리큘럼 메트릭
curriculum_creations_total = Counter(
    "curriculum_creations_total", "Total number of curriculum creations"
)

total_curriculums_gauge = Gauge(
    "total_curriculums", "Total number of curriculums in the system"
)

public_curriculums_gauge = Gauge("public_curriculums", "Number of public curriculums")

# 학습 메트릭
summary_creations_total = Counter(
    "summary_creations_total", "Total number of summary creations"
)

total_summaries_gauge = Gauge(
    "total_summaries", "Total number of summaries in the system"
)

feedback_creations_total = Counter(
    "feedback_creations_total", "Total number of feedback creations"
)

total_feedbacks_gauge = Gauge(
    "total_feedbacks", "Total number of feedbacks in the system"
)

# 학습 통계 메트릭
average_completion_rate_gauge = Gauge(
    "average_completion_rate", "Average curriculum completion rate across all users"
)

average_feedback_score_gauge = Gauge(
    "average_feedback_score", "Average feedback score across all users"
)

active_learners_gauge = Gauge(
    "active_learners", "Number of users who created summaries in the last 7 days"
)

# 태그/카테고리 메트릭
tag_creations_total = Counter("tag_creations_total", "Total number of tag creations")

total_tags_gauge = Gauge("total_tags", "Total number of tags in the system")

total_categories_gauge = Gauge(
    "total_categories", "Total number of categories in the system"
)

active_categories_gauge = Gauge("active_categories", "Number of active categories")

curriculum_tag_assignments_total = Counter(
    "curriculum_tag_assignments_total", "Total number of curriculum-tag assignments"
)

curriculum_category_assignments_total = Counter(
    "curriculum_category_assignments_total",
    "Total number of curriculum-category assignments",
)

total_curriculum_tags_gauge = Gauge(
    "total_curriculum_tags", "Total number of curriculum-tag connections"
)

total_curriculum_categories_gauge = Gauge(
    "total_curriculum_categories", "Total number of curriculum-category connections"
)

popular_tags_gauge = Gauge("popular_tags", "Number of popular tags (usage_count >= 10)")

average_tags_per_curriculum_gauge = Gauge(
    "average_tags_per_curriculum", "Average number of tags per curriculum"
)

# Like 메트릭
like_creations_total = Counter("like_creations_total", "Total number of like creations")

total_likes_gauge = Gauge("total_likes", "Total number of likes in the system")

likes_per_curriculum_gauge = Gauge(
    "likes_per_curriculum_avg", "Average number of likes per curriculum"
)

# Bookmark 메트릭
bookmark_creations_total = Counter(
    "bookmark_creations_total", "Total number of bookmark creations"
)

total_bookmarks_gauge = Gauge(
    "total_bookmarks", "Total number of bookmarks in the system"
)

bookmarks_per_user_gauge = Gauge(
    "bookmarks_per_user_avg", "Average number of bookmarks per user"
)

# Comment 메트릭 (기존에 없다면 추가)
comment_creations_total = Counter(
    "comment_creations_total", "Total number of comment creations"
)

total_comments_gauge = Gauge("total_comments", "Total number of comments in the system")

comments_per_curriculum_gauge = Gauge(
    "comments_per_curriculum_avg", "Average number of comments per curriculum"
)

# Follow 메트릭
follow_creations_total = Counter(
    "follow_creations_total", "Total number of follow creations"
)

total_follows_gauge = Gauge(
    "total_follows", "Total number of follow relationships in the system"
)

followers_per_user_gauge = Gauge(
    "followers_per_user_avg", "Average number of followers per user"
)

# Social Engagement 메트릭
active_social_users_gauge = Gauge(
    "active_social_users", "Number of users who performed social actions in last 7 days"
)

social_engagement_rate_gauge = Gauge(
    "social_engagement_rate", "Percentage of users who engaged socially in last 7 days"
)

# 쿼리 성능 메트릭
db_query_duration = Histogram(
    "db_query_duration_seconds",
    "Database query execution time",
    ["query_type", "table", "operation"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)

db_query_total = Counter(
    "db_query_total",
    "Total number of database queries",
    ["query_type", "table", "operation", "status"],
)

db_connection_pool_size = Gauge(
    "db_connection_pool_size", "Current database connection pool size"
)

db_connection_pool_checked_out = Gauge(
    "db_connection_pool_checked_out", "Number of connections currently checked out"
)

db_connection_pool_overflow = Gauge(
    "db_connection_pool_overflow", "Number of connections in overflow"
)

api_request_duration = Histogram(
    "api_request_duration_seconds",
    "API request execution time",
    ["method", "endpoint", "status_code"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

api_request_total = Counter(
    "api_request_total",
    "Total number of API requests",
    ["method", "endpoint", "status_code"],
)

# 에러 메트릭
application_errors_total = Counter(
    "application_errors_total",
    "Total number of application errors",
    ["error_type", "module", "severity"],
)

# Redis 캐시 메트릭
redis_operations_total = Counter(
    "redis_operations_total",
    "Total number of Redis operations",
    ["operation", "status"],
)

redis_operation_duration = Histogram(
    "redis_operation_duration_seconds",
    "Redis operation execution time",
    ["operation"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5],
)

cache_hit_ratio = Gauge("cache_hit_ratio", "Cache hit ratio percentage")

# 메트릭 서버 상태
_metrics_server_port: Optional[int] = None


async def initialize_metrics_collector(port: int = 8000) -> None:
    """메트릭 수집 서버 초기화"""
    global _metrics_server_port

    if _metrics_server_port is not None:
        logger.warning(f"Metrics server already running on port {_metrics_server_port}")
        return

    try:
        start_http_server(port)
        _metrics_server_port = port
        logger.info(f"Prometheus metrics server started on port {port}")
    except Exception as e:
        logger.error(f"Failed to start metrics server: {e}")
        raise


async def shutdown_metrics_collector() -> None:
    """메트릭 수집 서버 종료"""
    global _metrics_server_port

    if _metrics_server_port is None:
        logger.info("Metrics server was not running")
        return

    # HTTP 서버는 자동으로 정리됨
    _metrics_server_port = None
    logger.info("Metrics server shutdown complete")


# 편의 함수들
def increment_user_registration() -> None:
    """회원가입 수 증가"""
    user_registrations_total.inc()


def set_total_users(count: int) -> None:
    """전체 사용자 수 설정"""
    total_users_gauge.set(count)


def set_active_users(count: int) -> None:
    """활성 사용자 수 설정"""
    active_users_gauge.set(count)


def increment_curriculum_creation() -> None:
    """커리큘럼 생성 수 증가"""
    curriculum_creations_total.inc()


def set_total_curriculums(count: int) -> None:
    """전체 커리큘럼 수 설정"""
    total_curriculums_gauge.set(count)


def set_public_curriculums(count: int) -> None:
    """공개 커리큘럼 수 설정"""
    public_curriculums_gauge.set(count)


def increment_summary_creation() -> None:
    """요약 생성 수 증가"""
    summary_creations_total.inc()


def set_total_summaries(count: int) -> None:
    """전체 요약 수 설정"""
    total_summaries_gauge.set(count)


def increment_feedback_creation() -> None:
    """피드백 생성 수 증가"""
    feedback_creations_total.inc()


def set_total_feedbacks(count: int) -> None:
    """전체 피드백 수 설정"""
    total_feedbacks_gauge.set(count)


def set_average_completion_rate(rate: float) -> None:
    """평균 완료율 설정"""
    average_completion_rate_gauge.set(rate)


def set_average_feedback_score(score: float) -> None:
    """평균 피드백 점수 설정"""
    average_feedback_score_gauge.set(score)


def set_active_learners(count: int) -> None:
    """활성 학습자 수 설정"""
    active_learners_gauge.set(count)


def increment_tag_creation() -> None:
    """태그 생성 수 증가"""
    tag_creations_total.inc()


def set_total_tags(count: int) -> None:
    """전체 태그 수 설정"""
    total_tags_gauge.set(count)


def set_total_categories(count: int) -> None:
    """전체 카테고리 수 설정"""
    total_categories_gauge.set(count)


def set_active_categories(count: int) -> None:
    """활성 카테고리 수 설정"""
    active_categories_gauge.set(count)


def increment_curriculum_tag_assignment() -> None:
    """커리큘럼-태그 연결 수 증가"""
    curriculum_tag_assignments_total.inc()


def increment_curriculum_category_assignment() -> None:
    """커리큘럼-카테고리 연결 수 증가"""
    curriculum_category_assignments_total.inc()


def set_total_curriculum_tags(count: int) -> None:
    """전체 커리큘럼-태그 연결 수 설정"""
    total_curriculum_tags_gauge.set(count)


def set_total_curriculum_categories(count: int) -> None:
    """전체 커리큘럼-카테고리 연결 수 설정"""
    total_curriculum_categories_gauge.set(count)


def set_popular_tags(count: int) -> None:
    """인기 태그 수 설정"""
    popular_tags_gauge.set(count)


def set_average_tags_per_curriculum(avg: float) -> None:
    """커리큘럼당 평균 태그 수 설정"""
    average_tags_per_curriculum_gauge.set(avg)


# Social metrics 편의 함수
def increment_like_creation() -> None:
    """좋아요 생성 수 증가"""
    like_creations_total.inc()


def set_total_likes(count: int) -> None:
    """전체 좋아요 수 설정"""
    total_likes_gauge.set(count)


def set_likes_per_curriculum(avg: float) -> None:
    """커리큘럼당 평균 좋아요 수 설정"""
    likes_per_curriculum_gauge.set(avg)


def increment_bookmark_creation() -> None:
    """북마크 생성 수 증가"""
    bookmark_creations_total.inc()


def set_total_bookmarks(count: int) -> None:
    """전체 북마크 수 설정"""
    total_bookmarks_gauge.set(count)


def set_bookmarks_per_user(avg: float) -> None:
    """사용자당 평균 북마크 수 설정"""
    bookmarks_per_user_gauge.set(avg)


def increment_comment_creation() -> None:
    """댓글 생성 수 증가"""
    comment_creations_total.inc()


def set_total_comments(count: int) -> None:
    """전체 댓글 수 설정"""
    total_comments_gauge.set(count)


def set_comments_per_curriculum(avg: float) -> None:
    """커리큘럼당 평균 댓글 수 설정"""
    comments_per_curriculum_gauge.set(avg)


def increment_follow_creation() -> None:
    """팔로우 생성 수 증가"""
    follow_creations_total.inc()


def set_total_follows(count: int) -> None:
    """전체 팔로우 수 설정"""
    total_follows_gauge.set(count)


def set_followers_per_user(avg: float) -> None:
    """사용자당 평균 팔로워 수 설정"""
    followers_per_user_gauge.set(avg)


def set_active_social_users(count: int) -> None:
    """활성 소셜 사용자 수 설정"""
    active_social_users_gauge.set(count)


def set_social_engagement_rate(rate: float) -> None:
    """소셜 참여율 설정"""
    social_engagement_rate_gauge.set(rate)


# DB 성능 편의 함수
def record_db_query(
    query_type: str,
    table: str,
    operation: str,
    duration: float,
    status: str = "success",
) -> None:
    """DB 쿼리 메트릭 기록"""
    db_query_duration.labels(
        query_type=query_type, table=table, operation=operation
    ).observe(duration)
    db_query_total.labels(
        query_type=query_type, table=table, operation=operation, status=status
    ).inc()


def set_db_connection_metrics(pool_size: int, checked_out: int, overflow: int) -> None:
    """DB 연결 풀 메트릭 설정"""
    db_connection_pool_size.set(pool_size)
    db_connection_pool_checked_out.set(checked_out)
    db_connection_pool_overflow.set(overflow)


# API 성능 편의 함수
def record_api_request(
    method: str, endpoint: str, status_code: int, duration: float
) -> None:
    """API 요청 메트릭 기록"""
    api_request_duration.labels(
        method=method, endpoint=endpoint, status_code=status_code
    ).observe(duration)
    api_request_total.labels(
        method=method, endpoint=endpoint, status_code=status_code
    ).inc()


def increment_application_error(
    error_type: str, module: str, severity: str = "error"
) -> None:
    """애플리케이션 에러 수 증가"""
    application_errors_total.labels(
        error_type=error_type, module=module, severity=severity
    ).inc()


# Redis 편의 함수
def record_redis_operation(
    operation: str, duration: float, status: str = "success"
) -> None:
    """Redis 작업 메트릭 기록"""
    redis_operations_total.labels(operation=operation, status=status).inc()
    redis_operation_duration.labels(operation=operation).observe(duration)


def set_cache_hit_ratio(ratio: float) -> None:
    """캐시 적중률 설정"""
    cache_hit_ratio.set(ratio)
