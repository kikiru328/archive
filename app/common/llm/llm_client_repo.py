from abc import ABCMeta, abstractmethod
from typing import Any, Dict, List


class ILLMClientRepository(metaclass=ABCMeta):
    @abstractmethod
    async def generate_curriculum(
        self,
        goal: str,
        period: int,
        difficulty: str,
        details: str,
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def generate_feedback(
        self,
        lessons: List[str],
        summary_content: str,
    ) -> Dict[str, Any]:
        pass
