import pytest
from app.modules.curriculum.domain.vo.visibility import Visibility


class TestVisibility:
    """Visibility VO 테스트"""

    def test_visibility_values(self):
        """Visibility 값 테스트"""
        assert Visibility.PUBLIC == "PUBLIC"
        assert Visibility.PRIVATE == "PRIVATE"

    def test_is_public(self):
        """is_public 메서드 테스트"""
        assert Visibility.PUBLIC.is_public() is True
        assert Visibility.PRIVATE.is_public() is False

    def test_is_private(self):
        """is_private 메서드 테스트"""
        assert Visibility.PRIVATE.is_private() is True
        assert Visibility.PUBLIC.is_private() is False

    def test_visibility_from_string(self):
        """문자열에서 Visibility 생성 테스트"""
        public = Visibility("PUBLIC")
        private = Visibility("PRIVATE")

        assert public == Visibility.PUBLIC
        assert private == Visibility.PRIVATE

    def test_invalid_visibility(self):
        """잘못된 Visibility 값 테스트"""
        with pytest.raises(ValueError):
            Visibility("INVALID")
