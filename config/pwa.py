# PWA Configuration for Worksuite Clone
"""
Progressive Web App (PWA) Configuration
Enables offline support, installability, and app-like experience
"""

# PWA Settings
PWA_APP_NAME = "Worksuite Clone"
PWA_APP_DESCRIPTION = "Enterprise ERP System - Multi-tenant SaaS"
PWA_APP_THEME_COLOR = "#3B82F6"
PWA_APP_BACKGROUND_COLOR = "#FFFFFF"
PWA_APP_DISPLAY = "standalone"
PWA_APP_SCOPE = "/"
PWA_APP_ORIENTATION = "portrait-primary"
PWA_APP_START_URL = "/"
PWA_APP_STATUS_BAR_COLOR = "black"
PWA_APP_DIR = "ltr"
PWA_APP_LANG = "pt-BR"

# Icons for PWA
PWA_APP_ICONS = [
    {
        "src": "/static/images/icons/icon-72x72.png",
        "sizes": "72x72",
        "type": "image/png",
        "purpose": "any",
    },
    {
        "src": "/static/images/icons/icon-96x96.png",
        "sizes": "96x96",
        "type": "image/png",
        "purpose": "any",
    },
    {
        "src": "/static/images/icons/icon-128x128.png",
        "sizes": "128x128",
        "type": "image/png",
        "purpose": "any",
    },
    {
        "src": "/static/images/icons/icon-144x144.png",
        "sizes": "144x144",
        "type": "image/png",
        "purpose": "any",
    },
    {
        "src": "/static/images/icons/icon-152x152.png",
        "sizes": "152x152",
        "type": "image/png",
        "purpose": "any",
    },
    {
        "src": "/static/images/icons/icon-192x192.png",
        "sizes": "192x192",
        "type": "image/png",
        "purpose": "any",
    },
    {
        "src": "/static/images/icons/icon-384x384.png",
        "sizes": "384x384",
        "type": "image/png",
        "purpose": "any",
    },
    {
        "src": "/static/images/icons/icon-512x512.png",
        "sizes": "512x512",
        "type": "image/png",
        "purpose": "any",
    },
    {
        "src": "/static/images/icons/icon-maskable-192x192.png",
        "sizes": "192x192",
        "type": "image/png",
        "purpose": "maskable",
    },
    {
        "src": "/static/images/icons/icon-maskable-512x512.png",
        "sizes": "512x512",
        "type": "image/png",
        "purpose": "maskable",
    },
]

# Screenshot for app store
PWA_APP_SCREENSHOTS = [
    {
        "src": "/static/images/screenshots/screenshot-540x720.png",
        "sizes": "540x720",
        "type": "image/png",
        "form_factor": "narrow",
    },
    {
        "src": "/static/images/screenshots/screenshot-1280x720.png",
        "sizes": "1280x720",
        "type": "image/png",
        "form_factor": "wide",
    },
]

# Shortcuts for PWA (quick access)
PWA_APP_SHORTCUTS = [
    {
        "name": "Dashboard",
        "short_name": "Dashboard",
        "description": "Abrir Dashboard",
        "url": "/dashboard/",
        "icons": [
            {
                "src": "/static/images/icons/shortcut-dashboard-96x96.png",
                "sizes": "96x96",
                "type": "image/png",
            }
        ],
    },
    {
        "name": "Employees",
        "short_name": "Employees",
        "description": "Gerenciar Funcionários",
        "url": "/hrm/employees/",
        "icons": [
            {
                "src": "/static/images/icons/shortcut-employees-96x96.png",
                "sizes": "96x96",
                "type": "image/png",
            }
        ],
    },
    {
        "name": "Projects",
        "short_name": "Projects",
        "description": "Gerenciar Projetos",
        "url": "/work/projects/",
        "icons": [
            {
                "src": "/static/images/icons/shortcut-projects-96x96.png",
                "sizes": "96x96",
                "type": "image/png",
            }
        ],
    },
    {
        "name": "Invoices",
        "short_name": "Invoices",
        "description": "Gerenciar Faturas",
        "url": "/finance/invoices/",
        "icons": [
            {
                "src": "/static/images/icons/shortcut-invoices-96x96.png",
                "sizes": "96x96",
                "type": "image/png",
            }
        ],
    },
]

# Service Worker Configuration
SERVICE_WORKER_PATH = "/static/js/service-worker.js"
SERVICE_WORKER_VERSION = "1.0.0"

# Offline Support
OFFLINE_SUPPORT = True
OFFLINE_QUEUE_TIMEOUT = 3600  # 1 hour in seconds
OFFLINE_STORAGE_SIZE = 50 * 1024 * 1024  # 50 MB

# Push Notifications
PUSH_NOTIFICATIONS_ENABLED = True
PUSH_NOTIFICATION_VAPID_PUBLIC_KEY = None  # Set via environment
PUSH_NOTIFICATION_VAPID_PRIVATE_KEY = None  # Set via environment

# Web App Manifest
MANIFEST_VERSION = "1.0"
MANIFEST_CATEGORIES = ["productivity", "business"]

# PWA Development
PWA_DEV_MODE = False  # Set to True for development
PWA_CACHE_VERSION = "v1"
