import time
import functools
import logging
from typing import Any, Callable, List, Optional, Tuple, TypeVar, cast
from contextlib import asynccontextmanager

from app.common.monitoring.metrics import (
    record_db_query,
    record_api_request,
    increment_application_error,
    record_redis_operation,
)
from app.modules.social.domain.entity.like import Like
from app.modules.social.infrastructure.repository.like_repo import LikeRepository

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def monitor_db_query(query_type: str, table: str, operation: str):
    """DB 쿼리 성능 모니터링 데코레이터"""

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            status = "success"

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = "error"
                logger.error(f"DB query error in {func.__name__}: {e}")
                increment_application_error(
                    error_type=type(e).__name__, module="database", severity="error"
                )
                raise
            finally:
                duration = time.time() - start_time
                record_db_query(query_type, table, operation, duration, status)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            status = "success"

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status = "error"
                logger.error(f"DB query error in {func.__name__}: {e}")
                increment_application_error(
                    error_type=type(e).__name__, module="database", severity="error"
                )
                raise
            finally:
                duration = time.time() - start_time
                record_db_query(query_type, table, operation, duration, status)

        # 함수가 코루틴인지 확인
        import inspect

        if inspect.iscoroutinefunction(func):
            return cast(F, async_wrapper)
        else:
            return cast(F, sync_wrapper)

    return decorator


def monitor_api_request(endpoint: str):
    """API 요청 성능 모니터링 데코레이터"""

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            status_code = 200
            method = "GET"  # 기본값, 실제로는 request에서 가져와야 함

            try:
                # FastAPI의 경우 request 객체 찾기
                for arg in args:
                    if hasattr(arg, "method"):
                        method = arg.method
                        break

                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status_code = getattr(e, "status_code", 500)
                logger.error(f"API error in {func.__name__}: {e}")
                increment_application_error(
                    error_type=type(e).__name__, module="api", severity="error"
                )
                raise
            finally:
                duration = time.time() - start_time
                record_api_request(method, endpoint, status_code, duration)

        return cast(F, async_wrapper)

    return decorator


def monitor_redis_operation(operation: str):
    """Redis 작업 성능 모니터링 데코레이터"""

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            status = "success"

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = "error"
                logger.error(f"Redis operation error in {func.__name__}: {e}")
                increment_application_error(
                    error_type=type(e).__name__, module="redis", severity="error"
                )
                raise
            finally:
                duration = time.time() - start_time
                record_redis_operation(operation, duration, status)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            status = "success"

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status = "error"
                logger.error(f"Redis operation error in {func.__name__}: {e}")
                increment_application_error(
                    error_type=type(e).__name__, module="redis", severity="error"
                )
                raise
            finally:
                duration = time.time() - start_time
                record_redis_operation(operation, duration, status)

        import inspect

        if inspect.iscoroutinefunction(func):
            return cast(F, async_wrapper)
        else:
            return cast(F, sync_wrapper)

    return decorator


@asynccontextmanager
async def monitor_db_transaction(operation_name: str):
    """DB 트랜잭션 모니터링 컨텍스트 매니저"""
    start_time = time.time()
    status = "success"

    try:
        yield
    except Exception as e:
        status = "error"
        logger.error(f"DB transaction error in {operation_name}: {e}")
        increment_application_error(
            error_type=type(e).__name__, module="database", severity="error"
        )
        raise
    finally:
        duration = time.time() - start_time
        record_db_query("transaction", "multiple", operation_name, duration, status)


# Repository 메서드에 적용 예시
class LikeRepositoryWithMonitoring(LikeRepository):
    """모니터링이 적용된 Like Repository"""

    @monitor_db_query("insert", "likes", "create")
    async def save(self, like: Like) -> None:
        """좋아요 저장"""
        return await super().save(like)

    @monitor_db_query("select", "likes", "find_by_id")
    async def find_by_id(self, like_id: str) -> Optional[Like]:
        """ID로 좋아요 조회"""
        return await super().find_by_id(like_id)

    @monitor_db_query("select", "likes", "find_by_curriculum_and_user")
    async def find_by_curriculum_and_user(
        self, curriculum_id: str, user_id: str
    ) -> Optional[Like]:
        """커리큘럼과 사용자로 좋아요 조회"""
        return await super().find_by_curriculum_and_user(curriculum_id, user_id)

    @monitor_db_query("select", "likes", "find_by_curriculum")
    async def find_by_curriculum(
        self, curriculum_id: str, page: int = 1, items_per_page: int = 10
    ) -> Tuple[int, List[Like]]:
        """커리큘럼의 모든 좋아요 조회 (페이징)"""
        return await super().find_by_curriculum(curriculum_id, page, items_per_page)

    @monitor_db_query("select", "likes", "find_by_user")
    async def find_by_user(
        self, user_id: str, page: int = 1, items_per_page: int = 10
    ) -> Tuple[int, List[Like]]:
        """사용자의 모든 좋아요 조회 (페이징)"""
        return await super().find_by_user(user_id, page, items_per_page)

    @monitor_db_query("delete", "likes", "delete")
    async def delete(self, like_id: str) -> None:
        """좋아요 삭제"""
        return await super().delete(like_id)

    @monitor_db_query("delete", "likes", "delete_by_curriculum_and_user")
    async def delete_by_curriculum_and_user(
        self, curriculum_id: str, user_id: str
    ) -> None:
        """커리큘럼과 사용자로 좋아요 삭제"""
        return await super().delete_by_curriculum_and_user(curriculum_id, user_id)

    @monitor_db_query("select", "likes", "count_by_curriculum")
    async def count_by_curriculum(self, curriculum_id: str) -> int:
        """커리큘럼의 좋아요 수 조회"""
        return await super().count_by_curriculum(curriculum_id)

    @monitor_db_query("select", "likes", "count_by_user")
    async def count_by_user(self, user_id: str) -> int:
        """사용자의 좋아요 수 조회"""
        return await super().count_by_user(user_id)

    @monitor_db_query("select", "likes", "exists_by_curriculum_and_user")
    async def exists_by_curriculum_and_user(
        self, curriculum_id: str, user_id: str
    ) -> bool:
        """커리큘럼-사용자 좋아요 존재 여부 확인"""
        return await super().exists_by_curriculum_and_user(curriculum_id, user_id)
