import logging
from typing import Optional, Dict, Any
from langfuse import Langfuse, get_client
from app.core.config import get_settings
from langfuse.langchain import CallbackHandler
from typing import ContextManager

logger = logging.getLogger(__name__)
settings = get_settings()


class LangfuseManager:
    """Langfuse 연동 관리 클래스"""

    _instance: Optional["LangfuseManager"] = None
    _langfuse_client: Optional[Langfuse] = None

    def __new__(cls) -> "LangfuseManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return

        self._initialized = True

        # Langfuse 클라이언트 초기화
        if settings.langfuse_secret_key and settings.langfuse_public_key:
            try:
                self._langfuse_client = Langfuse(
                    secret_key=settings.langfuse_secret_key,
                    public_key=settings.langfuse_public_key,
                    host=settings.langfuse_host,
                )
                try:
                    get_client()
                except Exception:
                    pass
                logger.info("Langfuse initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Langfuse: {e}")
                self._langfuse_client = None
        else:
            logger.info("Langfuse keys not provided, skipping initialization")

    @property
    def client(self) -> Optional[Langfuse]:
        return self._langfuse_client

    @property
    def callback_handler(self):
        if not self.is_enabled:
            return None
        try:
            # v3: 무인자
            return CallbackHandler()
        except Exception as e:
            logger.error(f"Failed to create callback handler: {e}")
            return None

    @property
    def is_enabled(self) -> bool:
        return self._langfuse_client is not None

    def create_trace(
        self, name: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[ContextManager[Any]]:
        """
        v3: 수동 트레이스 시작 = 컨텍스트 매니저 반환
        사용 예:
            with langfuse_manager.create_trace("process", {"user_id": "u1"}) as span:
                ...
        """
        if not self.is_enabled:
            return None
        try:
            langfuse = get_client()
            cm = langfuse.start_as_current_span(name=name)

            class _TraceCM:
                def __init__(self, inner_cm, md):
                    self._cm = inner_cm
                    self._md = md
                    self._span = None

                def __enter__(self):
                    span = self._cm.__enter__()
                    self._span = span
                    if self._md:
                        # trace 레벨 속성 업데이트 (user_id/session_id/tags 등)
                        span.update_trace(**self._md)
                    return span

                def __exit__(self, exc_type, exc, tb):
                    return self._cm.__exit__(exc_type, exc, tb)

            return _TraceCM(cm, metadata)
        except Exception as e:
            logger.error(f"Failed to start Langfuse trace context: {e}")
            return None

    def log_event(self, name: str, metadata: Optional[Dict[str, Any]] = None):
        """
        v3 권장: '이벤트'를 짧은 자식 span으로 기록
        (OTEL span.add_event는 현재 Langfuse에서 미표시 이슈가 있어 span 방식을 권장)
        """
        if not self.is_enabled:
            return None
        try:
            langfuse = get_client()
            with langfuse.start_as_current_span(name=f"event:{name}") as span:
                # 메타데이터는 input/output/metadata 등 원하는 필드로 기록
                if metadata:
                    span.update(input=metadata)
            return True
        except Exception as e:
            logger.error(f"Failed to log event to Langfuse: {e}")
            return None

    def flush(self):
        """Langfuse 데이터 플러시"""
        if self.is_enabled and self._langfuse_client is not None:
            try:
                if hasattr(self._langfuse_client, "flush"):
                    self._langfuse_client.flush()
                    logger.debug("Langfuse data flushed successfully")
                else:
                    logger.debug("Langfuse flush method not available")
            except Exception as e:
                logger.error(f"Failed to flush Langfuse data: {e}")

    def get_available_methods(self):
        """디버깅용: 사용 가능한 Langfuse 메서드 확인"""
        if not self.is_enabled or self._langfuse_client is None:
            return []

        methods = [
            method
            for method in dir(self._langfuse_client)
            if not method.startswith("_")
        ]
        logger.info(f"Available Langfuse methods: {methods}")
        return methods


# 전역 인스턴스
langfuse_manager = LangfuseManager()
