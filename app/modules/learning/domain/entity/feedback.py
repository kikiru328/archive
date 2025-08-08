from dataclasses import dataclass
from datetime import datetime

from app.modules.learning.domain.vo.feedback_comment import FeedbackComment
from app.modules.learning.domain.vo.feedback_score import FeedbackScore


@dataclass
class Feedback:
    """학습 피드백 Entity"""

    id: str
    summary_id: str
    comment: FeedbackComment
    score: FeedbackScore
    created_at: datetime
    updated_at: datetime

    def __post_init__(self):
        if not isinstance(self.id, str) or not self.id.strip():
            raise TypeError("id must be a non-empty string")
        if not isinstance(self.summary_id, str) or not self.summary_id.strip():
            raise TypeError("summary_id must be a non-empty string")
        if not isinstance(self.comment, FeedbackComment):
            raise TypeError(
                f"comment must be FeedbackComment, got {type(self.comment).__name__}"
            )
        if not isinstance(self.score, FeedbackScore):
            raise TypeError(
                f"score must be FeedbackScore, got {type(self.score).__name__}"
            )
        if not isinstance(self.created_at, datetime):
            raise TypeError(
                f"created_at must be datetime, got {type(self.created_at).__name__}"
            )
        if not isinstance(self.updated_at, datetime):
            raise TypeError(
                f"updated_at must be datetime, got {type(self.updated_at).__name__}"
            )

    def update_feedback(
        self, new_comment: FeedbackComment, new_score: FeedbackScore
    ) -> None:
        """피드백 내용 수정"""
        if self.comment == new_comment and self.score == new_score:
            return

        self.comment = new_comment
        self.score = new_score
        self.updated_at = datetime.now()

    def is_good_score(self, threshold: float = 7.0) -> bool:
        """좋은 점수인지 확인"""
        return self.score.value >= threshold

    def is_poor_score(self, threshold: float = 4.0) -> bool:
        """낮은 점수인지 확인"""
        return self.score.value <= threshold

    def get_grade(self) -> str:
        """점수에 따른 등급 반환"""
        score = self.score.value
        if score >= 9.0:
            return "A+"
        elif score >= 8.0:
            return "A"
        elif score >= 7.0:
            return "B+"
        elif score >= 6.0:
            return "B"
        elif score >= 5.0:
            return "C+"
        elif score >= 4.0:
            return "C"
        else:
            return "D"

    def __str__(self) -> str:
        return f"Feedback({self.score}): {self.comment.value[:50]}..."

    def __repr__(self) -> str:
        return f"<Feedback id={self.id} summary_id={self.summary_id} score={self.score.value}>"
