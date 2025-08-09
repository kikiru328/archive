from prometheus_client import Counter, Gauge, start_http_server
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# 메트릭 정의
user_registrations_total = Counter(
    "user_registrations_total", "Total number of user registrations"
)

total_users_gauge = Gauge("total_users", "Total number of users in the system")

active_users_gauge = Gauge("active_users", "Number of currently active users")


curriculum_creations_total = Counter(
    "curriculum_creations_total", "Total number of curriculum creations"
)

total_curriculums_gauge = Gauge(
    "total_curriculums", "Total number of curriculums in the system"
)

public_curriculums_gauge = Gauge("public_curriculums", "Number of public curriculums")

private_curriculums_gauge = Gauge(
    "private_curriculums", "Number of private curriculums"
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


def set_private_curriculums(count: int) -> None:
    """비공개 커리큘럼 수 설정"""
    private_curriculums_gauge.set(count)
