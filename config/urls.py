"""
URL Configuration for SyncRH project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from . import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app import views
    2. Add a URL to urlpatterns:  path('', views.Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from apps.core.health_check import health_check, readiness_check, liveness_check

urlpatterns = [
    # Health Check Endpoints (for load balancers & Kubernetes)
    path("health/", health_check, name="health_check"),
    path("health/ready/", readiness_check, name="readiness_check"),
    path("health/live/", liveness_check, name="liveness_check"),
    
    # Admin
    path("admin/", admin.site.urls),
    
    # Assistant (main app)
    path("", include("apps.assistant.urls")),
    
    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    
    # API v1 - Módulos Originais
    path("api/v1/core/", include("apps.core.urls")),
    path("api/v1/hrm/", include("apps.hrm.urls")),
    path("api/v1/work/", include("apps.work.urls")),
    path("api/v1/finance/", include("apps.finance.urls")),
    path("api/v1/crm/", include("apps.crm.urls")),
    path("api/v1/recruitment/", include("apps.recruitment.urls")),
    path("api/v1/security/", include("apps.security.urls")),
    path("api/v1/saas/", include("apps.saas_admin.urls")),
    path("api/v1/utilities/", include("apps.utilities.urls")),
    
    # API v1 - Módulos SyncRH HR
    path("api/v1/dp/", include("apps.departamento_pessoal.urls")),
    path("api/v1/recrutamento/", include("apps.recrutamento_selecao.urls")),
    path("api/v1/performance/", include("apps.desenvolvimento_performance.urls")),
    path("api/v1/engajamento/", include("apps.engajamento_retencao.urls")),
    path("api/v1/comportamental/", include("apps.gestao_comportamental.urls")),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

from django.urls import path
from django.http import HttpResponse

def trigger_error(request):
    division_by_zero = 1 / 0

urlpatterns += [
    path('sentry-debug/', trigger_error),
]
