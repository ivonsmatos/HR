"""
TYPE HINTS ADDITIONS for apps/core/views.py

Enhanced views with comprehensive type hints
"""

from typing import Optional, Dict, Any, List, Union
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import viewsets, status
from rest_framework.serializers import Serializer
from django.db.models import QuerySet, Model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.core.models import User, Company, UserProfile
from apps.core.serializers import (
    UserSerializer,
    CompanySerializer,
    UserProfileSerializer,
)


# ============================================================================
# API Views with Type Hints
# ============================================================================


class TypedViewMixin:
    """
    Mixin providing common typed methods for all views
    """

    def get_current_user(self, request: Request) -> Optional[User]:
        """Get authenticated user from request"""
        return request.user if request.user.is_authenticated else None

    def get_current_company(self, request: Request) -> Optional[Company]:
        """Get user's company from request"""
        user = self.get_current_user(request)
        return user.company if user else None

    def get_serializer_context(self, request: Request) -> Dict[str, Any]:
        """Get common serializer context"""
        return {
            "request": request,
            "format": self.format_kwarg,
            "view": self,
            "user": self.get_current_user(request),
            "company": self.get_current_company(request),
        }

    def success_response(
        self,
        data: Any = None,
        message: str = "Success",
        status_code: int = status.HTTP_200_OK,
    ) -> Response:
        """Generate standardized success response"""
        return Response(
            {
                "status": "success",
                "message": message,
                "data": data,
            },
            status=status_code,
        )

    def error_response(
        self,
        error: str,
        details: Dict[str, Any] = None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ) -> Response:
        """Generate standardized error response"""
        return Response(
            {
                "status": "error",
                "error": error,
                "details": details or {},
            },
            status=status_code,
        )


class UserViewSet(TypedViewMixin, viewsets.ModelViewSet):
    """
    User management viewset with comprehensive type hints
    
    Methods:
        GET /api/v1/users/ - List all users
        POST /api/v1/users/ - Create new user
        GET /api/v1/users/{id}/ - Get specific user
        PUT /api/v1/users/{id}/ - Update user
        DELETE /api/v1/users/{id}/ - Delete user
    """

    queryset: QuerySet = User.objects.all()
    serializer_class: type = UserSerializer
    permission_classes: List = [IsAuthenticated]
    filter_backends: List = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields: List[str] = ["is_active", "is_employee", "is_contractor"]
    search_fields: List[str] = ["username", "email", "first_name", "last_name"]
    ordering_fields: List[str] = ["created_at", "username", "email"]
    ordering: str = "-created_at"

    def get_queryset(self) -> QuerySet:
        """
        Get filtered queryset based on user's company
        
        Returns:
            QuerySet: Filtered user queryset
        """
        queryset = super().get_queryset()
        user = self.get_current_user(self.request)
        
        if user and user.company:
            queryset = queryset.filter(company=user.company)
        
        return queryset.filter(is_active=True)

    def get_object(self) -> User:
        """
        Retrieve a user object with authorization check
        
        Returns:
            User: The requested user object
        """
        user = super().get_object()
        current_user = self.get_current_user(self.request)
        
        # Check authorization
        if user.company != current_user.company:
            self.permission_denied(self.request)
        
        return user

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Create a new user in the current company
        
        Args:
            request: HTTP request with user data
            *args: Positional arguments
            **kwargs: Keyword arguments
        
        Returns:
            Response: Created user data or error
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.save(company=self.get_current_company(request))
        
        return self.success_response(
            data=UserSerializer(user, context=self.get_serializer_context(request)).data,
            message="User created successfully",
            status_code=status.HTTP_201_CREATED,
        )

    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Update an existing user
        
        Args:
            request: HTTP request with updated user data
            *args: Positional arguments
            **kwargs: Keyword arguments
        
        Returns:
            Response: Updated user data or error
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
            context=self.get_serializer_context(request),
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return self.success_response(
            data=UserSerializer(user, context=self.get_serializer_context(request)).data,
            message="User updated successfully",
        )

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Soft-delete a user (set is_active to False)
        
        Args:
            request: HTTP request
            *args: Positional arguments
            **kwargs: Keyword arguments
        
        Returns:
            Response: Success message
        """
        instance = self.get_object()
        instance.is_active = False
        instance.save(update_fields=["is_active"])
        
        return self.success_response(
            message="User deleted successfully",
            status_code=status.HTTP_204_NO_CONTENT,
        )


class CompanyViewSet(TypedViewMixin, viewsets.ModelViewSet):
    """
    Company management viewset
    
    Methods:
        GET /api/v1/companies/ - List all companies (admin only)
        POST /api/v1/companies/ - Create new company
        GET /api/v1/companies/{id}/ - Get company details
        PUT /api/v1/companies/{id}/ - Update company
        DELETE /api/v1/companies/{id}/ - Delete company
    """

    queryset: QuerySet = Company.objects.all()
    serializer_class: type = CompanySerializer
    permission_classes: List = [IsAuthenticated]
    filter_backends: List = [SearchFilter, OrderingFilter]
    search_fields: List[str] = ["name", "slug", "email", "city"]
    ordering_fields: List[str] = ["created_at", "name", "subscription_status"]
    ordering: str = "-created_at"

    def get_queryset(self) -> QuerySet:
        """
        Get company queryset (limited to user's company unless admin)
        
        Returns:
            QuerySet: Filtered company queryset
        """
        user = self.get_current_user(self.request)
        
        if user.is_superuser or user.is_staff:
            return super().get_queryset()
        
        # Regular users only see their own company
        if user.company:
            return super().get_queryset().filter(id=user.company.id)
        
        return super().get_queryset().none()

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Create a new company (admin only)"""
        if not request.user.is_staff:
            return self.error_response(
                error="Permission denied",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        
        return super().create(request, *args, **kwargs)

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Get company details with additional metrics
        
        Returns:
            Response: Company data with metrics
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        data = serializer.data
        data["metrics"] = {
            "total_users": instance.get_user_count(),
            "is_subscription_active": instance.is_subscription_active(),
        }
        
        return self.success_response(data=data)


class UserProfileViewSet(TypedViewMixin, viewsets.ModelViewSet):
    """
    User Profile management viewset
    """

    queryset: QuerySet = UserProfile.objects.all()
    serializer_class: type = UserProfileSerializer
    permission_classes: List = [IsAuthenticated]

    def get_queryset(self) -> QuerySet:
        """Get profiles for current company"""
        user = self.get_current_user(self.request)
        
        if user and user.company:
            return super().get_queryset().filter(company=user.company)
        
        return super().get_queryset().none()

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Get user profile with manager information
        
        Returns:
            Response: Profile data with manager details
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        data = serializer.data
        if instance.manager:
            data["manager_info"] = {
                "id": instance.manager.id,
                "name": instance.manager.get_full_name(),
                "email": instance.manager.email,
            }
        
        data["subordinates_count"] = instance.get_subordinates_count()
        
        return self.success_response(data=data)


# ============================================================================
# Standalone API Views with Type Hints
# ============================================================================


@api_view(["GET"])
@permission_classes([AllowAny])
def api_health_check(request: Request) -> Response:
    """
    Health check endpoint
    
    Args:
        request: HTTP request
    
    Returns:
        Response: Health status
    """
    return Response(
        {
            "status": "ok",
            "service": "SyncRH API",
            "version": "1.0.0",
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def current_user_profile(request: Request) -> Response:
    """
    Get current authenticated user's profile
    
    Args:
        request: HTTP request from authenticated user
    
    Returns:
        Response: Current user data
    """
    user = request.user
    serializer = UserSerializer(
        user,
        context={"request": request},
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def increment_user_login(request: Request) -> Response:
    """
    Increment user login counter
    
    Args:
        request: HTTP request from authenticated user
    
    Returns:
        Response: Updated login count
    """
    user = request.user
    user.increment_login_count()
    
    return Response(
        {
            "login_count": user.login_count,
            "last_activity": user.last_activity,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_company_users(request: Request) -> Response:
    """
    Get all users in current user's company
    
    Args:
        request: HTTP request from authenticated user
    
    Returns:
        Response: List of users in company
    """
    user = request.user
    
    if not user.company:
        return Response(
            {"error": "User has no company assigned"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    company_users = user.company.get_users()
    serializer = UserSerializer(
        company_users,
        many=True,
        context={"request": request},
    )
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_management_stats(request: Request) -> Response:
    """
    Get user management statistics for company
    
    Args:
        request: HTTP request from authenticated user
    
    Returns:
        Response: Statistics dictionary
    """
    user = request.user
    
    if not user.company:
        return Response(
            {"error": "User has no company assigned"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    company = user.company
    
    stats: Dict[str, Any] = {
        "company_name": company.name,
        "total_users": company.get_user_count(),
        "active_users": company.users.filter(is_active=True).count(),
        "employees": company.users.filter(is_employee=True).count(),
        "contractors": company.users.filter(is_contractor=True).count(),
        "admins": company.users.filter(is_staff=True).count(),
        "verified_users": company.users.filter(is_verified=True).count(),
    }
    
    return Response(stats, status=status.HTTP_200_OK)
