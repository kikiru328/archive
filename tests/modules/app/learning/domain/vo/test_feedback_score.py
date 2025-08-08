import pytest
from app.modules.learning.domain.vo.feedback_score import FeedbackScore


class TestFeedbackScore:
    """FeedbackScore VO 테스트"""

    def test_valid_scores(self):
        """유효한 점수 테스트"""
        scores = [0.0, 5.5, 10.0, 7, 8.75]
        for score in scores:
            feedback_score = FeedbackScore(score)
            assert feedback_score.value == float(score)

    def test_minimum_score(self):
        """최소 점수 테스트"""
        score = FeedbackScore(0.0)
        assert score.value == 0.0

    def test_maximum_score(self):
        """최대 점수 테스트"""
        score = FeedbackScore(10.0)
        assert score.value == 10.0

    def test_score_below_minimum(self):
        """최소값 미만 점수 테스트"""
        with pytest.raises(
            ValueError, match="FeedbackScore must be between 0.0 and 10.0"
        ):
            FeedbackScore(-0.1)

    def test_score_above_maximum(self):
        """최대값 초과 점수 테스트"""
        with pytest.raises(
            ValueError, match="FeedbackScore must be between 0.0 and 10.0"
        ):
            FeedbackScore(10.1)

    def test_integer_score(self):
        """정수 점수 테스트"""
        score = FeedbackScore(7)
        assert score.value == 7.0
        assert isinstance(score.value, float)

    def test_invalid_type(self):
        """잘못된 타입 테스트"""
        with pytest.raises(TypeError, match="FeedbackScore must be int or float"):
            FeedbackScore("7.5")  # type: ignore

    def test_string_representation(self):
        """문자열 표현 테스트"""
        score = FeedbackScore(7.5)
        assert str(score) == "7.5/10"

    def test_equality(self):
        """동등성 비교 테스트"""
        score1 = FeedbackScore(7.5)
        score2 = FeedbackScore(7.5)
        score3 = FeedbackScore(8.0)

        assert score1 == score2
        assert score1 != score3

    def test_hash(self):
        """해시 테스트"""
        score1 = FeedbackScore(7.5)
        score2 = FeedbackScore(7.5)

        assert hash(score1) == hash(score2)

    def test_repr(self):
        """repr 테스트"""
        score = FeedbackScore(7.5)
        assert repr(score) == "<FeedbackScore 7.5>"
