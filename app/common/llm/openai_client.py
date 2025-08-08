import json
import logging
from typing import Any, Dict, List, Optional

import aiohttp
from app.common.llm.llm_client_repo import ILLMClientRepository
from app.common.llm.prompts.curriculum import CURRICULUM_GENERATION_PROMPT
from app.common.llm.prompts.feedback import FEEDBACK_GENERATION_PROMPT
from app.core.config import Settings, get_settings

logger: logging.Logger = logging.getLogger(__name__)


class OpenAILLMClient(ILLMClientRepository):
    def __init__(
        self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"
    ) -> None:

        settings: Settings = get_settings()
        self.api_key: str = api_key or settings.llm_api_key
        self.model: str = model
        self.endpoint = "https://api.openai.com/v1/chat/completions"

    async def _make_request(
        self,
        prompt: str,
        role_content: str,
        max_tokens: int = 1200,
        timeout: float | None = 10.0,
    ) -> str:
        """OpenAI API 요청"""
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": role_content,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            "max_tokens": max_tokens,
            "temperature": 0.3,  # 저무작위성
        }

        headers: Dict[str, str] = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=timeout)
        ) as session:
            async with session.post(
                self.endpoint, json=payload, headers=headers
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data["choices"][0]["message"]["content"]

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

        response_text = await self._make_request(
            prompt=prompt,
            role_content=role_content,
            timeout=None,
        )
        return self._parse_json_response(response_text)

    async def generate_feedback(
        self,
        lessons: List[str],
        summary_content: str,
    ) -> Dict[str, Any]:

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
        response_text = await self._make_request(
            prompt=prompt,
            role_content=role_content,
            timeout=10.0,
        )
        return self._parse_json_response(response_text)
