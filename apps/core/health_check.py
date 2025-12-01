"""
Health Check Endpoints

GET /health/ - Simple health check
GET /health/ready/ - Readiness probe
GET /health/live/ - Liveness probe
"""

from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
import redis
import logging

logger = logging.getLogger(__name__)


def health_check(request):
    """Simple health check - used by load balancers"""
    return JsonResponse({'status': 'ok'}, status=200)


def readiness_check(request):
    """Readiness probe - check if app is ready to accept traffic"""
    checks = {
        'database': False,
        'cache': False,
        'app': True,
    }
    
    # Check database
    try:
        connection.ensure_connection()
        checks['database'] = True
    except Exception as e:
        logger.error(f"Database check failed: {e}")
    
    # Check cache
    try:
        cache.set('health_check', 'ok', 10)
        if cache.get('health_check') == 'ok':
            checks['cache'] = True
    except Exception as e:
        logger.error(f"Cache check failed: {e}")
    
    all_ok = all(checks.values())
    status_code = 200 if all_ok else 503
    
    return JsonResponse({
        'status': 'ready' if all_ok else 'not_ready',
        'checks': checks,
    }, status=status_code)


def liveness_check(request):
    """Liveness probe - check if app is still running"""
    try:
        connection.ensure_connection()
        return JsonResponse({'status': 'alive'}, status=200)
    except Exception as e:
        logger.error(f"Liveness check failed: {e}")
        return JsonResponse({'status': 'dead'}, status=503)


# URLs: config/urls.py
from apps.core.views import health_check, readiness_check, liveness_check

urlpatterns = [
    # Health checks
    path('health/', health_check, name='health_check'),
    path('health/ready/', readiness_check, name='readiness_check'),
    path('health/live/', liveness_check, name='liveness_check'),
]
