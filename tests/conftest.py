"""
Pytest configuration and fixtures for Worksuite HR tests

Define fixtures here for use across all tests
"""

import os
import sys
import django

# Ensure we're using test settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.test')

# Setup Django
django.setup()

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from faker import Faker

fake = Faker()
User = get_user_model()


@pytest.fixture
def api_client():
    """Returns an API client instance"""
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, user):
    """Returns an authenticated API client"""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def user():
    """Creates a test user"""
    return User.objects.create_user(
        username=fake.user_name(),
        email=fake.email(),
        password="testpass123456",
        first_name=fake.first_name(),
        last_name=fake.last_name(),
    )


@pytest.fixture
def admin_user():
    """Creates a test admin user"""
    return User.objects.create_superuser(
        username="admin_test",
        email="admin@test.com",
        password="adminpass123456",
    )


@pytest.fixture
def authenticated_admin_client(api_client, admin_user):
    """Returns an authenticated admin API client"""
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def test_data():
    """Returns test data dictionary"""
    return {
        "username": fake.user_name(),
        "email": fake.email(),
        "password": "testpass123456",
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
    }
