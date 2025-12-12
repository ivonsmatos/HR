"""Core app URLs."""
from django.urls import path
from .views import lgpd_consent

app_name = "core"

urlpatterns = [
    path('privacy/lgpd-consent/', lgpd_consent, name='lgpd_consent'),
    # Placeholder for future core endpoints
    # path('users/', UserListView.as_view(), name='user-list'),
    # path('companies/', CompanyListView.as_view(), name='company-list'),
]
