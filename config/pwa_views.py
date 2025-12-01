# PWA Views - Serve manifest.json and PWA configurations
"""
Progressive Web App Views
Handles manifest generation, offline page, and PWA metadata
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from django.conf import settings
from config.pwa import (
    PWA_APP_NAME,
    PWA_APP_DESCRIPTION,
    PWA_APP_THEME_COLOR,
    PWA_APP_BACKGROUND_COLOR,
    PWA_APP_DISPLAY,
    PWA_APP_SCOPE,
    PWA_APP_ORIENTATION,
    PWA_APP_START_URL,
    PWA_APP_STATUS_BAR_COLOR,
    PWA_APP_ICONS,
    PWA_APP_SCREENSHOTS,
    PWA_APP_SHORTCUTS,
    MANIFEST_CATEGORIES,
)
import os


@require_http_methods(["GET"])
@cache_page(60 * 60)  # Cache for 1 hour
def manifest(request):
    """
    Generate PWA Web App Manifest (manifest.json)
    Provides app metadata for installation on devices
    """
    manifest_data = {
        "name": PWA_APP_NAME,
        "short_name": PWA_APP_NAME.split()[0],  # First word
        "description": PWA_APP_DESCRIPTION,
        "start_url": PWA_APP_START_URL,
        "scope": PWA_APP_SCOPE,
        "display": PWA_APP_DISPLAY,
        "orientation": PWA_APP_ORIENTATION,
        "theme_color": PWA_APP_THEME_COLOR,
        "background_color": PWA_APP_BACKGROUND_COLOR,
        "icons": PWA_APP_ICONS,
        "categories": MANIFEST_CATEGORIES,
        "screenshots": PWA_APP_SCREENSHOTS,
        "shortcuts": PWA_APP_SHORTCUTS,
        "prefer_related_applications": False,
    }

    # Add share target if applicable
    if hasattr(settings, "PWA_SHARE_TARGET"):
        manifest_data["share_target"] = settings.PWA_SHARE_TARGET

    return JsonResponse(manifest_data)


@require_http_methods(["GET"])
def browserconfig(request):
    """
    Generate browserconfig.xml for Windows tile support
    """
    browserconfig = f"""<?xml version="1.0" encoding="utf-8"?>
<browserconfig>
  <msapplication>
    <tile>
      <square70x70logo src="/static/images/icons/mstile-70x70.png"/>
      <square150x150logo src="/static/images/icons/mstile-150x150.png"/>
      <square310x310logo src="/static/images/icons/mstile-310x310.png"/>
      <TileColor>{PWA_APP_THEME_COLOR}</TileColor>
    </tile>
  </msapplication>
</browserconfig>"""

    return JsonResponse(
        {"browserconfig": browserconfig},
        safe=False,
        content_type="application/xml",
    )


@require_http_methods(["GET"])
def service_worker(request):
    """
    Serve service worker with proper caching headers
    """
    from django.views.static import serve
    from django.conf import settings
    import os

    sw_path = os.path.join(settings.STATIC_ROOT, "js", "service-worker.js")
    if os.path.exists(sw_path):
        response = serve(request, "js/service-worker.js", settings.STATIC_ROOT)
        response["Cache-Control"] = "public, max-age=3600"
        return response

    return JsonResponse({"error": "Service worker not found"}, status=404)


@require_http_methods(["GET"])
def offline(request):
    """
    Offline fallback page
    Displayed when user tries to access a page while offline
    """
    return JsonResponse(
        {
            "status": "offline",
            "message": "You are currently offline. Some features may not be available.",
            "timestamp": str(__import__("django.utils.timezone", fromlist=["now"]).now()),
        }
    )


@require_http_methods(["GET"])
def pwa_metadata(request):
    """
    Return PWA metadata for frontend initialization
    """
    return JsonResponse(
        {
            "app_name": PWA_APP_NAME,
            "theme_color": PWA_APP_THEME_COLOR,
            "display": PWA_APP_DISPLAY,
            "start_url": PWA_APP_START_URL,
            "is_installable": True,
            "supports_offline": True,
        }
    )
