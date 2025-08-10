import pytest
from app.modules.learning.domain.vo.feedback_comment import FeedbackComment


class TestFeedbackComment:
    """FeedbackComment VO 테스트"""

    def test_valid_comment(self):
        """유효한 코멘트 테스트"""
        comment_text = "좋은 요약입니다. 핵심 내용을 잘 파악했네요."
        comment = FeedbackComment(comment_text)
        assert comment.value == comment_text

    def test_empty_comment(self):
        """빈 코멘트 테스트"""
        with pytest.raises(ValueError, match="FeedbackComment cannot be empty"):
            FeedbackComment("")

    def test_whitespace_only_comment(self):
        """공백만 있는 코멘트 테스트"""
        with pytest.raises(ValueError, match="FeedbackComment cannot be empty"):
            FeedbackComment("   ")

    def test_comment_with_whitespace_trimming(self):
        """공백 제거 테스트"""
        comment_text = "  좋은 요약입니다  "
        comment = FeedbackComment(comment_text)
        assert comment.value == "좋은 요약입니다"

    def test_non_string_type(self):
        """문자열이 아닌 타입 테스트"""
        with pytest.raises(TypeError, match="FeedbackComment must be a string"):
            FeedbackComment(123)  # type: ignore

    def test_equality(self):
        """동등성 비교 테스트"""
        comment1 = FeedbackComment("좋은 요약")
        comment2 = FeedbackComment("좋은 요약")
        comment3 = FeedbackComment("나쁜 요약")

        assert comment1 == comment2
        assert comment1 != comment3

    def test_hash(self):
        """해시 테스트"""
        comment1 = FeedbackComment("좋은 요약")
        comment2 = FeedbackComment("좋은 요약")

        assert hash(comment1) == hash(comment2)

    def test_repr(self):
        """repr 테스트"""
        comment = FeedbackComment("좋은 요약입니다")
        assert repr(comment) == "<FeedbackComment length=8>"

    def test_str(self):
        """str 테스트"""
        comment_text = "좋은 요약입니다"
        comment = FeedbackComment(comment_text)
        assert str(comment) == comment_text
