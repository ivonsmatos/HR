"""Security middleware for audit logging."""
import logging
from django.utils.deprecation import MiddlewareMixin
from apps.core.models import AuditoriaLog

logger = logging.getLogger(__name__)


class AuditoriaLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log security and audit events.
    Records HTTP requests, particularly focusing on sensitive operations.
    """

    # Methods that should be logged
    AUDIT_METHODS = ["POST", "PUT", "PATCH", "DELETE"]
    
    # Exclude these paths from logging
    EXCLUDE_PATHS = [
        "/static/",
        "/media/",
        "/admin/",
        "/api/schema/",
    ]

    def process_request(self, request):
        """Store request details for later processing."""
        request._start_time = request.META.get("SERVER_TIME", None)
        request._audit_user = request.user if request.user.is_authenticated else None
        return None

    def process_response(self, request, response):
        """Log the response and create audit entries if needed."""
        # Skip logging for excluded paths
        if any(request.path.startswith(path) for path in self.EXCLUDE_PATHS):
            return response

        # Log audit events for sensitive operations
        if request.method in self.AUDIT_METHODS and request.user.is_authenticated:
            try:
                self._log_audit_event(request, response)
            except Exception as e:
                logger.error(f"Erro logging audit event: {str(e)}")

        return response

    def _log_audit_event(self, request, response):
        """Create an audit log entry for the request."""
        user = request.user
        ip_address = self._get_client_ip(request)
        user_agent = request.META.get("HTTP_USER_AGENT", "")

        # Determine action type from method
        action_map = {
            "POST": "create",
            "PUT": "update",
            "PATCH": "update",
            "DELETE": "delete",
        }
        action = action_map.get(request.method, "unknown")

        # Extract module from URL path
        path_parts = request.path.strip("/").split("/")
        module = path_parts[2] if len(path_parts) > 2 else "unknown"

        # Only log if user has a company (tenant)
        if hasattr(user, "company") and user.company:
            AuditoriaLog.objects.create(
                company=user.company,
                user=user,
                action=action,
                module=module,
                object_type=path_parts[3] if len(path_parts) > 3 else "unknown",
                object_id=path_parts[4] if len(path_parts) > 4 else "",
                ip_address=ip_address,
                user_agent=user_agent,
                status_code=response.status_code,
            )

    @staticmethod
    def _get_client_ip(request):
        """Extract client IP from request."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
