import functools
import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)


def trace_llm_operation(operation_name: str):
    """LLM 작업 추적 데코레이터 (단순 로깅용)"""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                logger.info(f"Starting {operation_name}")
                result = await func(*args, **kwargs)
                logger.info(f"Completed {operation_name}")
                return result
            except Exception as e:
                logger.error(f"Failed {operation_name}: {e}")
                raise

        return wrapper

    return decorator
