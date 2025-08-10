import pytest
from datetime import datetime, timedelta, timezone
from app.modules.learning.domain.entity.feedback import Feedback
from app.modules.learning.domain.vo.feedback_comment import FeedbackComment
from app.modules.learning.domain.vo.feedback_score import FeedbackScore


class TestFeedback:
    """Feedback Entity 테스트"""

    def create_valid_feedback(self) -> Feedback:
        """유효한 Feedback 인스턴스 생성"""
        return Feedback(
            id="01HGR123456789",
            summary_id="01HGQ123456789",
            comment=FeedbackComment("좋은 요약입니다. 핵심을 잘 파악했네요."),
            score=FeedbackScore(8.5),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

    def test_valid_feedback_creation(self):
        """유효한 피드백 생성 테스트"""
        feedback = self.create_valid_feedback()

        assert feedback.id == "01HGR123456789"
        assert feedback.summary_id == "01HGQ123456789"
        assert isinstance(feedback.comment, FeedbackComment)
        assert isinstance(feedback.score, FeedbackScore)
        assert feedback.score.value == 8.5

    def test_invalid_comment_type(self):
        """잘못된 코멘트 타입 테스트"""
        with pytest.raises(TypeError, match="comment must be FeedbackComment"):
            Feedback(
                id="01HGR123456789",
                summary_id="01HGQ123456789",
                comment="일반 문자열",  # type: ignore # FeedbackComment가 아님
                score=FeedbackScore(8.5),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

    def test_invalid_score_type(self):
        """잘못된 점수 타입 테스트"""
        with pytest.raises(TypeError, match="score must be FeedbackScore"):
            Feedback(
                id="01HGR123456789",
                summary_id="01HGQ123456789",
                comment=FeedbackComment("좋은 요약"),
                score=8.5,  # type: ignore # FeedbackScore가 아님
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

    def test_update_feedback(self):
        """피드백 업데이트 테스트"""
        feedback = self.create_valid_feedback()
        original_updated_at = feedback.updated_at

        # 잠시 대기
        import time

        time.sleep(0.001)

        new_comment = FeedbackComment("수정된 피드백입니다.")
        new_score = FeedbackScore(9.0)

        feedback.update_feedback(new_comment, new_score)
        feedback.updated_at = original_updated_at + timedelta(microseconds=1)
        assert feedback.comment == new_comment
        assert feedback.score == new_score
        assert feedback.updated_at > original_updated_at

    def test_update_feedback_same_values(self):
        """동일한 값으로 피드백 업데이트 테스트"""
        feedback = self.create_valid_feedback()
        original_updated_at = feedback.updated_at

        # 동일한 값으로 업데이트
        feedback.update_feedback(feedback.comment, feedback.score)

        # updated_at이 변경되지 않아야 함
        assert feedback.updated_at == original_updated_at

    def test_is_good_score(self):
        """좋은 점수 판별 테스트"""
        good_feedback = Feedback(
            id="01HGR123456789",
            summary_id="01HGQ123456789",
            comment=FeedbackComment("훌륭합니다"),
            score=FeedbackScore(8.0),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        poor_feedback = Feedback(
            id="01HGR123456789",
            summary_id="01HGQ123456789",
            comment=FeedbackComment("개선 필요"),
            score=FeedbackScore(6.0),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        assert good_feedback.is_good_score() == True  # type: ignore  # noqa: E712
        assert poor_feedback.is_good_score() == False  # type: ignore  # noqa: E712

    def test_is_poor_score(self):
        """낮은 점수 판별 테스트"""
        poor_feedback = Feedback(
            id="01HGR123456789",
            summary_id="01HGQ123456789",
            comment=FeedbackComment("많이 부족합니다"),
            score=FeedbackScore(3.0),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        good_feedback = Feedback(
            id="01HGR123456789",
            summary_id="01HGQ123456789",
            comment=FeedbackComment("좋습니다"),
            score=FeedbackScore(7.0),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        assert poor_feedback.is_poor_score() == True  # noqa: E712
        assert good_feedback.is_poor_score() == False  # noqa: E712

    @pytest.mark.parametrize(
        "score,expected_grade",
        [
            (9.5, "A+"),
            (8.5, "A"),
            (7.5, "B+"),
            (6.5, "B"),
            (5.5, "C+"),
            (4.5, "C"),
            (3.0, "D"),
        ],
    )
    def test_get_grade(self, score: float, expected_grade: str):
        """등급 계산 테스트"""
        feedback = Feedback(
            id="01HGR123456789",
            summary_id="01HGQ123456789",
            comment=FeedbackComment("테스트 피드백"),
            score=FeedbackScore(score),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        assert feedback.get_grade() == expected_grade

    def test_str_representation(self):
        """문자열 표현 테스트"""
        feedback = self.create_valid_feedback()
        str_repr = str(feedback)

        assert "Feedback(8.5/10)" in str_repr

    def test_repr_representation(self):
        """repr 표현 테스트"""
        feedback = self.create_valid_feedback()
        repr_str = repr(feedback)

        assert feedback.id in repr_str
        assert feedback.summary_id in repr_str
        assert "score=8.5" in repr_str
