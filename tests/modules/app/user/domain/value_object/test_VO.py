from app.modules.user.domain.vo.role import RoleVO


class TestRoleVO:
    def test_user_role(self):
        role = RoleVO.USER
        assert role.value == "USER"
        assert str(role) == "USER"
        assert role.is_user() is True
        assert role.is_admin() is False

    def test_admin_role(self):
        role = RoleVO.ADMIN
        assert role.value == "ADMIN"
        assert str(role) == "ADMIN"
        assert role.is_admin() is True
        assert role.is_user() is False

    def test_role_equality(self):
        role1 = RoleVO.USER
        role2 = RoleVO.USER
        role3 = RoleVO.ADMIN

        assert role1 == role2
        assert role1 != role3
        assert role1 == "USER"  # StrEnum 특성

    def test_role_from_string(self):
        user_role = RoleVO("USER")
        admin_role = RoleVO("ADMIN")

        assert user_role == RoleVO.USER
        assert admin_role == RoleVO.ADMIN
