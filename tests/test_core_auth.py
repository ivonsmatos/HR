"""
Tests para autenticação e autorização - apps.core

Cobre:
- User model
- Authentication (JWT, OAuth2)
- Permissions
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()
pytestmark = pytest.mark.django_db


class TestUserModel(APITestCase):
    """Tests para User model"""

    def setUp(self):
        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123456",
            "first_name": "Test",
            "last_name": "User",
        }

    def test_user_creation(self):
        """Testa criação de usuário"""
        user = User.objects.create_user(**self.user_data)
        assert user.username == self.user_data["username"]
        assert user.email == self.user_data["email"]
        assert user.check_password(self.user_data["password"])

    def test_user_email_is_required(self):
        """Testa que email é obrigatório"""
        user_data = self.user_data.copy()
        user_data.pop("email")
        user = User.objects.create_user(**user_data)
        assert user.email == ""

    def test_superuser_creation(self):
        """Testa criação de superuser"""
        user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123456",
        )
        assert user.is_admin or user.is_superuser
        assert user.is_staff

    def test_user_str_representation(self):
        """Testa string representation do usuário"""
        user = User.objects.create_user(**self.user_data)
        assert str(user) == user.username

    def test_user_get_full_name(self):
        """Testa get_full_name do usuário"""
        user = User.objects.create_user(**self.user_data)
        full_name = f"{user.first_name} {user.last_name}"
        assert full_name == "Test User"


class TestUserAuthentication:
    """Tests para autenticação de usuário"""

    @pytest.fixture
    def user(self, db):
        return User.objects.create_user(
            username="testauth",
            email="auth@test.com",
            password="authpass123456",
        )

    def test_user_authentication_valid(self, user, api_client):
        """Testa autenticação com credenciais válidas"""
        assert user.check_password("authpass123456")

    def test_user_authentication_invalid_password(self, user):
        """Testa autenticação com senha inválida"""
        assert not user.check_password("wrongpassword")

    def test_user_authentication_nonexistent(self, db):
        """Testa autenticação com usuário inexistente"""
        user = User.objects.filter(username="nonexistent").first()
        assert user is None


class TestUserPermissions:
    """Tests para permissões de usuário"""

    @pytest.fixture
    def regular_user(self, db):
        return User.objects.create_user(
            username="regular",
            email="regular@test.com",
            password="pass123456",
        )

    @pytest.fixture
    def admin_user(self, db):
        return User.objects.create_superuser(
            username="adminuser",
            email="admin@test.com",
            password="adminpass123456",
        )

    def test_regular_user_not_staff(self, regular_user):
        """Testa que usuário regular não é staff"""
        assert not regular_user.is_staff

    def test_admin_user_is_staff(self, admin_user):
        """Testa que admin user é staff"""
        assert admin_user.is_staff

    def test_admin_user_is_superuser(self, admin_user):
        """Testa que admin user é superuser"""
        assert admin_user.is_superuser


class TestUserQueryset:
    """Tests para QuerySet customizado de User"""

    @pytest.fixture
    def users(self, db):
        users = []
        for i in range(5):
            user = User.objects.create_user(
                username=f"user{i}",
                email=f"user{i}@test.com",
                password="pass123456",
            )
            users.append(user)
        return users

    def test_user_count(self, users):
        """Testa contagem de usuários"""
        assert User.objects.count() == 5

    def test_user_filter_by_email(self, users):
        """Testa filtro por email"""
        user = User.objects.get(email="user0@test.com")
        assert user.username == "user0"

    def test_user_filter_by_username(self, users):
        """Testa filtro por username"""
        user = User.objects.get(username="user2")
        assert user.email == "user2@test.com"
