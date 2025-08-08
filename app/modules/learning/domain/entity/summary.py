from dataclasses import dataclass
from datetime import datetime

from app.modules.curriculum.domain.vo.week_number import WeekNumber
from app.modules.learning.domain.vo.summary_content import SummaryContent


@dataclass
class Summary:
    """학습 요약 Entity"""

    id: str
    owner_id: str
    curriculum_id: str
    week_number: WeekNumber
    content: SummaryContent
    created_at: datetime
    updated_at: datetime

    def __post_init__(self):
        if not isinstance(self.id, str) or not self.id.strip():
            raise TypeError("id must be a non-empty string")
        if not isinstance(self.curriculum_id, str) or not self.curriculum_id.strip():
            raise TypeError("curriculum_id must be a non-empty string")
        if not isinstance(self.week_number, WeekNumber):
            raise TypeError(
                f"week_number must be WeekNumber, got {type(self.week_number).__name__}"
            )
        if not isinstance(self.content, SummaryContent):
            raise TypeError(
                f"content must be SummaryContent, got {type(self.content).__name__}"
            )
        if not isinstance(self.created_at, datetime):
            raise TypeError(
                f"created_at must be datetime, got {type(self.created_at).__name__}"
            )
        if not isinstance(self.updated_at, datetime):
            raise TypeError(
                f"updated_at must be datetime, got {type(self.updated_at).__name__}"
            )

    def update_content(self, new_content: SummaryContent) -> None:
        """요약 내용 수정"""
        if self.content == new_content:
            return

        self.content = new_content
        self.updated_at = datetime.now()

    def get_content_snippet(self, max_length: int = 100) -> str:
        """요약 내용의 미리보기 반환"""
        if len(self.content.value) <= max_length:
            return self.content.value
        return self.content.value[:max_length] + "..."

    def is_owned_by(self, owner_id: str) -> bool:
        return self.owner_id == owner_id

    def __str__(self) -> str:
        return f"Summary(Week {self.week_number.value}): {self.get_content_snippet(50)}"

    def __repr__(self) -> str:
        return f"<Summary id={self.id} curriculum_id={self.curriculum_id} week={self.week_number.value}>"
