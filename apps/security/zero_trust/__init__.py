"""
SyncRH - Zero-Trust Security Module
====================================
Implementação completa do modelo de segurança Zero-Trust:
"Never Trust, Always Verify"

Princípios implementados:
1. Verify Explicitly - Autenticação contínua
2. Least Privilege Access - Acesso mínimo necessário
3. Assume Breach - Monitoramento constante

Baseado em:
- NIST SP 800-207 (Zero Trust Architecture)
- Microsoft Zero Trust Model
- Google BeyondCorp

@version 1.0.0
"""

default_app_config = 'apps.security.zero_trust.apps.ZeroTrustConfig'

# Lazy imports para evitar importação circular durante inicialização do Django
# Importe diretamente quando necessário:
# from apps.security.zero_trust.middleware import ZeroTrustMiddleware

__all__ = [
    # Middleware
    'ZeroTrustMiddleware',
    'DeviceTrustMiddleware',
    'RateLimitMiddleware',
    # Services
    'ZeroTrustService',
    'DeviceTrustService',
    'ContinuousAuthService',
    'ThreatIntelligenceService',
]
