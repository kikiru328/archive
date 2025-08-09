from prometheus_client import Counter, Gauge, start_http_server
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
