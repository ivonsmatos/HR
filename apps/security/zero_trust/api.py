"""
============================================================================
Zero-Trust Security - REST API
============================================================================

API REST para o módulo Zero-Trust Security.
Implementa ViewSets e Views para gerenciamento de segurança via API.

@version 1.0.0
"""

from rest_framework import viewsets, views, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404
import hashlib
import secrets

from .models import (
    TrustedDevice,
    AccessContext,
    ContinuousAuth,
    SecurityPolicy,
    UserBehaviorProfile,
    APISecurityToken,
    ThreatIndicator,
)
from .services import (
    ZeroTrustService,
    DeviceTrustService,
    ContinuousAuthService,
    ThreatIntelligenceService,
)
from .serializers import (
    TrustedDeviceSerializer,
    TrustedDeviceCreateSerializer,
    AccessContextSerializer,
    ContinuousAuthSerializer,
    SecurityPolicySerializer,
    UserBehaviorProfileSerializer,
    APISecurityTokenSerializer,
    APISecurityTokenCreateSerializer,
    ThreatIndicatorSerializer,
    RiskAssessmentSerializer,
)


# ============================================================================
# PERMISSIONS
# ============================================================================

class IsSecurityAdmin(permissions.BasePermission):
    """
    Permissão para administradores de segurança.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (request.user.is_superuser or 
             request.user.groups.filter(name='security_admins').exists())
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permissão para proprietário do recurso ou admin.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False


# ============================================================================
# TRUSTED DEVICE VIEWSET
# ============================================================================

class TrustedDeviceViewSet(viewsets.ModelViewSet):
    """
    API para gerenciamento de dispositivos confiáveis.
    """
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return TrustedDevice.objects.all()
        return TrustedDevice.objects.filter(user=user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TrustedDeviceCreateSerializer
        return TrustedDeviceSerializer
    
    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """
        Revoga a confiança de um dispositivo.
        """
        device = self.get_object()
        DeviceTrustService.revoke_trust(device)
        return Response({'status': 'revoked'})
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """
        Marca dispositivo como verificado.
        """
        device = self.get_object()
        device.verified = True
        device.verified_at = timezone.now()
        device.save()
        return Response({'status': 'verified'})
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """
        Retorna informações do dispositivo atual.
        """
        fingerprint = DeviceTrustService.generate_fingerprint(request)
        device = TrustedDevice.objects.filter(
            user=request.user,
            device_fingerprint=fingerprint
        ).first()
        
        if device:
            return Response(TrustedDeviceSerializer(device).data)
        return Response({'detail': 'Dispositivo não registrado'}, status=404)


# ============================================================================
# ACCESS CONTEXT VIEWSET
# ============================================================================

class AccessContextViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API para visualização de contextos de acesso (somente leitura).
    """
    serializer_class = AccessContextSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return AccessContext.objects.all().order_by('-created_at')
        return AccessContext.objects.filter(user=user).order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        Retorna os últimos 50 contextos de acesso.
        """
        queryset = self.get_queryset()[:50]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def denied(self, request):
        """
        Retorna apenas acessos negados.
        """
        queryset = self.get_queryset().filter(decision='deny')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# ============================================================================
# CONTINUOUS AUTH VIEWSET
# ============================================================================

class ContinuousAuthViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API para gerenciamento de sessões de autenticação contínua.
    """
    serializer_class = ContinuousAuthSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return ContinuousAuth.objects.all()
        return ContinuousAuth.objects.filter(user=user)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """
        Retorna a sessão atual do usuário.
        """
        session = ContinuousAuth.objects.filter(
            user=request.user,
            is_valid=True,
            expires_at__gt=timezone.now()
        ).order_by('-created_at').first()
        
        if session:
            return Response(ContinuousAuthSerializer(session).data)
        return Response({'detail': 'Nenhuma sessão ativa'}, status=404)
    
    @action(detail=True, methods=['post'])
    def refresh(self, request, pk=None):
        """
        Atualiza a confiança da sessão.
        """
        session = self.get_object()
        ContinuousAuthService.refresh_confidence(session)
        return Response(ContinuousAuthSerializer(session).data)
    
    @action(detail=True, methods=['post'])
    def invalidate(self, request, pk=None):
        """
        Invalida uma sessão.
        """
        session = self.get_object()
        session.is_valid = False
        session.save()
        return Response({'status': 'invalidated'})


# ============================================================================
# SECURITY POLICY VIEWSET
# ============================================================================

class SecurityPolicyViewSet(viewsets.ModelViewSet):
    """
    API para gerenciamento de políticas de segurança.
    """
    serializer_class = SecurityPolicySerializer
    permission_classes = [IsSecurityAdmin]
    queryset = SecurityPolicy.objects.all().order_by('-priority')
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        Retorna apenas políticas ativas.
        """
        policies = SecurityPolicy.objects.filter(is_active=True).order_by('-priority')
        serializer = self.get_serializer(policies, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        """
        Ativa/desativa uma política.
        """
        policy = self.get_object()
        policy.is_active = not policy.is_active
        policy.save()
        return Response({'status': 'active' if policy.is_active else 'inactive'})


# ============================================================================
# USER BEHAVIOR PROFILE VIEWSET
# ============================================================================

class UserBehaviorProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API para visualização de perfis comportamentais.
    """
    serializer_class = UserBehaviorProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return UserBehaviorProfile.objects.all()
        return UserBehaviorProfile.objects.filter(user=user)
    
    @action(detail=False, methods=['get'])
    def my_profile(self, request):
        """
        Retorna o perfil comportamental do usuário atual.
        """
        profile, created = UserBehaviorProfile.objects.get_or_create(
            user=request.user,
            defaults={'risk_score': 0}
        )
        return Response(UserBehaviorProfileSerializer(profile).data)


# ============================================================================
# API SECURITY TOKEN VIEWSET
# ============================================================================

class APISecurityTokenViewSet(viewsets.ModelViewSet):
    """
    API para gerenciamento de tokens de API.
    """
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return APISecurityToken.objects.all()
        return APISecurityToken.objects.filter(user=user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return APISecurityTokenCreateSerializer
        return APISecurityTokenSerializer
    
    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """
        Revoga um token de API.
        """
        token = self.get_object()
        token.is_active = False
        token.save()
        return Response({'status': 'revoked'})
    
    @action(detail=True, methods=['post'])
    def rotate(self, request, pk=None):
        """
        Rotaciona um token (gera novo, mantendo configurações).
        """
        old_token = self.get_object()
        
        # Gera novo token
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        
        # Cria novo com mesmas configurações
        new_token = APISecurityToken.objects.create(
            user=old_token.user,
            name=f"{old_token.name} (rotacionado)",
            token_hash=token_hash,
            token_prefix=raw_token[:8],
            scopes=old_token.scopes,
            allowed_ips=old_token.allowed_ips,
            rate_limit=old_token.rate_limit,
            expires_at=old_token.expires_at,
        )
        
        # Revoga antigo
        old_token.is_active = False
        old_token.save()
        
        return Response({
            'token': raw_token,
            'token_id': new_token.id,
            'message': 'Guarde este token, ele não será exibido novamente.'
        })


# ============================================================================
# THREAT INDICATOR VIEWSET
# ============================================================================

class ThreatIndicatorViewSet(viewsets.ModelViewSet):
    """
    API para gerenciamento de indicadores de ameaça.
    """
    serializer_class = ThreatIndicatorSerializer
    permission_classes = [IsSecurityAdmin]
    queryset = ThreatIndicator.objects.all().order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def check_ip(self, request):
        """
        Verifica se um IP está na lista de ameaças.
        """
        ip = request.data.get('ip')
        if not ip:
            return Response({'error': 'IP não fornecido'}, status=400)
        
        is_threat, indicators = ThreatIntelligenceService.check_ip_reputation(ip)
        return Response({
            'ip': ip,
            'is_threat': is_threat,
            'indicators': ThreatIndicatorSerializer(indicators, many=True).data
        })
    
    @action(detail=False, methods=['post'])
    def report(self, request):
        """
        Reporta novo indicador de ameaça.
        """
        indicator = ThreatIntelligenceService.report_threat(
            indicator_type=request.data.get('type'),
            value=request.data.get('value'),
            severity=request.data.get('severity', 'medium'),
            source='user_report',
            description=request.data.get('description', '')
        )
        return Response(ThreatIndicatorSerializer(indicator).data, status=201)


# ============================================================================
# CUSTOM VIEWS
# ============================================================================

class ZeroTrustVerifyView(views.APIView):
    """
    Endpoint para verificação Zero-Trust de um recurso.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """
        Verifica se o usuário pode acessar um recurso específico.
        """
        resource_path = request.data.get('resource')
        method = request.data.get('method', 'GET')
        
        if not resource_path:
            return Response({'error': 'Recurso não especificado'}, status=400)
        
        # Avalia acesso
        decision = ZeroTrustService.evaluate_access(request, resource_path, method)
        
        return Response({
            'resource': resource_path,
            'method': method,
            'decision': decision['decision'],
            'risk_score': decision['risk_score'],
            'reason': decision.get('reason'),
            'required_action': decision.get('required_action'),
        })


class DeviceRegistrationView(views.APIView):
    """
    Endpoint para registro de novo dispositivo.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """
        Registra o dispositivo atual como confiável.
        """
        device_name = request.data.get('name', 'Dispositivo sem nome')
        
        device = DeviceTrustService.register_device(request, device_name)
        
        return Response({
            'device_id': device.id,
            'device_name': device.device_name,
            'fingerprint': device.device_fingerprint[:12] + '...',
            'trust_level': device.trust_level,
            'message': 'Dispositivo registrado. Verificação pendente para elevação de confiança.'
        }, status=201)


class TokenGenerationView(views.APIView):
    """
    Endpoint para geração de novos tokens de API.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """
        Gera um novo token de API para o usuário.
        """
        name = request.data.get('name', f'Token {timezone.now().strftime("%Y%m%d%H%M%S")}')
        scopes = request.data.get('scopes', ['read'])
        expires_days = request.data.get('expires_days', 30)
        
        # Gera token seguro
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        
        from datetime import timedelta
        expires_at = timezone.now() + timedelta(days=expires_days)
        
        token = APISecurityToken.objects.create(
            user=request.user,
            name=name,
            token_hash=token_hash,
            token_prefix=raw_token[:8],
            scopes=scopes,
            expires_at=expires_at,
        )
        
        return Response({
            'token': raw_token,
            'token_id': token.id,
            'name': token.name,
            'scopes': token.scopes,
            'expires_at': token.expires_at.isoformat(),
            'warning': 'Guarde este token com segurança. Ele não será exibido novamente.'
        }, status=201)


class RiskAssessmentView(views.APIView):
    """
    Endpoint para avaliação de risco em tempo real.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """
        Retorna avaliação de risco atual do usuário.
        """
        # Avalia risco atual
        risk_data = ZeroTrustService.evaluate_access(request, '/api/', 'GET')
        
        # Obtém perfil comportamental
        profile, _ = UserBehaviorProfile.objects.get_or_create(
            user=request.user,
            defaults={'risk_score': 0}
        )
        
        # Obtém dispositivo atual
        fingerprint = DeviceTrustService.generate_fingerprint(request)
        device = TrustedDevice.objects.filter(
            user=request.user,
            device_fingerprint=fingerprint
        ).first()
        
        return Response({
            'user': {
                'username': request.user.username,
                'risk_score': profile.risk_score,
                'anomalies': profile.anomalies_detected,
            },
            'device': {
                'registered': device is not None,
                'trust_level': device.trust_level if device else None,
                'verified': device.verified if device else False,
            },
            'session': {
                'risk_score': risk_data['risk_score'],
                'factors': risk_data.get('factors', {}),
            },
            'recommendations': RiskAssessmentView._get_recommendations(
                risk_data['risk_score'],
                device,
                profile
            )
        })
    
    @staticmethod
    def _get_recommendations(risk_score, device, profile):
        """
        Gera recomendações baseadas na avaliação de risco.
        """
        recommendations = []
        
        if not device:
            recommendations.append({
                'type': 'device',
                'priority': 'high',
                'message': 'Registre este dispositivo para melhorar sua pontuação de confiança.'
            })
        elif not device.verified:
            recommendations.append({
                'type': 'device',
                'priority': 'medium',
                'message': 'Verifique seu dispositivo para elevar o nível de confiança.'
            })
        
        if risk_score < 50:
            recommendations.append({
                'type': 'security',
                'priority': 'high',
                'message': 'Seu acesso está com pontuação de risco baixa. Considere usar VPN corporativa ou conectar de uma rede conhecida.'
            })
        
        if profile.anomalies_detected > 5:
            recommendations.append({
                'type': 'behavior',
                'priority': 'medium',
                'message': 'Detectamos padrões incomuns em seu uso. Revise seu histórico de acesso.'
            })
        
        return recommendations
