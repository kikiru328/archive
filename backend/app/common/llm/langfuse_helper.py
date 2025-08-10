import logging
from typing import Optional
import os
from langfuse.langchain import CallbackHandler

logger = logging.getLogger(__name__)


class LangfuseManager:
    """Langfuse v3 연동 관리 클래스"""

    _instance: Optional["LangfuseManager"] = None
    _callback_handler: Optional[CallbackHandler] = None

    def __new__(cls) -> "LangfuseManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        os.environ["LANGFUSE_LOG_LEVEL"] = "WARNING"
        os.environ["LANGFUSE_LOG_DIR"] = "/workspace/backend/app/logs"

        if hasattr(self, "_initialized"):
            return

        self._initialized = True

        # 🔥 환경변수 검증
        secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

        logger.info(f"🔥 Langfuse Host: {host}")
        logger.info(f"🔥 Secret Key Present: {bool(secret_key)}")
        logger.info(f"🔥 Public Key Present: {bool(public_key)}")

        if secret_key:
            logger.info(
                f"🔥 Secret Key Format: {secret_key[:10]}...{secret_key[-4:] if len(secret_key) > 14 else ''}"
            )
        if public_key:
            logger.info(
                f"🔥 Public Key Format: {public_key[:10]}...{public_key[-4:] if len(public_key) > 14 else ''}"
            )

        # 키 형식 검증
        if secret_key and not secret_key.startswith("sk-lf-"):
            logger.error("🔥 Secret key should start with 'sk-lf-'")
            return

        if public_key and not public_key.startswith("pk-lf-"):
            logger.error("🔥 Public key should start with 'pk-lf-'")
            return

        # Langfuse v3는 환경변수만 있으면 자동 초기화
        if secret_key and public_key:
            try:
                logger.info("🔥 Creating Langfuse v3 callback handler...")

                # 환경변수 설정 확인
                os.environ["LANGFUSE_SECRET_KEY"] = secret_key
                os.environ["LANGFUSE_PUBLIC_KEY"] = public_key
                os.environ["LANGFUSE_HOST"] = host

                # v3에서는 환경변수만 있으면 자동으로 연결
                self._callback_handler = CallbackHandler()

                logger.info("🔥 Langfuse v3 initialized successfully")
                logger.info(
                    f"🔥 Callback handler created: {type(self._callback_handler)}"
                )

                # 추가 설정 로깅
                logger.info(f"🔥 Using host: {host}")

            except Exception as e:
                logger.error(f"🔥 Failed to initialize Langfuse v3: {e}")
                logger.exception("🔥 Langfuse v3 initialization error details:")
                self._callback_handler = None
        else:
            logger.warning("🔥 Langfuse keys not provided or invalid format")

    @property
    def callback_handler(self) -> Optional[CallbackHandler]:
        """콜백 핸들러 반환"""
        return self._callback_handler

    @property
    def is_enabled(self) -> bool:
        enabled = self._callback_handler is not None
        return enabled

    def test_connection(self):
        """연결 테스트"""
        if not self.is_enabled:
            logger.warning("🔥 Langfuse not enabled for connection test")
            return False

        try:
            # 간단한 테스트 이벤트 생성
            from langfuse import Langfuse

            client = Langfuse()

            trace = client.trace(name="connection_test")  # type: ignore
            trace.event(name="test_event", metadata={"test": True})
            client.flush()

            logger.info("🔥 Connection test successful")
            return True

        except Exception as e:
            logger.error(f"🔥 Connection test failed: {e}")
            return False


# 전역 인스턴스
logger.info("🔥 Creating Langfuse v3 manager instance...")
langfuse_manager = LangfuseManager()
logger.info(f"🔥 Langfuse v3 manager created, enabled: {langfuse_manager.is_enabled}")

# 연결 테스트 실행
if langfuse_manager.is_enabled:
    langfuse_manager.test_connection()
