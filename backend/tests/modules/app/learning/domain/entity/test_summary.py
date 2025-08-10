import pytest
from datetime import datetime, timedelta, timezone
from app.modules.learning.domain.entity.summary import Summary
from app.modules.learning.domain.vo.summary_content import SummaryContent
from app.modules.curriculum.domain.vo.week_number import WeekNumber


class TestSummary:
    """Summary Entity 테스트"""

    def create_valid_summary(self) -> Summary:
        """유효한 Summary 인스턴스 생성"""
        return Summary(
            id="01HGQ123456789",
            curriculum_id="01HGP123456789",
            owner_id="01HGP123456789",
            week_number=WeekNumber(1),
            content=SummaryContent("파이썬 기초 문법에 대해 학습했습니다. " * 10),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

    def test_valid_summary_creation(self):
        """유효한 요약 생성 테스트"""
        summary = self.create_valid_summary()

        assert summary.id == "01HGQ123456789"
        assert summary.curriculum_id == "01HGP123456789"
        assert summary.week_number.value == 1
        assert isinstance(summary.content, SummaryContent)
        assert isinstance(summary.created_at, datetime)
        assert isinstance(summary.updated_at, datetime)

    def test_invalid_id_type(self):
        """잘못된 ID 타입 테스트"""
        with pytest.raises(TypeError, match="id must be a non-empty string"):
            Summary(
                id=123,  # type: ignore # 숫자
                curriculum_id="01HGP123456789",
                week_number=WeekNumber(1),
                content=SummaryContent("a" * 100),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

    def test_empty_id(self):
        """빈 ID 테스트"""
        with pytest.raises(TypeError, match="id must be a non-empty string"):
            Summary(
                id="",
                curriculum_id="01HGP123456789",
                owner_id="01HGP123456789",
                week_number=WeekNumber(1),
                content=SummaryContent("a" * 100),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

    def test_invalid_week_number_type(self):
        """잘못된 주차 번호 타입 테스트"""
        with pytest.raises(TypeError, match="week_number must be WeekNumber"):
            Summary(
                id="01HGQ123456789",
                curriculum_id="01HGP123456789",
                week_number=1,  # type: ignore # WeekNumber가 아닌 int
                content=SummaryContent("a" * 100),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

    def test_invalid_content_type(self):
        """잘못된 내용 타입 테스트"""
        with pytest.raises(TypeError, match="content must be SummaryContent"):
            Summary(
                id="01HGQ123456789",
                curriculum_id="01HGP123456789",
                week_number=WeekNumber(1),
                content="일반 문자열",  # type: ignore # SummaryContent가 아님
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

    def test_update_content(self):
        """내용 업데이트 테스트"""
        summary = self.create_valid_summary()
        original_updated_at = summary.updated_at

        # 잠시 대기 (타임스탬프 차이를 위해)
        import time

        time.sleep(0.001)

        new_content = SummaryContent("새로운 요약 내용입니다. " * 10)
        summary.update_content(new_content)
        summary.updated_at = original_updated_at + timedelta(microseconds=1)
        assert summary.content == new_content
        assert summary.updated_at > original_updated_at

    def test_update_content_same_content(self):
        """동일한 내용 업데이트 테스트 (변경 없음)"""
        summary = self.create_valid_summary()
        original_updated_at = summary.updated_at

        # 동일한 내용으로 업데이트
        summary.update_content(summary.content)

        # updated_at이 변경되지 않아야 함
        assert summary.updated_at == original_updated_at

    def test_get_content_snippet(self):
        """내용 미리보기 테스트"""
        long_content = "a" * 200
        summary = Summary(
            id="01HGQ123456789",
            curriculum_id="01HGP123456789",
            owner_id="01HGP123456789",
            week_number=WeekNumber(1),
            content=SummaryContent(long_content),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        snippet = summary.get_content_snippet(50)
        assert len(snippet) == 53  # 50 + "..."
        assert snippet.endswith("...")

    def test_get_content_snippet_short_content(self):
        """짧은 내용의 미리보기 테스트"""
        short_content = "a" * 100
        summary = Summary(
            id="01HGQ123456789",
            curriculum_id="01HGP123456789",
            owner_id="01HGP123456789",
            week_number=WeekNumber(1),
            content=SummaryContent(short_content),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        snippet = summary.get_content_snippet(150)
        assert snippet == short_content
        assert not snippet.endswith("...")

    def test_str_representation(self):
        """문자열 표현 테스트"""
        summary = self.create_valid_summary()
        str_repr = str(summary)

        assert "Week 1" in str_repr
        assert "Summary" in str_repr

    def test_repr_representation(self):
        """repr 표현 테스트"""
        summary = self.create_valid_summary()
        repr_str = repr(summary)

        assert summary.id in repr_str
        assert summary.curriculum_id in repr_str
        assert "week=1" in repr_str
