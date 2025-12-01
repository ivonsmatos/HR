"""
Extended Test Suite - 25+ New Tests

Integration tests, transaction tests, cache tests, multi-tenancy tests, and error handling
"""

import pytest
from django.test import TestCase, TransactionTestCase, Client
from django.contrib.auth import get_user_model
from django.db import transaction, IntegrityError
from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from apps.core.models import Company, User, UserProfile, CompanyDomain
from apps.core.serializers import UserSerializer, CompanySerializer


User = get_user_model()


class UserModelIntegrationTests(TestCase):
    """Integration tests for User model"""

    def setUp(self):
        """Setup test data"""
        self.company = Company.objects.create(
            name="Test Company",
            slug="test-company",
            email="admin@test.com",
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            company=self.company,
        )

    def test_user_creation_with_company(self):
        """Test user is created with company assignment"""
        assert self.user.company == self.company
        assert self.user.username == "testuser"
        assert self.user.is_active

    def test_user_full_name_generation(self):
        """Test full name generation"""
        self.user.first_name = "John"
        self.user.last_name = "Doe"
        self.user.save()
        
        assert self.user.get_full_name() == "John Doe"

    def test_user_without_full_name(self):
        """Test fallback to username when no full name"""
        assert self.user.get_full_name() == "testuser"

    def test_user_is_admin(self):
        """Test admin status detection"""
        assert not self.user.is_admin_user()
        
        self.user.is_staff = True
        assert self.user.is_admin_user()

    def test_user_to_dict_conversion(self):
        """Test user to dictionary conversion"""
        user_dict = self.user.to_dict()
        
        assert user_dict["username"] == "testuser"
        assert user_dict["email"] == "test@example.com"
        assert "id" in user_dict
        assert "created_at" in user_dict

    def test_user_to_dict_with_company(self):
        """Test user to dict with company info"""
        user_dict = self.user.to_dict(include_company=True)
        
        assert "company" in user_dict
        assert user_dict["company"]["slug"] == "test-company"

    def test_user_increment_login_count(self):
        """Test login counter increment"""
        initial_count = self.user.login_count
        
        self.user.increment_login_count()
        
        self.user.refresh_from_db()
        assert self.user.login_count == initial_count + 1

    def test_user_multiple_login_increments(self):
        """Test multiple login count increments"""
        for i in range(5):
            self.user.increment_login_count()
        
        self.user.refresh_from_db()
        assert self.user.login_count == 5


class CompanyModelIntegrationTests(TestCase):
    """Integration tests for Company model"""

    def setUp(self):
        """Setup test data"""
        self.company = Company.objects.create(
            name="ACME Corp",
            slug="acme-corp",
            email="admin@acme.com",
            currency="USD",
            timezone="America/New_York",
        )

    def test_company_creation(self):
        """Test company is created correctly"""
        assert self.company.name == "ACME Corp"
        assert self.company.is_on_trial is True
        assert self.company.is_verified is False

    def test_company_get_user_count(self):
        """Test user count method"""
        # Initially no users
        assert self.company.get_user_count() == 0
        
        # Add users
        for i in range(3):
            User.objects.create_user(
                username=f"user{i}",
                email=f"user{i}@acme.com",
                password="pass123",
                company=self.company,
            )
        
        assert self.company.get_user_count() == 3

    def test_company_get_users_queryset(self):
        """Test get_users queryset method"""
        # Create users
        active_user = User.objects.create_user(
            username="active",
            email="active@acme.com",
            password="pass123",
            company=self.company,
        )
        
        inactive_user = User.objects.create_user(
            username="inactive",
            email="inactive@acme.com",
            password="pass123",
            company=self.company,
        )
        inactive_user.is_active = False
        inactive_user.save()
        
        users = self.company.get_users()
        
        assert active_user in users
        assert inactive_user not in users

    def test_company_subscription_active_check(self):
        """Test subscription active status"""
        # Active subscription
        self.company.subscription_status = "active"
        self.company.subscription_ends_at = None
        self.company.save()
        
        assert self.company.is_subscription_active()

    def test_company_subscription_expired_check(self):
        """Test expired subscription detection"""
        from datetime import datetime, timedelta
        
        self.company.subscription_status = "active"
        self.company.subscription_ends_at = datetime.now() - timedelta(days=1)
        self.company.save()
        
        assert not self.company.is_subscription_active()

    def test_company_str_representation(self):
        """Test company string representation"""
        assert str(self.company) == "ACME Corp (acme-corp)"


class TransactionModelTests(TransactionTestCase):
    """Transaction-level tests for data integrity"""

    def test_user_creation_rollback_on_error(self):
        """Test transaction rollback on error"""
        company = Company.objects.create(
            name="Test",
            slug="test",
            email="test@test.com",
        )
        
        try:
            with transaction.atomic():
                user1 = User.objects.create_user(
                    username="user1",
                    email="user1@test.com",
                    company=company,
                )
                
                # Try to create duplicate - should fail
                user2 = User.objects.create_user(
                    username="user1",  # Duplicate username
                    email="user2@test.com",
                    company=company,
                )
        except IntegrityError:
            pass
        
        # Verify user1 was rolled back
        assert not User.objects.filter(username="user1").exists()

    def test_company_cascade_delete(self):
        """Test cascade delete of company removes users"""
        company = Company.objects.create(
            name="Delete Test",
            slug="delete-test",
            email="delete@test.com",
        )
        
        user = User.objects.create_user(
            username="deleteuser",
            email="delete@user.com",
            company=company,
        )
        
        user_id = user.id
        company.delete()
        
        # User should be deleted too
        assert not User.objects.filter(id=user_id).exists()


class UserProfileIntegrationTests(TestCase):
    """Integration tests for User Profile"""

    def setUp(self):
        """Setup test data"""
        self.company = Company.objects.create(
            name="Profile Test",
            slug="profile-test",
            email="profile@test.com",
        )
        
        self.user = User.objects.create_user(
            username="profileuser",
            email="profile@user.com",
            company=self.company,
        )
        
        self.profile = UserProfile.objects.create(
            user=self.user,
            company=self.company,
            job_title_full="Senior Engineer",
            department_full="Engineering",
        )

    def test_profile_creation(self):
        """Test profile is created"""
        assert self.profile.user == self.user
        assert self.profile.company == self.company

    def test_profile_manager_assignment(self):
        """Test manager assignment to profile"""
        manager = User.objects.create_user(
            username="manager",
            email="manager@user.com",
            company=self.company,
        )
        
        self.profile.manager = manager
        self.profile.save()
        
        assert self.profile.manager == manager
        assert self.profile.get_manager_name() == "manager"

    def test_profile_is_manager(self):
        """Test manager detection"""
        assert not self.profile.is_manager()
        
        subordinate = User.objects.create_user(
            username="subordinate",
            email="sub@user.com",
            company=self.company,
        )
        
        sub_profile = UserProfile.objects.create(
            user=subordinate,
            company=self.company,
            manager=self.user,
        )
        
        self.profile.refresh_from_db()
        assert self.profile.is_manager()

    def test_profile_subordinates_count(self):
        """Test subordinates counting"""
        assert self.profile.get_subordinates_count() == 0
        
        for i in range(3):
            sub = User.objects.create_user(
                username=f"sub{i}",
                email=f"sub{i}@user.com",
                company=self.company,
            )
            UserProfile.objects.create(
                user=sub,
                company=self.company,
                manager=self.user,
            )
        
        self.profile.refresh_from_db()
        assert self.profile.get_subordinates_count() == 3


class CacheIntegrationTests(TestCase):
    """Tests for caching behavior"""

    def setUp(self):
        """Setup test data"""
        self.company = Company.objects.create(
            name="Cache Test",
            slug="cache-test",
            email="cache@test.com",
        )

    def test_user_cache_operations(self):
        """Test user data caching"""
        cache_key = f"user_company_{self.company.id}"
        
        # Cache miss
        cached_data = cache.get(cache_key)
        assert cached_data is None
        
        # Set cache
        cache.set(cache_key, {"users": []}, 300)
        
        # Cache hit
        cached_data = cache.get(cache_key)
        assert cached_data is not None
        assert cached_data == {"users": []}

    def test_cache_invalidation(self):
        """Test cache invalidation on data change"""
        cache_key = f"company_users_{self.company.id}"
        cache.set(cache_key, {"count": 0}, 300)
        
        assert cache.get(cache_key) is not None
        
        # Invalidate cache
        cache.delete(cache_key)
        
        assert cache.get(cache_key) is None


class MultiTenancyTests(TestCase):
    """Tests for multi-tenancy data isolation"""

    def setUp(self):
        """Setup multiple companies"""
        self.company1 = Company.objects.create(
            name="Company 1",
            slug="company-1",
            email="comp1@test.com",
        )
        
        self.company2 = Company.objects.create(
            name="Company 2",
            slug="company-2",
            email="comp2@test.com",
        )
        
        # Create users for each company
        self.user1 = User.objects.create_user(
            username="user1",
            email="user1@test.com",
            company=self.company1,
        )
        
        self.user2 = User.objects.create_user(
            username="user2",
            email="user2@test.com",
            company=self.company2,
        )

    def test_users_isolated_by_company(self):
        """Test users are isolated by company"""
        company1_users = User.objects.filter(company=self.company1)
        company2_users = User.objects.filter(company=self.company2)
        
        assert self.user1 in company1_users
        assert self.user1 not in company2_users
        assert self.user2 in company2_users
        assert self.user2 not in company1_users

    def test_profiles_isolated_by_company(self):
        """Test profiles are isolated by company"""
        profile1 = UserProfile.objects.create(
            user=self.user1,
            company=self.company1,
        )
        
        profile2 = UserProfile.objects.create(
            user=self.user2,
            company=self.company2,
        )
        
        company1_profiles = UserProfile.objects.filter(company=self.company1)
        company2_profiles = UserProfile.objects.filter(company=self.company2)
        
        assert profile1 in company1_profiles
        assert profile1 not in company2_profiles
        assert profile2 in company2_profiles
        assert profile2 not in company1_profiles

    def test_cannot_query_across_tenants(self):
        """Test data cannot leak across tenants"""
        company1_users = self.company1.users.all()
        
        # Should only have company1 users
        assert self.user1 in company1_users
        assert self.user2 not in company1_users


class ErrorHandlingTests(APITestCase):
    """Tests for error handling and edge cases"""

    def setUp(self):
        """Setup test data"""
        self.client = APIClient()
        self.company = Company.objects.create(
            name="Error Test",
            slug="error-test",
            email="error@test.com",
        )
        
        self.user = User.objects.create_user(
            username="erroruser",
            email="error@user.com",
            password="pass123",
            company=self.company,
        )

    def test_user_not_found(self):
        """Test 404 on non-existent user"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("user-detail", kwargs={"pk": 99999}))
        
        assert response.status_code == 404

    def test_invalid_company_assignment(self):
        """Test invalid company assignment"""
        self.client.force_authenticate(user=self.user)
        
        # Try to access user from another company
        other_company = Company.objects.create(
            name="Other",
            slug="other",
            email="other@test.com",
        )
        
        other_user = User.objects.create_user(
            username="otheruser",
            email="other@user.com",
            company=other_company,
        )
        
        response = self.client.get(
            reverse("user-detail", kwargs={"pk": other_user.id})
        )
        
        # Should be 404 or 403 (different company)
        assert response.status_code in [403, 404]

    def test_missing_required_fields(self):
        """Test error on missing required fields"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post(
            reverse("user-list"),
            data={"username": "newuser"},  # Missing email and password
            format="json",
        )
        
        assert response.status_code == 400

    def test_duplicate_username(self):
        """Test error on duplicate username"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post(
            reverse("user-list"),
            data={
                "username": "erroruser",  # Duplicate
                "email": "new@test.com",
                "password": "newpass123",
            },
            format="json",
        )
        
        assert response.status_code == 400

    def test_invalid_email_format(self):
        """Test error on invalid email"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post(
            reverse("user-list"),
            data={
                "username": "newuser",
                "email": "notanemail",
                "password": "pass123",
            },
            format="json",
        )
        
        assert response.status_code == 400
