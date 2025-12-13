"""
============================================================================
Zero-Trust Security - API URLs
============================================================================

Configuração de rotas da API REST para o módulo Zero-Trust Security.
Endpoints para gerenciamento de dispositivos, tokens e verificação de acesso.

@version 1.0.0
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api import (
    TrustedDeviceViewSet,
    AccessContextViewSet,
    ContinuousAuthViewSet,
    SecurityPolicyViewSet,
    UserBehaviorProfileViewSet,
    APISecurityTokenViewSet,
    ThreatIndicatorViewSet,
    ZeroTrustVerifyView,
    DeviceRegistrationView,
    TokenGenerationView,
    RiskAssessmentView,
)

# Router para ViewSets
router = DefaultRouter()
router.register(r'devices', TrustedDeviceViewSet, basename='trusted-device')
router.register(r'contexts', AccessContextViewSet, basename='access-context')
router.register(r'sessions', ContinuousAuthViewSet, basename='continuous-auth')
router.register(r'policies', SecurityPolicyViewSet, basename='security-policy')
router.register(r'behaviors', UserBehaviorProfileViewSet, basename='user-behavior')
router.register(r'tokens', APISecurityTokenViewSet, basename='api-token')
router.register(r'threats', ThreatIndicatorViewSet, basename='threat-indicator')

app_name = 'zero_trust'

urlpatterns = [
    # ViewSets registrados no router
    path('', include(router.urls)),
    
    # Endpoints especiais
    path('verify/', ZeroTrustVerifyView.as_view(), name='verify-access'),
    path('devices/register/', DeviceRegistrationView.as_view(), name='register-device'),
    path('tokens/generate/', TokenGenerationView.as_view(), name='generate-token'),
    path('risk/assess/', RiskAssessmentView.as_view(), name='assess-risk'),
]
