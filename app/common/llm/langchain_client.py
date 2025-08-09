import json
import logging
from typing import Any, Dict, List, Optional

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, BaseMessage

from app.common.llm.llm_client_repo import ILLMClientRepository
from app.common.llm.prompts.curriculum import CURRICULUM_GENERATION_PROMPT
from app.common.llm.prompts.feedback import FEEDBACK_GENERATION_PROMPT
from app.common.llm.langfuse_helper import langfuse_manager
from app.core.config import Settings, get_settings

logger: logging.Logger = logging.getLogger(__name__)


class LangChainLLMClient(ILLMClientRepository):
    def __init__(
        self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"
    ) -> None:
        logger.info("🔥 LangChainLLMClient v3 초기화 시작")

        settings: Settings = get_settings()
        self.api_key: str = api_key or settings.llm_api_key
        self.model: str = model

        logger.info(f"🔥 Langfuse v3 manager enabled: {langfuse_manager.is_enabled}")

        # 콜백 리스트 준비
        callbacks = []
        if langfuse_manager.is_enabled:
            callback_handler = langfuse_manager.callback_handler
            if callback_handler:
                callbacks.append(callback_handler)
                logger.info(
                    f"🔥 Langfuse v3 callback handler added: {type(callback_handler)}"
                )
            else:
                logger.error("🔥 Langfuse v3 is enabled but callback handler is None!")
        else:
            logger.warning("🔥 Langfuse v3 is not enabled, no callback handler added")

        # LangChain ChatOpenAI 클라이언트 초기화
        self.llm = ChatOpenAI(
            model=self.model,
            api_key=self.api_key,
            temperature=0.3,
            max_tokens=1200,  # model_kwargs 대신 직접 설정 # type: ignore
            callbacks=callbacks,
        )

        logger.info(
            f"🔥 LangChain v3 client initialized with {len(callbacks)} callbacks"
        )

    def _create_messages(self, prompt: str, role_content: str) -> List[BaseMessage]:
        """메시지 생성"""
        return [
            SystemMessage(content=role_content),
            HumanMessage(content=prompt),
        ]

    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """JSON 응답 파싱"""
        cleaned = response_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]

        try:
            return json.loads(cleaned.strip())
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response: {response_text}")
            raise ValueError(f"Invalid JSON response from LLM: {e}")

    async def generate_curriculum(
        self,
        goal: str,
        period: int,
        difficulty: str,
        details: str,
    ) -> Dict[str, Any]:
        """커리큘럼 생성"""
        logger.info("🔥 Starting curriculum generation with LangChain v3")

        prompt: str = CURRICULUM_GENERATION_PROMPT.format(
            goal=goal,
            period=period,
            difficulty=difficulty,
            details=details,
        )

        role_content: str = (
            "You are a curriculum generator. "
            "Generate in Korean "
            "Output *only* valid JSON "
            "The JSON must be an array with these fields "
            "`title` (string), and `schedule` (array of objects with {week_number:int, topics:list[str]})."
            "no markdown, no explanations, nothing else "
            "if request for Computer Science, refer to OSSU curriculum "
            "else, generate as request"
        )

        messages = self._create_messages(prompt, role_content)

        logger.info(
            f"🔥 Generating curriculum - Goal: {goal}, Period: {period}, Difficulty: {difficulty}"
        )
        logger.info(f"🔥 Langfuse v3 enabled: {langfuse_manager.is_enabled}")

        try:
            logger.info("🔥 Calling LLM with LangChain v3...")

            # v3에서는 콜백핸들러가 자동으로 모든 추적 처리
            response = await self.llm.ainvoke(messages)

            logger.info("🔥 LLM call completed")

            # response.content 처리
            response_text: str
            if isinstance(response.content, str):
                response_text = response.content
            elif isinstance(response.content, list):
                response_text = str(response.content[0]) if response.content else ""
            else:
                response_text = str(response.content)

            result = self._parse_json_response(response_text)

            logger.info("🔥 Curriculum generation completed successfully")
            logger.info(f"🔥 Response length: {len(response_text)}")

            return result

        except Exception as e:
            logger.error(f"🔥 Curriculum generation failed: {e}")
            raise

    async def generate_feedback(
        self,
        lessons: List[str],
        summary_content: str,
    ) -> Dict[str, Any]:
        """피드백 생성"""
        logger.info("🔥 Starting feedback generation with LangChain v3")

        prompt = FEEDBACK_GENERATION_PROMPT.format(
            lessons=", ".join(lessons), summary=summary_content
        )

        role_content: str = (
            "You are a learning feedback generator. "
            "Output *only* valid JSON with exactly `comment` (string) "
            "Generate in Korean "
            "no markdown, no explanations, nothing else "
            "and `score` (float 0–10). No other keys or markdown."
        )

        messages = self._create_messages(prompt, role_content)

        logger.info(
            f"🔥 Generating feedback - Lessons count: {len(lessons)}, Summary length: {len(summary_content)}"
        )

        try:
            logger.info("🔥 Calling LLM with LangChain v3...")

            # v3에서는 콜백핸들러가 자동으로 모든 추적 처리
            response = await self.llm.ainvoke(messages)

            logger.info("🔥 LLM call completed")

            # response.content 처리
            response_text: str
            if isinstance(response.content, str):
                response_text = response.content
            elif isinstance(response.content, list):
                response_text = str(response.content[0]) if response.content else ""
            else:
                response_text = str(response.content)

            result = self._parse_json_response(response_text)

            logger.info("🔥 Feedback generation completed successfully")
            return result

        except Exception as e:
            logger.error(f"🔥 Feedback generation failed: {e}")
            raise
