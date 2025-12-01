"""
API Documentation Configuration for DRF Spectacular

Adds comprehensive API documentation with Swagger/OpenAPI schema
"""

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework import viewsets, serializers
from typing import Optional, Dict, Any, List


# ============================================================================
# Custom Schemas for Documentation
# ============================================================================


class APIDocumentationSchema:
    """
    Schema definitions for API documentation
    """

    @staticmethod
    def get_user_schema() -> Dict[str, Any]:
        """Get User schema for documentation"""
        return {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "description": "User ID"},
                "username": {"type": "string", "description": "Username"},
                "email": {"type": "string", "format": "email", "description": "Email address"},
                "first_name": {"type": "string", "description": "First name"},
                "last_name": {"type": "string", "description": "Last name"},
                "phone": {"type": "string", "description": "Phone number"},
                "department": {"type": "string", "description": "Department"},
                "job_title": {"type": "string", "description": "Job title"},
                "is_active": {"type": "boolean", "description": "Is user active"},
                "is_verified": {"type": "boolean", "description": "Is user verified"},
                "is_employee": {"type": "boolean", "description": "Is employee"},
                "is_contractor": {"type": "boolean", "description": "Is contractor"},
            },
            "required": ["username", "email"],
        }

    @staticmethod
    def get_company_schema() -> Dict[str, Any]:
        """Get Company schema for documentation"""
        return {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "description": "Company ID"},
                "name": {"type": "string", "description": "Company name"},
                "slug": {"type": "string", "description": "URL slug"},
                "email": {"type": "string", "format": "email", "description": "Company email"},
                "phone": {"type": "string", "description": "Phone"},
                "website": {"type": "string", "format": "uri", "description": "Website URL"},
                "address": {"type": "string", "description": "Street address"},
                "city": {"type": "string", "description": "City"},
                "state": {"type": "string", "description": "State/Province"},
                "country": {"type": "string", "description": "Country"},
                "industry": {"type": "string", "description": "Industry"},
                "currency": {"type": "string", "description": "Currency code"},
                "subscription_status": {"type": "string", "enum": ["trial", "active", "paused", "cancelled", "expired"]},
            },
            "required": ["name", "slug", "email"],
        }


# ============================================================================
# Endpoint Documentation with Enhanced Docstrings
# ============================================================================


class DocumentedEndpoints:
    """
    Endpoint documentation with comprehensive docstrings
    """

    # ========================================================================
    # User Endpoints
    # ========================================================================

    @staticmethod
    def user_list_docstring() -> str:
        """Docstring for User list endpoint"""
        return """
        List all users in current company
        
        Retrieves a paginated list of active users in the authenticated user's company.
        
        Query Parameters:
            - is_active (boolean): Filter by active status
            - is_employee (boolean): Filter by employee status
            - is_contractor (boolean): Filter by contractor status
            - search (string): Search by username, email, first_name, or last_name
            - ordering (string): Order by created_at, username, or email
        
        Returns:
            - 200 OK: List of users
            - 401 Unauthorized: Not authenticated
            - 403 Forbidden: Insufficient permissions
        
        Example:
            GET /api/v1/users/?is_active=true&search=john&ordering=-created_at
        """

    @staticmethod
    def user_create_docstring() -> str:
        """Docstring for User create endpoint"""
        return """
        Create a new user in the current company
        
        Creates a new user account with the provided information.
        The user is automatically assigned to the authenticated user's company.
        
        Request Body:
            - username (string, required): Unique username
            - email (string, required): Email address
            - password (string, required): User password
            - first_name (string, optional): First name
            - last_name (string, optional): Last name
            - phone (string, optional): Phone number
            - department (string, optional): Department
            - job_title (string, optional): Job title
        
        Returns:
            - 201 Created: New user created successfully
            - 400 Bad Request: Invalid data
            - 401 Unauthorized: Not authenticated
        
        Example:
            POST /api/v1/users/
            {
                "username": "john.doe",
                "email": "john@example.com",
                "password": "secure_password_123",
                "first_name": "John",
                "last_name": "Doe"
            }
        """

    @staticmethod
    def user_detail_docstring() -> str:
        """Docstring for User detail endpoint"""
        return """
        Retrieve, update, or delete a specific user
        
        GET /api/v1/users/{id}/
            Returns user details
        
        PUT /api/v1/users/{id}/
            Updates all user fields
        
        PATCH /api/v1/users/{id}/
            Partially updates user fields
        
        DELETE /api/v1/users/{id}/
            Soft-deletes user (sets is_active=false)
        
        Returns:
            - 200 OK: Operation successful
            - 204 No Content: Deletion successful
            - 400 Bad Request: Invalid data
            - 401 Unauthorized: Not authenticated
            - 404 Not Found: User not found
        """

    # ========================================================================
    # Company Endpoints
    # ========================================================================

    @staticmethod
    def company_list_docstring() -> str:
        """Docstring for Company list endpoint"""
        return """
        List all companies (admin) or user's company
        
        Admin users see all companies. Regular users see only their own company.
        
        Query Parameters:
            - search (string): Search by name, slug, email, or city
            - ordering (string): Order by created_at, name, or subscription_status
        
        Returns:
            - 200 OK: List of companies
            - 401 Unauthorized: Not authenticated
        
        Example:
            GET /api/v1/companies/?search=acme&ordering=-created_at
        """

    @staticmethod
    def company_retrieve_docstring() -> str:
        """Docstring for Company detail endpoint"""
        return """
        Retrieve company details with metrics
        
        Returns company information and business metrics including:
        - Total users count
        - Subscription status
        - Trial/subscription expiration dates
        
        Returns:
            - 200 OK: Company details
            - 401 Unauthorized: Not authenticated
            - 404 Not Found: Company not found
        
        Example Response:
            {
                "id": 1,
                "name": "ACME Corp",
                "slug": "acme-corp",
                "email": "admin@acme.com",
                "subscription_status": "active",
                "metrics": {
                    "total_users": 42,
                    "is_subscription_active": true
                }
            }
        """

    # ========================================================================
    # Profile Endpoints
    # ========================================================================

    @staticmethod
    def profile_detail_docstring() -> str:
        """Docstring for User Profile detail endpoint"""
        return """
        Retrieve user profile with management hierarchy
        
        Returns detailed profile information including:
        - Manager information (if assigned)
        - Count of subordinates
        - Professional details
        - Preferences and settings
        
        Returns:
            - 200 OK: Profile details
            - 401 Unauthorized: Not authenticated
            - 404 Not Found: Profile not found
        
        Example Response:
            {
                "id": 1,
                "user": 1,
                "job_title_full": "Senior Software Engineer",
                "department_full": "Engineering",
                "manager_info": {
                    "id": 5,
                    "name": "Jane Smith",
                    "email": "jane@acme.com"
                },
                "subordinates_count": 3,
                "hire_date": "2022-01-15"
            }
        """

    # ========================================================================
    # Health Check Endpoints
    # ========================================================================

    @staticmethod
    def health_check_docstring() -> str:
        """Docstring for health check endpoints"""
        return """
        Health Check Endpoints
        
        /health/
            Basic service health check
            Returns: 200 OK if service is running
        
        /health/ready/
            Readiness probe for Kubernetes/load balancers
            Checks: Database connection, cache connectivity
            Returns: 200 OK if all systems ready
        
        /health/live/
            Liveness probe for Kubernetes/load balancers
            Checks: Process is alive and responsive
            Returns: 200 OK if process is alive
        
        Example:
            GET /health/
            Response: {
                "status": "ok",
                "service": "SyncRH API",
                "version": "1.0.0"
            }
        """


# ============================================================================
# URL Configuration for Swagger
# ============================================================================

SWAGGER_URLS = [
    # Swagger UI
    {
        "path": "api/schema/swagger-ui/",
        "name": "swagger-ui",
        "view": SpectacularSwaggerView.as_view(
            url_name="schema"
        ),
        "description": "Interactive Swagger UI documentation",
    },
    # ReDoc
    {
        "path": "api/schema/redoc/",
        "name": "redoc",
        "view": SpectacularRedocView.as_view(
            url_name="schema"
        ),
        "description": "ReDoc documentation",
    },
    # OpenAPI Schema
    {
        "path": "api/schema/",
        "name": "schema",
        "view": SpectacularAPIView.as_view(),
        "description": "OpenAPI schema JSON",
    },
]


# ============================================================================
# Installation Instructions
# ============================================================================

INSTALLATION_INSTRUCTIONS = """
SWAGGER/OPENAPI SETUP INSTRUCTIONS
==================================

1. Add to INSTALLED_APPS in settings.py:
    - 'drf_spectacular'

2. Add to REST_FRAMEWORK settings:
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',

3. Add URLs to urls.py:
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema')),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema')),

4. Access documentation:
    - Swagger UI: http://localhost:8000/api/schema/swagger-ui/
    - ReDoc: http://localhost:8000/api/schema/redoc/
    - OpenAPI JSON: http://localhost:8000/api/schema/

FEATURES
========
✅ Auto-generated from docstrings
✅ Interactive "Try it out" feature
✅ Request/response examples
✅ Parameter validation
✅ Schema visualization
✅ Multiple format support (JSON, YAML)

DOCSTRING FORMAT
================
Use the format shown in DocumentedEndpoints class:
- Description of endpoint
- Query Parameters (if applicable)
- Request Body (if applicable)
- Response codes and meanings
- Examples with actual requests/responses
"""
