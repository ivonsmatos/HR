"""
PERFORMANCE BASELINE MEASUREMENT
Establishes performance metrics and baselines
"""

from typing import Dict, List, Any, Optional
import time
from datetime import datetime


class PerformanceBaseline:
    """Define and track performance baselines"""

    # Performance Targets (SLA)
    BASELINES: Dict[str, Dict[str, Any]] = {
        "API_Latency": {
            "description": "API response time",
            "metrics": {
                "p50": {"target": 50, "unit": "ms", "description": "50th percentile"},
                "p95": {"target": 200, "unit": "ms", "description": "95th percentile"},
                "p99": {"target": 500, "unit": "ms", "description": "99th percentile"},
            },
        },
        "Database_Queries": {
            "description": "Database query performance",
            "metrics": {
                "avg_query_time": {"target": 10, "unit": "ms"},
                "max_query_time": {"target": 100, "unit": "ms"},
                "slow_query_threshold": {"target": 1, "unit": "%", "description": "% of queries > 100ms"},
            },
        },
        "Cache_Performance": {
            "description": "Cache hit rate and performance",
            "metrics": {
                "hit_rate": {"target": 80, "unit": "%", "description": "% cache hits"},
                "cache_latency": {"target": 5, "unit": "ms"},
            },
        },
        "Page_Load": {
            "description": "Frontend page load performance",
            "metrics": {
                "html_load": {"target": 200, "unit": "ms"},
                "css_load": {"target": 100, "unit": "ms"},
                "js_load": {"target": 500, "unit": "ms"},
                "total_load": {"target": 2000, "unit": "ms"},
            },
        },
        "Endpoint_Specific": {
            "description": "Specific endpoint performance",
            "metrics": {
                "GET /health/": {"target": 10, "unit": "ms"},
                "GET /api/v1/users/": {"target": 100, "unit": "ms"},
                "POST /api/v1/users/": {"target": 200, "unit": "ms"},
                "GET /api/v1/users/{id}/": {"target": 50, "unit": "ms"},
            },
        },
        "Throughput": {
            "description": "System throughput capacity",
            "metrics": {
                "requests_per_second": {"target": 100, "unit": "req/s"},
                "concurrent_users": {"target": 100, "unit": "users"},
            },
        },
        "Error_Rate": {
            "description": "Error rate and reliability",
            "metrics": {
                "error_rate_target": {"target": 0.1, "unit": "%"},
                "availability_target": {"target": 99.9, "unit": "%"},
            },
        },
        "Resource_Usage": {
            "description": "Server resource utilization",
            "metrics": {
                "cpu_usage": {"target": 60, "unit": "%"},
                "memory_usage": {"target": 70, "unit": "%"},
                "disk_io": {"target": 50, "unit": "%"},
            },
        },
    }

    # Measurement Points
    MEASUREMENT_POINTS = [
        "health_check",
        "list_users",
        "create_user",
        "get_user",
        "update_user",
        "list_companies",
        "get_company",
    ]

    @classmethod
    def get_baseline_report(cls) -> Dict[str, Any]:
        """Generate baseline report"""
        return {
            "timestamp": datetime.now().isoformat(),
            "baselines": cls.BASELINES,
            "measurement_points": cls.MEASUREMENT_POINTS,
        }

    @classmethod
    def validate_response_time(cls, endpoint: str, response_time_ms: float) -> bool:
        """
        Validate if response time meets baseline
        
        Args:
            endpoint: API endpoint
            response_time_ms: Response time in milliseconds
        
        Returns:
            bool: True if meets baseline
        """
        metrics = cls.BASELINES.get("Endpoint_Specific", {}).get("metrics", {})
        
        if endpoint in metrics:
            target = metrics[endpoint]["target"]
            return response_time_ms <= target
        
        # Default P95 target if not specified
        default_target = cls.BASELINES["API_Latency"]["metrics"]["p95"]["target"]
        return response_time_ms <= default_target

    @classmethod
    def print_baselines(cls):
        """Print baseline report"""
        print("\n" + "="*80)
        print("PERFORMANCE BASELINE TARGETS - SyncRH")
        print("="*80)
        
        for category, details in cls.BASELINES.items():
            print(f"\n📊 {category}")
            print(f"   {details['description']}")
            print("   " + "-"*60)
            
            for metric, spec in details["metrics"].items():
                desc = spec.get("description", "")
                desc_str = f" ({desc})" if desc else ""
                print(f"   • {metric}: {spec['target']} {spec['unit']}{desc_str}")


# ============================================================================
# PERFORMANCE MEASUREMENT UTILITIES
# ============================================================================


class PerformanceMeasurement:
    """Measure and record performance metrics"""

    def __init__(self, name: str):
        """Initialize measurement"""
        self.name = name
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.duration_ms: float = 0

    def __enter__(self):
        """Start measurement"""
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End measurement"""
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000

    def get_report(self) -> Dict[str, Any]:
        """Get measurement report"""
        baseline = PerformanceBaseline.BASELINES.get("API_Latency", {}).get("metrics", {})
        p95_target = baseline.get("p95", {}).get("target", 200)
        
        is_within_baseline = self.duration_ms <= p95_target
        status = "✅ OK" if is_within_baseline else "⚠️ SLOW"
        
        return {
            "name": self.name,
            "duration_ms": round(self.duration_ms, 2),
            "status": status,
            "target_ms": p95_target,
            "exceeds_target": self.duration_ms > p95_target,
        }


# ============================================================================
# LOAD TESTING SETUP
# ============================================================================

LOAD_TEST_CONFIGURATION = """
LOAD TESTING WITH LOCUST
========================

Install Locust:
    pip install locust

Create locustfile.py:

    from locust import HttpUser, task, between
    
    class SyncRHUser(HttpUser):
        wait_time = between(1, 3)
        
        @task
        def health_check(self):
            self.client.get("/health/")
        
        @task(2)
        def list_users(self):
            self.client.get("/api/v1/users/")
        
        @task
        def get_company(self):
            self.client.get("/api/v1/companies/1/")

Run load test:
    locust -f locustfile.py --host=http://localhost:8000

Configuration:
    - Number of users: 100
    - Spawn rate: 10 users/second
    - Duration: 5 minutes
    - Ramp-up: 2 minutes

Monitor:
    - Response time (P50, P95, P99)
    - Throughput (requests/second)
    - Error rate
    - CPU/Memory usage
    - Database connections

Expected Results (Production Target):
    ✅ P95 latency < 200ms
    ✅ Throughput > 100 req/s
    ✅ Error rate < 0.1%
    ✅ CPU usage < 70%
    ✅ Memory usage < 80%
"""

# ============================================================================
# MONITORING & ALERTING
# ============================================================================

MONITORING_ALERTS = {
    "api_latency_p95": {
        "threshold": 200,
        "unit": "ms",
        "condition": "greater_than",
        "message": "API latency exceeded 200ms (P95)",
        "action": "trigger_alert",
    },
    "error_rate": {
        "threshold": 1,
        "unit": "%",
        "condition": "greater_than",
        "message": "Error rate exceeded 1%",
        "action": "trigger_alert",
    },
    "database_slow_queries": {
        "threshold": 5,
        "unit": "%",
        "condition": "greater_than",
        "message": "More than 5% of queries exceed 100ms",
        "action": "trigger_alert",
    },
    "memory_usage": {
        "threshold": 85,
        "unit": "%",
        "condition": "greater_than",
        "message": "Memory usage exceeded 85%",
        "action": "trigger_alert",
    },
    "cpu_usage": {
        "threshold": 80,
        "unit": "%",
        "condition": "greater_than",
        "message": "CPU usage exceeded 80%",
        "action": "trigger_alert",
    },
    "disk_usage": {
        "threshold": 85,
        "unit": "%",
        "condition": "greater_than",
        "message": "Disk usage exceeded 85%",
        "action": "trigger_alert",
    },
}


if __name__ == "__main__":
    PerformanceBaseline.print_baselines()
    print("\n" + LOAD_TEST_CONFIGURATION)
