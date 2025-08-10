import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from app.modules.learning.domain.entity.summary import Summary
from app.modules.learning.domain.entity.feedback import Feedback
from app.modules.learning.domain.vo.summary_content import SummaryContent
from app.modules.learning.domain.vo.feedback_comment import FeedbackComment
from app.modules.learning.domain.vo.feedback_score import FeedbackScore
from app.modules.curriculum.domain.vo.week_number import WeekNumber


@pytest.fixture
def mock_summary_repo():
    """Summary Repository Mock"""
    return AsyncMock()


@pytest.fixture
def mock_feedback_repo():
    """Feedback Repository Mock"""
    return AsyncMock()


@pytest.fixture
def mock_curriculum_repo():
    """Curriculum Repository Mock"""
    return AsyncMock()


@pytest.fixture
def sample_summary():
    """샘플 Summary 엔티티"""
    return Summary(
        id="01HGQ123456789",
        curriculum_id="01HGP123456789",
        week_number=WeekNumber(1),
        content=SummaryContent(
            "파이썬 기초 문법에 대해 학습한 내용을 요약합니다. " * 5
        ),
        owner_id="01HGU123456789",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_feedback():
    """샘플 Feedback 엔티티"""
    return Feedback(
        id="01HGR123456789",
        summary_id="01HGQ123456789",
        comment=FeedbackComment("파이썬 기초 문법에 대한 이해가 잘 되어 있습니다."),
        score=FeedbackScore(8.5),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_curriculum():
    """샘플 Curriculum 엔티티 (Mock)"""
    from app.modules.curriculum.domain.entity.curriculum import Curriculum
    from app.modules.curriculum.domain.vo.title import Title
    from app.modules.curriculum.domain.vo.visibility import Visibility
    from app.modules.curriculum.domain.entity.week_schedule import WeekSchedule
    from app.modules.curriculum.domain.vo.lessons import Lessons

    curriculum = MagicMock(spec=Curriculum)
    curriculum.id = "01HGP123456789"
    curriculum.owner_id = "01HGU123456789"
    curriculum.title = Title("파이썬 기초 과정")
    curriculum.visibility = Visibility.PRIVATE
    curriculum.week_schedules = [
        WeekSchedule(
            week_number=WeekNumber(1),
            lessons=Lessons(["변수와 자료형", "연산자", "조건문"]),
        )
    ]
    curriculum.is_owned_by.return_value = True
    curriculum.is_public.return_value = False
    curriculum.has_week.return_value = True
    curriculum.get_week_schedule.return_value = curriculum.week_schedules[0]
