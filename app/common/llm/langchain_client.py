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
        settings: Settings = get_settings()
        self.api_key: str = api_key or settings.llm_api_key
        self.model: str = model

        # 콜백 리스트 준비
        callbacks = []
        callback_handler = langfuse_manager.callback_handler
        if langfuse_manager.is_enabled and callback_handler:
            callbacks.append(callback_handler)
            logger.info("Langfuse callback handler added to LLM client")

        # LangChain ChatOpenAI 클라이언트 초기화
        self.llm = ChatOpenAI(
            model=self.model,
            api_key=self.api_key,  # type: ignore
            temperature=0.3,
            model_kwargs={"max_tokens": 1200},
            callbacks=callbacks,
        )

    def _create_messages(self, prompt: str, role_content: str) -> List[BaseMessage]:
        """메시지 생성"""
        return [
            SystemMessage(content=role_content),
            HumanMessage(content=prompt),
        ]

    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """JSON 응답 파싱"""
        # 마크다운 코드 블록 제거
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

        # 로깅 및 추적
        operation_metadata = {
            "goal": goal,
            "period": period,
            "difficulty": difficulty,
            "model": self.model,
        }

        logger.info(
            f"Generating curriculum - Goal: {goal}, Period: {period}, Difficulty: {difficulty}"
        )

        # Langfuse 이벤트 로깅 (선택적)
        if langfuse_manager.is_enabled:
            langfuse_manager.log_event(
                name="curriculum_generation_start", metadata=operation_metadata
            )

        try:
            response = await self.llm.ainvoke(messages)

            # response.content의 타입을 확인하고 문자열로 변환
            response_text: str
            if isinstance(response.content, str):
                response_text = response.content
            elif isinstance(response.content, list):
                response_text = str(response.content[0]) if response.content else ""
            else:
                response_text = str(response.content)

            result = self._parse_json_response(response_text)

            # 성공 로깅
            if langfuse_manager.is_enabled:
                langfuse_manager.log_event(
                    name="curriculum_generation_success",
                    metadata={
                        **operation_metadata,
                        "response_length": len(response_text),
                        "success": True,
                    },
                )

            logger.info("Curriculum generation completed successfully")
            return result

        except Exception as e:
            # 실패 로깅
            if langfuse_manager.is_enabled:
                langfuse_manager.log_event(
                    name="curriculum_generation_error",
                    metadata={**operation_metadata, "error": str(e), "success": False},
                )

            logger.error(f"Curriculum generation failed: {e}")
            raise

    async def generate_feedback(
        self,
        lessons: List[str],
        summary_content: str,
    ) -> Dict[str, Any]:
        """피드백 생성"""
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

        # 로깅 및 추적
        operation_metadata = {
            "lessons_count": len(lessons),
            "summary_length": len(summary_content),
            "model": self.model,
        }

        logger.info(
            f"Generating feedback - Lessons count: {len(lessons)}, Summary length: {len(summary_content)}"
        )

        # Langfuse 이벤트 로깅 (선택적)
        if langfuse_manager.is_enabled:
            langfuse_manager.log_event(
                name="feedback_generation_start", metadata=operation_metadata
            )

        try:
            response = await self.llm.ainvoke(messages)

            # response.content의 타입을 확인하고 문자열로 변환
            response_text: str
            if isinstance(response.content, str):
                response_text = response.content
            elif isinstance(response.content, list):
                response_text = str(response.content[0]) if response.content else ""
            else:
                response_text = str(response.content)

            result = self._parse_json_response(response_text)

            # 성공 로깅
            if langfuse_manager.is_enabled:
                langfuse_manager.log_event(
                    name="feedback_generation_success",
                    metadata={
                        **operation_metadata,
                        "score": result.get("score"),
                        "success": True,
                    },
                )

            logger.info("Feedback generation completed successfully")
            return result

        except Exception as e:
            # 실패 로깅
            if langfuse_manager.is_enabled:
                langfuse_manager.log_event(
                    name="feedback_generation_error",
                    metadata={**operation_metadata, "error": str(e), "success": False},
                )

            logger.error(f"Feedback generation failed: {e}")
            raise
