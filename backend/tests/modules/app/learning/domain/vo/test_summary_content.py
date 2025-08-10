import pytest
from app.modules.learning.domain.vo.summary_content import SummaryContent


class TestSummaryContent:
    """SummaryContent VO 테스트"""

    def test_valid_summary_content(self):
        """유효한 요약 내용 테스트"""
        content = "이번 주차에서는 파이썬의 기본 문법에 대해 학습했습니다." * 10
        summary_content = SummaryContent(content)

        assert summary_content.value == content
        assert summary_content.length == len(content)

    def test_minimum_length(self):
        """최소 길이 테스트"""
        content = "a" * 100  # 정확히 100자
        summary_content = SummaryContent(content)
        assert summary_content.length == 100

    def test_maximum_length(self):
        """최대 길이 테스트"""
        content = "a" * 5000  # 정확히 5000자
        summary_content = SummaryContent(content)
        assert summary_content.length == 5000

    def test_content_too_short(self):
        """너무 짧은 내용 테스트"""
        content = "a" * 99  # 99자
        with pytest.raises(ValueError, match="요약 내용은 100자 이상이어야 합니다"):
            SummaryContent(content)

    def test_content_too_long(self):
        """너무 긴 내용 테스트"""
        content = "a" * 5001  # 5001자
        with pytest.raises(ValueError, match="요약 내용은 5000자 이하이어야 합니다"):
            SummaryContent(content)

    def test_empty_content(self):
        """빈 내용 테스트"""
        with pytest.raises(ValueError, match="SummaryContent cannot be empty"):
            SummaryContent("")

    def test_whitespace_only_content(self):
        """공백만 있는 내용 테스트"""
        with pytest.raises(ValueError, match="SummaryContent cannot be empty"):
            SummaryContent("   ")

    def test_content_with_whitespace_trimming(self):
        """공백 제거 테스트"""
        content = "  " + "a" * 100 + "  "
        summary_content = SummaryContent(content)
        assert summary_content.value == "a" * 100
        assert summary_content.length == 100

    def test_non_string_type(self):
        """문자열이 아닌 타입 테스트"""
        with pytest.raises(ValueError, match="SummaryContent must be a string"):
            SummaryContent(123)  # type: ignore

    def test_equality(self):
        """동등성 비교 테스트"""
        content1 = SummaryContent("a" * 100)
        content2 = SummaryContent("a" * 100)
        content3 = SummaryContent("b" * 100)

        assert content1 == content2
        assert content1 != content3

    def test_hash(self):
        """해시 테스트"""
        content1 = SummaryContent("a" * 100)
        content2 = SummaryContent("a" * 100)

        assert hash(content1) == hash(content2)

    def test_repr(self):
        """문자열 표현 테스트"""
        content = SummaryContent("a" * 100)
        assert repr(content) == "<SummaryContent length=100>"
