"""
Helix Configuration - Integração de Fase E+ em settings.py

Adicionar ao config/settings.py
"""

# ===== FASE E+ Configuration =====

# GPU Support
HELIX_GPU_SUPPORT = {
    'enabled': True,
    'auto_detect': True,
    'preferred_type': 'cuda',  # cuda, rocm, cpu
    'fallback_to_cpu': True,
}

# Model Quantization
HELIX_QUANTIZATION = {
    'enabled': True,
    'level': 'q4',  # q2, q3, q4, q5, q8, fp16
    'auto_select': True,  # Auto select based on available memory
}

# Multi-Language Support
HELIX_LANGUAGES = {
    'enabled': True,
    'auto_detect': True,
    'default': 'pt-BR',
    'supported': [
        'pt-BR',  # Portuguese (Brazil)
        'en',     # English
        'es',     # Spanish
        'fr',     # French
        'de',     # German
        'it',     # Italian
        'zh',     # Chinese
        'ja',     # Japanese
    ]
}

# API Configuration
HELIX_API = {
    'rest_enabled': True,
    'graphql_enabled': True,
    'rate_limit': 100,  # Requests per hour
    'pagination_size': 20,
}

# Admin Dashboard
HELIX_ADMIN = {
    'enabled': True,
    'custom_dashboard': True,
    'show_system_status': True,
    'show_gpu_info': True,
    'analytics_window_days': 7,
}

# ===== Register in INSTALLED_APPS =====

# Ensure these are in INSTALLED_APPS:
INSTALLED_APPS += [
    'graphene_django',  # For GraphQL
]

# ===== Add to MIDDLEWARE =====

# If using GraphQL middleware:
MIDDLEWARE += [
    # Optional: Add GraphQL middleware if needed
]

# ===== Templates Configuration =====

# Ensure context processors are registered:
TEMPLATES[0]['OPTIONS']['context_processors'] += [
    'apps.assistant.context_processors.helix_context',
]

# ===== GraphQL Configuration =====

GRAPHENE = {
    'SCHEMA': 'apps.assistant.api.schema',
    'MIDDLEWARE': [
        'graphene_django.debug.DjangoDebugMiddleware',
    ]
}

# ===== API URLs Registration =====

# In config/urls.py, add:
"""
from django.urls import path, include

urlpatterns = [
    # ... other urls ...
    path('api/helix/', include('apps.assistant.api_urls')),  # REST API
    path('graphql/', GraphQLView.as_view(schema=schema), name='graphql'),  # GraphQL
]
"""

# ===== Environment Variables (for .env) =====

"""
# GPU Configuration
HELIX_GPU_ENABLED=true
HELIX_GPU_TYPE=cuda
CUDA_VISIBLE_DEVICES=0
OLLAMA_NUM_GPU=1

# Model Quantization
HELIX_QUANTIZATION_LEVEL=q4

# Language
HELIX_DEFAULT_LANGUAGE=pt-BR
HELIX_AUTO_DETECT_LANGUAGE=true

# API
HELIX_API_RATE_LIMIT=100

# Admin
HELIX_ADMIN_DASHBOARD=true
"""
