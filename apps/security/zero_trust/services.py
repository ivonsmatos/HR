"""
SyncRH - Zero-Trust Security Services
======================================
Serviços para implementação de Zero-Trust Security.
"""

import hashlib
import secrets
import logging
from datetime import timedelta
from typing import Dict, List, Tuple, Optional
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger('security.zero_trust')


class ZeroTrustService:
    """
    Serviço central para operações Zero-Trust.
    """
    
    @staticmethod
    def evaluate_access_request(
        user,
        device_fingerprint: str,
        ip_address: str,
        resource_path: str,
        request_context: Dict
    ) -> Tuple[bool, str, Dict]:
        """
        Avalia uma requisição de acesso usando Zero-Trust.
        
        Returns:
            (allowed, reason, metadata)
        """
        evaluation = {
            'user_score': 0,
            'device_score': 0,
            'network_score': 0,
            'behavior_score': 0,
            'resource_score': 0,
            'total_score': 0,
            'factors': [],
        }
        
        # 1. Avaliar usuário
        user_score, user_factors = ZeroTrustService._evaluate_user(user)
        evaluation['user_score'] = user_score
        evaluation['factors'].extend(user_factors)
        
        # 2. Avaliar dispositivo
        device_score, device_factors = ZeroTrustService._evaluate_device(
            user, device_fingerprint
        )
        evaluation['device_score'] = device_score
        evaluation['factors'].extend(device_factors)
        
        # 3. Avaliar rede/IP
        network_score, network_factors = ZeroTrustService._evaluate_network(
            ip_address, request_context
        )
        evaluation['network_score'] = network_score
        evaluation['factors'].extend(network_factors)
        
        # 4. Avaliar comportamento
        behavior_score, behavior_factors = ZeroTrustService._evaluate_behavior(
            user, request_context
        )
        evaluation['behavior_score'] = behavior_score
        evaluation['factors'].extend(behavior_factors)
        
        # 5. Avaliar recurso solicitado
        resource_score, resource_factors = ZeroTrustService._evaluate_resource(
            resource_path, user
        )
        evaluation['resource_score'] = resource_score
        evaluation['factors'].extend(resource_factors)
        
        # Calcular score total (média ponderada)
        weights = {
            'user': 0.25,
            'device': 0.20,
            'network': 0.20,
            'behavior': 0.20,
            'resource': 0.15,
        }
        
        total = (
            evaluation['user_score'] * weights['user'] +
            evaluation['device_score'] * weights['device'] +
            evaluation['network_score'] * weights['network'] +
            evaluation['behavior_score'] * weights['behavior'] +
            evaluation['resource_score'] * weights['resource']
        )
        
        evaluation['total_score'] = round(total, 2)
        
        # Decisão baseada no score (score alto = confiável)
        if evaluation['total_score'] >= 70:
            return True, 'Access granted - High trust score', evaluation
        elif evaluation['total_score'] >= 50:
            return True, 'Access granted - Additional monitoring enabled', evaluation
        elif evaluation['total_score'] >= 30:
            return False, 'MFA required - Medium trust score', evaluation
        else:
            return False, 'Access denied - Low trust score', evaluation
    
    @staticmethod
    def _evaluate_user(user) -> Tuple[int, List[str]]:
        """Avalia confiabilidade do usuário."""
        score = 50  # Base score
        factors = []
        
        if not user or not user.is_authenticated:
            return 0, ['user_not_authenticated']
        
        # Usuário ativo
        if user.is_active:
            score += 20
        else:
            return 0, ['user_inactive']
        
        # Tempo desde criação da conta
        account_age = (timezone.now() - user.date_joined).days
        if account_age > 365:
            score += 15
            factors.append('mature_account')
        elif account_age > 90:
            score += 10
            factors.append('established_account')
        elif account_age < 7:
            score -= 10
            factors.append('new_account')
        
        # Verificar 2FA
        if hasattr(user, 'two_factor_auth') and user.two_factor_auth.is_enabled:
            score += 15
            factors.append('mfa_enabled')
        
        return min(100, max(0, score)), factors
    
    @staticmethod
    def _evaluate_device(user, fingerprint: str) -> Tuple[int, List[str]]:
        """Avalia confiabilidade do dispositivo."""
        score = 30  # Base score para dispositivo desconhecido
        factors = []
        
        if not user or not fingerprint:
            return score, ['device_unknown']
        
        # Verificar se dispositivo é conhecido
        cache_key = f"trusted_device:{user.id}:{fingerprint}"
        device_data = cache.get(cache_key)
        
        if device_data:
            trust_level = device_data.get('trust_level', 'untrusted')
            
            if trust_level == 'corporate':
                score = 100
                factors.append('corporate_device')
            elif trust_level == 'elevated':
                score = 85
                factors.append('elevated_trust_device')
            elif trust_level == 'standard':
                score = 70
                factors.append('standard_trust_device')
            elif trust_level == 'limited':
                score = 50
                factors.append('limited_trust_device')
            else:
                score = 30
                factors.append('untrusted_device')
            
            # Verificar última vez visto
            last_seen = device_data.get('last_seen')
            if last_seen:
                days_since = (timezone.now() - last_seen).days
                if days_since > 30:
                    score -= 10
                    factors.append('device_not_seen_recently')
        else:
            factors.append('device_first_seen')
        
        return min(100, max(0, score)), factors
    
    @staticmethod
    def _evaluate_network(ip_address: str, context: Dict) -> Tuple[int, List[str]]:
        """Avalia confiabilidade da rede."""
        score = 50  # Base score
        factors = []
        
        # IP privado/corporativo
        if ip_address.startswith(('10.', '192.168.', '172.')):
            score += 30
            factors.append('private_network')
        elif ip_address.startswith('127.'):
            score += 40
            factors.append('localhost')
        else:
            # IP público - verificar reputação
            reputation = ZeroTrustService._check_ip_reputation(ip_address)
            score += reputation
            if reputation < 0:
                factors.append('suspicious_ip')
            elif reputation > 10:
                factors.append('known_good_ip')
        
        # Verificar se IP está na lista de IPs do usuário
        if context.get('is_known_ip'):
            score += 15
            factors.append('known_user_ip')
        
        # VPN detectada
        if context.get('is_vpn'):
            score -= 10  # VPN não é necessariamente ruim, mas adiciona incerteza
            factors.append('vpn_detected')
        
        return min(100, max(0, score)), factors
    
    @staticmethod
    def _check_ip_reputation(ip: str) -> int:
        """Verifica reputação do IP."""
        # Em produção, integrar com serviços de threat intelligence
        cache_key = f"ip_reputation:{ip}"
        reputation = cache.get(cache_key)
        
        if reputation is not None:
            return reputation
        
        # Default: neutro
        reputation = 0
        cache.set(cache_key, reputation, 3600)
        return reputation
    
    @staticmethod
    def _evaluate_behavior(user, context: Dict) -> Tuple[int, List[str]]:
        """Avalia comportamento do usuário."""
        score = 60  # Base score
        factors = []
        
        if not user or not user.is_authenticated:
            return 50, []
        
        # Verificar horário
        now = timezone.localtime()
        if 7 <= now.hour <= 20 and now.weekday() < 5:
            score += 10
            factors.append('business_hours')
        else:
            score -= 5
            factors.append('outside_business_hours')
        
        # Verificar frequência de acesso
        access_count = ZeroTrustService._get_recent_access_count(user.id)
        if access_count > 100:  # Muitos acessos = possível ataque
            score -= 20
            factors.append('high_access_frequency')
        elif access_count < 5:  # Poucos acessos = padrão normal ou conta dormant
            factors.append('low_activity')
        
        # Verificar falhas recentes de autenticação
        failed_auths = ZeroTrustService._get_failed_auth_count(user.id)
        if failed_auths > 3:
            score -= 30
            factors.append('recent_auth_failures')
        
        return min(100, max(0, score)), factors
    
    @staticmethod
    def _get_recent_access_count(user_id: int) -> int:
        """Conta acessos recentes do usuário."""
        cache_key = f"access_count:{user_id}"
        return cache.get(cache_key, 0)
    
    @staticmethod
    def _get_failed_auth_count(user_id: int) -> int:
        """Conta falhas de autenticação recentes."""
        cache_key = f"failed_auth:{user_id}"
        return cache.get(cache_key, 0)
    
    @staticmethod
    def _evaluate_resource(resource_path: str, user) -> Tuple[int, List[str]]:
        """Avalia se usuário tem acesso ao recurso."""
        score = 70  # Base score
        factors = []
        
        # Recursos públicos
        public_paths = ['/api/public/', '/health/', '/api/auth/']
        if any(resource_path.startswith(p) for p in public_paths):
            return 100, ['public_resource']
        
        # Recursos sensíveis
        sensitive_paths = {
            '/api/lgpd/': ['lgpd.view', 'lgpd.manage'],
            '/api/nist/': ['nist.view', 'nist.manage'],
            '/api/security/': ['security.admin'],
            '/admin/': ['admin.access'],
            '/api/finance/': ['finance.view', 'finance.manage'],
        }
        
        for path, required_perms in sensitive_paths.items():
            if resource_path.startswith(path):
                if user and user.is_authenticated:
                    # Verificar permissões (simplificado)
                    if user.is_superuser:
                        score = 80
                        factors.append('superuser_access')
                    elif user.is_staff:
                        score = 70
                        factors.append('staff_access')
                    else:
                        score = 50
                        factors.append('limited_permissions')
                else:
                    score = 20
                    factors.append('auth_required_resource')
                
                factors.append('sensitive_resource')
                break
        
        return min(100, max(0, score)), factors


class DeviceTrustService:
    """
    Serviço para gerenciamento de confiança de dispositivos.
    """
    
    @staticmethod
    def register_device(
        user,
        fingerprint: str,
        device_info: Dict,
        ip_address: str
    ) -> Dict:
        """Registra novo dispositivo."""
        device_id = hashlib.sha256(
            f"{user.id}:{fingerprint}".encode()
        ).hexdigest()[:32]
        
        device_data = {
            'device_id': device_id,
            'user_id': user.id,
            'fingerprint': fingerprint,
            'trust_level': 'untrusted',
            'device_type': device_info.get('device_type', 'unknown'),
            'browser': device_info.get('browser', 'unknown'),
            'os': device_info.get('os', 'unknown'),
            'first_seen': timezone.now().isoformat(),
            'last_seen': timezone.now().isoformat(),
            'last_ip': ip_address,
            'is_verified': False,
        }
        
        # Salvar no cache (em produção, salvar no banco)
        cache_key = f"trusted_device:{user.id}:{fingerprint}"
        cache.set(cache_key, device_data, 86400 * 30)  # 30 dias
        
        logger.info(f"Device registered: {device_id} for user {user.id}")
        
        return device_data
    
    @staticmethod
    def verify_device(user, fingerprint: str, verification_code: str) -> bool:
        """Verifica dispositivo com código."""
        cache_key = f"trusted_device:{user.id}:{fingerprint}"
        device_data = cache.get(cache_key)
        
        if not device_data:
            return False
        
        # Verificar código (em produção, usar código enviado por email/SMS)
        expected_code = cache.get(f"device_verify_code:{user.id}:{fingerprint}")
        
        if verification_code == expected_code:
            device_data['is_verified'] = True
            device_data['trust_level'] = 'standard'
            device_data['verified_at'] = timezone.now().isoformat()
            cache.set(cache_key, device_data, 86400 * 30)
            
            logger.info(f"Device verified: {device_data['device_id']}")
            return True
        
        return False
    
    @staticmethod
    def elevate_trust(user, fingerprint: str, new_level: str) -> bool:
        """Eleva nível de confiança do dispositivo."""
        valid_levels = ['limited', 'standard', 'elevated', 'corporate']
        if new_level not in valid_levels:
            return False
        
        cache_key = f"trusted_device:{user.id}:{fingerprint}"
        device_data = cache.get(cache_key)
        
        if device_data:
            device_data['trust_level'] = new_level
            cache.set(cache_key, device_data, 86400 * 30)
            return True
        
        return False
    
    @staticmethod
    def revoke_device(user, fingerprint: str, reason: str = '') -> bool:
        """Revoga confiança do dispositivo."""
        cache_key = f"trusted_device:{user.id}:{fingerprint}"
        device_data = cache.get(cache_key)
        
        if device_data:
            device_data['trust_level'] = 'untrusted'
            device_data['is_verified'] = False
            device_data['revoked_at'] = timezone.now().isoformat()
            device_data['revoked_reason'] = reason
            cache.set(cache_key, device_data, 86400 * 7)  # Manter histórico por 7 dias
            
            logger.warning(f"Device revoked: {device_data['device_id']} - {reason}")
            return True
        
        return False


class ContinuousAuthService:
    """
    Serviço de autenticação contínua.
    """
    
    CONFIDENCE_DECAY_RATE = 5  # Pontos por período
    DECAY_INTERVAL_MINUTES = 15
    MIN_CONFIDENCE_THRESHOLD = 70
    
    @staticmethod
    def create_session(
        user,
        device_fingerprint: str,
        auth_methods: List[str]
    ) -> Dict:
        """Cria sessão de autenticação contínua."""
        session_key = secrets.token_urlsafe(32)
        
        session_data = {
            'session_key': session_key,
            'user_id': user.id,
            'device_fingerprint': device_fingerprint,
            'confidence_score': 100,
            'auth_methods': auth_methods,
            'auth_level': len(auth_methods),
            'created_at': timezone.now().isoformat(),
            'last_verification': timezone.now().isoformat(),
            'expires_at': (timezone.now() + timedelta(hours=8)).isoformat(),
        }
        
        cache_key = f"continuous_auth:{session_key}"
        cache.set(cache_key, session_data, 28800)  # 8 horas
        
        return session_data
    
    @staticmethod
    def verify_session(session_key: str) -> Tuple[bool, Optional[Dict]]:
        """Verifica sessão de autenticação contínua."""
        cache_key = f"continuous_auth:{session_key}"
        session_data = cache.get(cache_key)
        
        if not session_data:
            return False, None
        
        # Aplicar decay
        session_data = ContinuousAuthService._apply_decay(session_data)
        
        # Verificar threshold
        if session_data['confidence_score'] < ContinuousAuthService.MIN_CONFIDENCE_THRESHOLD:
            session_data['requires_reauthentication'] = True
            return False, session_data
        
        return True, session_data
    
    @staticmethod
    def _apply_decay(session_data: Dict) -> Dict:
        """Aplica decay ao score de confiança."""
        last_verification = timezone.datetime.fromisoformat(session_data['last_verification'])
        elapsed = timezone.now() - last_verification
        intervals = int(elapsed.total_seconds() / (ContinuousAuthService.DECAY_INTERVAL_MINUTES * 60))
        
        if intervals > 0:
            decay = intervals * ContinuousAuthService.CONFIDENCE_DECAY_RATE
            session_data['confidence_score'] = max(0, session_data['confidence_score'] - decay)
        
        return session_data
    
    @staticmethod
    def boost_confidence(session_key: str, method: str) -> bool:
        """Aumenta confiança após verificação."""
        cache_key = f"continuous_auth:{session_key}"
        session_data = cache.get(cache_key)
        
        if not session_data:
            return False
        
        boost_amounts = {
            'password': 30,
            'mfa_totp': 40,
            'biometric': 50,
            'passkey': 50,
            'behavioral': 15,
        }
        
        boost = boost_amounts.get(method, 20)
        session_data['confidence_score'] = min(100, session_data['confidence_score'] + boost)
        session_data['last_verification'] = timezone.now().isoformat()
        session_data['requires_reauthentication'] = False
        
        if method not in session_data['auth_methods']:
            session_data['auth_methods'].append(method)
            session_data['auth_level'] = len(session_data['auth_methods'])
        
        cache.set(cache_key, session_data, 28800)
        return True


class ThreatIntelligenceService:
    """
    Serviço de inteligência de ameaças.
    """
    
    @staticmethod
    def check_ip(ip_address: str) -> Dict:
        """Verifica IP contra indicadores de ameaça."""
        result = {
            'ip': ip_address,
            'is_threat': False,
            'threat_level': 'none',
            'indicators': [],
        }
        
        # Verificar cache
        cache_key = f"threat_intel:ip:{ip_address}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        # Em produção, consultar APIs de threat intelligence
        # Exemplo: AbuseIPDB, VirusTotal, etc.
        
        cache.set(cache_key, result, 3600)
        return result
    
    @staticmethod
    def report_threat(
        indicator_type: str,
        indicator_value: str,
        threat_level: str,
        description: str
    ):
        """Reporta novo indicador de ameaça."""
        logger.warning(
            f"Threat reported: {indicator_type}={indicator_value} "
            f"level={threat_level} - {description}"
        )
        
        # Em produção, salvar no banco e notificar admin
