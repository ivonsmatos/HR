"""
Performance Monitoring Setup - 2 horas

Implementar APM com DataDog/New Relic
Baselines de performance
Monitoring automático
"""

# apps/core/monitoring.py

import logging
import time
from functools import wraps
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.utils.decorators import method_decorator

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Monitor de performance da aplicação"""
    
    METRICS = {
        'api_latency': [],
        'db_queries': [],
        'cache_hits': 0,
        'cache_misses': 0,
    }
    
    @staticmethod
    def record_api_call(endpoint, duration_ms):
        """Registrar latência de API"""
        key = f"perf:api:{endpoint}"
        metrics = cache.get(key, [])
        metrics.append(duration_ms)
        if len(metrics) > 100:
            metrics = metrics[-100:]
        cache.set(key, metrics, 3600)
        
        # Log P95, P99
        if len(metrics) >= 10:
            sorted_metrics = sorted(metrics)
            p95 = sorted_metrics[int(len(sorted_metrics) * 0.95)]
            p99 = sorted_metrics[int(len(sorted_metrics) * 0.99)]
            logger.info(f"API {endpoint} - P95: {p95}ms, P99: {p99}ms")
    
    @staticmethod
    def get_db_query_count():
        """Obter número de queries por request"""
        return len(connection.queries)
    
    @staticmethod
    def get_slow_queries(threshold_ms=100):
        """Queries mais lentas"""
        slow_queries = []
        for query in connection.queries:
            if float(query['time']) > (threshold_ms / 1000):
                slow_queries.append({
                    'sql': query['sql'][:100],
                    'time': query['time'],
                })
        return slow_queries


def monitor_performance(endpoint_name=None):
    """Decorator para monitorar performance de views/funções"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            name = endpoint_name or func.__name__
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = (time.time() - start_time) * 1000  # ms
                PerformanceMonitor.record_api_call(name, duration)
                
                # Log se > 500ms
                if duration > 500:
                    logger.warning(
                        f"Slow {name}: {duration:.0f}ms | "
                        f"Queries: {PerformanceMonitor.get_db_query_count()}"
                    )
        return wrapper
    return decorator


class PerformanceMiddleware:
    """Middleware para monitorar performance de requests"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time.time()
        
        response = self.get_response(request)
        
        duration = (time.time() - start_time) * 1000  # ms
        
        # Adicionar header
        response['X-Response-Time'] = f"{duration:.0f}ms"
        
        # Log lento
        if duration > 500:
            queries = len(connection.queries) if settings.DEBUG else 0
            logger.warning(
                f"SLOW REQUEST: {request.method} {request.path} "
                f"- {duration:.0f}ms ({queries} queries)"
            )
        
        # Métricas
        endpoint = f"{request.method} {request.path[:50]}"
        PerformanceMonitor.record_api_call(endpoint, duration)
        
        return response


class PerformanceCheckMiddleware:
    """Verificar performance e alertar se > threshold"""
    
    THRESHOLD_MS = 500
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        duration = (time.time() - start_time) * 1000
        
        if duration > self.THRESHOLD_MS:
            logger.error(
                f"PERFORMANCE ALERT: {request.path} took {duration:.0f}ms "
                f"(threshold: {self.THRESHOLD_MS}ms)"
            )
        
        return response
