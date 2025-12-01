# 🚀 PWA - Progressive Web App Guide

## O que é PWA?

**Progressive Web App (PWA)** é uma aplicação web que usa capacidades modernas do navegador para oferecer uma experiência similar à de um aplicativo nativo:

- ✅ **Instalável** - Pode ser instalada na tela inicial (iOS/Android/Windows/macOS)
- ✅ **Offline-first** - Funciona sem conexão com internet
- ✅ **Responsiva** - Funciona em qualquer dispositivo
- ✅ **Fast** - Carregamento rápido com cache
- ✅ **Segura** - Usa HTTPS e isolamento de origem
- ✅ **Notificações** - Push notifications em tempo real

---

## 📁 Estrutura PWA do Worksuite Clone

### Arquivos Criados

```
HR/
├── config/
│   ├── pwa.py                          # Configuração PWA
│   └── pwa_views.py                    # Views PWA (manifest, browserconfig)
│
├── static/
│   ├── js/
│   │   ├── service-worker.js           # Service Worker (caching, offline)
│   │   └── pwa.js                      # Client PWA (registro, sincronização)
│   └── images/
│       ├── icons/                      # Icons em vários tamanhos
│       │   ├── icon-72x72.png
│       │   ├── icon-96x96.png
│       │   ├── icon-128x128.png
│       │   ├── icon-144x144.png
│       │   ├── icon-152x152.png
│       │   ├── icon-192x192.png
│       │   ├── icon-384x384.png
│       │   ├── icon-512x512.png
│       │   ├── icon-maskable-192x192.png
│       │   ├── icon-maskable-512x512.png
│       │   └── mstile-*.png            # Windows tiles
│       └── screenshots/                # Screenshots para app store
│           ├── screenshot-540x720.png
│           └── screenshot-1280x720.png
│
├── templates/
│   └── base.html                       # Template com PWA meta tags
│
└── docs/
    └── PWA.md                          # Este arquivo
```

---

## ⚙️ Configuração

### 1. settings.py

Adicione ao `config/settings.py`:

```python
# Import PWA config
from config.pwa import *

# PWA Settings
PWA_DEV_MODE = False
PWA_CACHE_VERSION = "v1"

# WhiteNoise for static files (PWA requirement)
MIDDLEWARE = [
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Add this first
    # ... rest of middleware
]

# Compression for better performance
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# HTTPS required for PWA
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    "default-src": ("'self'",),
    "script-src": (
        "'self'",
        "'unsafe-inline'",
        "cdn.jsdelivr.net",
    ),
    "img-src": ("'self'", "data:", "https:"),
}
```

### 2. urls.py

Adicione as rotas PWA:

```python
from config import pwa_views
from django.urls import path

urlpatterns = [
    # PWA
    path("api/pwa/manifest/", pwa_views.manifest, name="pwa-manifest"),
    path("api/pwa/browserconfig/", pwa_views.browserconfig, name="pwa-browserconfig"),
    path("api/pwa/metadata/", pwa_views.pwa_metadata, name="pwa-metadata"),
    path("api/pwa/offline/", pwa_views.offline, name="pwa-offline"),
    path("static/js/service-worker.js", pwa_views.service_worker, name="service-worker"),

    # ... rest of URLs
]
```

### 3. base.html

Já incluído em `templates/base.html`:

```html
<!-- PWA Manifest -->
<link rel="manifest" href="/api/pwa/manifest/" />

<!-- App Icons -->
<link rel="apple-touch-icon" href="/static/images/icons/icon-192x192.png" />

<!-- Script PWA -->
<script src="/static/js/pwa.js" defer></script>
```

---

## 🎯 Funcionalidades PWA Implementadas

### 1. Service Worker (service-worker.js)

**Caching Strategies:**

```javascript
// Network First - para HTML
networkFirstStrategy(request);
// Tenta rede primeiro, fallback para cache

// Cache First - para assets estáticos
cacheFirstStrategy(request);
// Usa cache, atualiza em background

// Stale While Revalidate
// Retorna cache, atualiza em background
```

**Eventos:**

- ✅ `install` - Cache de assets essenciais
- ✅ `activate` - Limpeza de caches antigos
- ✅ `fetch` - Interceptação de requisições
- ✅ `sync` - Background sync de offline queue

### 2. Cliente PWA (pwa.js)

**Funcionalidades:**

```javascript
class WorksuitePWA {
  // Service Worker registration
  registerServiceWorker()

  // Online/Offline detection
  handleOnline()
  handleOffline()

  // Install prompt
  showInstallPrompt()
  installApp()

  // Offline queue
  queueRequest(method, url, data)
  syncOfflineQueue()

  // Notifications
  requestNotificationPermission()
  sendNotification(title, options)

  // App state
  isAppInstalled()
  getDisplayMode()
}
```

### 3. Web App Manifest

**Informações da app:**

```json
{
  "name": "Worksuite Clone",
  "short_name": "Worksuite",
  "description": "Enterprise ERP System - Multi-tenant SaaS",
  "start_url": "/",
  "scope": "/",
  "display": "standalone",
  "theme_color": "#3B82F6",
  "background_color": "#FFFFFF",
  "icons": [
    {
      "src": "/static/images/icons/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/static/images/icons/icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any"
    }
  ],
  "screenshots": [...],
  "shortcuts": [...]
}
```

---

## 🚀 Como Usar

### 1. Preparar Icons

**Gerar icons em vários tamanhos:**

```bash
# Usando ImageMagick
convert icon-512x512.png -resize 192x192 icon-192x192.png
convert icon-512x512.png -resize 384x384 icon-384x384.png

# Ou usando Python/Pillow
from PIL import Image
img = Image.open("icon-512x512.png")
img.thumbnail((192, 192))
img.save("icon-192x192.png")
```

**Criar maskable icons (para modernos):**

```bash
# Maskable icons para Android Adaptive Icons
# Usar ferramenta: https://www.pwabuilder.com/
```

### 2. Configurar Screenshots

Para Google Play Store e app stores:

```bash
# 540x720 - narrow form factor (mobile)
# 1280x720 - wide form factor (tablet)
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar HTTPS

PWA requer HTTPS:

```bash
# Development (com mkcert):
mkcert -install
mkcert localhost 127.0.0.1

# Production:
# Use Let's Encrypt com Certbot
```

### 5. Executar

```bash
python manage.py collectstatic --noinput
python manage.py runserver
```

Acesse: `https://localhost:8000`

---

## 📱 Instalação

### Desktop

1. Acesse a aplicação no navegador
2. Clique no botão "Instalar" (geralmente top-right)
3. Selecione "Sim" no prompt
4. App será adicionado ao seu desktop/aplicações

### Mobile (Android)

1. Abra em Chrome/Edge
2. Menu → "Instalar aplicativo" ou "Adicionar à tela inicial"
3. Confirme
4. App funcionará como nativo

### Mobile (iOS)

1. Abra em Safari
2. Menu compartilhar → "Adicionar à tela inicial"
3. Nomeie o app
4. Confirme

---

## 🌐 Funcionalidades Offline

### Quando Offline:

1. ✅ Visualizar dados em cache
2. ✅ Navegar entre páginas em cache
3. ✅ Editar dados (fila para sincronização)
4. ✅ Ver indicador "Offline"

### Quando Online:

1. ✅ Sincronizar alterações automaticamente
2. ✅ Atualizar cache com dados novos
3. ✅ Mostrar notificação de atualização

### Offline Queue:

```javascript
// Dados armazenados em localStorage + IndexedDB
{
  method: "POST",
  url: "/api/v1/hrm/employees/",
  data: { name: "John Doe", ... },
  timestamp: "2025-12-01T10:30:00Z"
}

// Sincronizado quando online
```

---

## 🔔 Push Notifications

### Setup

```python
# settings.py
PUSH_NOTIFICATIONS_ENABLED = True

# No frontend, requestar permissão:
await workSuitePWA.requestNotificationPermission()

# Enviar notificação:
workSuitePWA.sendNotification("Nova mensagem", {
  body: "Você tem uma nova mensagem",
  icon: "/static/images/icons/icon-192x192.png",
  badge: "/static/images/icons/badge-72x72.png",
  tag: "message-123",
  requireInteraction: true
})
```

### Evento de clique:

```javascript
// No service worker
self.addEventListener("notificationclick", (event) => {
  event.notification.close();

  event.waitUntil(
    clients.matchAll({ type: "window" }).then((clientList) => {
      // Abrir ou focar janela existente
      if (clientList.length > 0) {
        return clientList[0].focus();
      }
      return clients.openWindow("/dashboard/");
    })
  );
});
```

---

## 🧪 Testing PWA

### Chrome DevTools

1. `F12` → Application tab
2. Manifest - Verificar se válido
3. Service Workers - Ver status
4. Storage - Ver cache e IndexedDB
5. Network - Simular offline

### Lighthouse

```bash
# No Chrome DevTools → Lighthouse
# Run audit → PWA section
```

### PWA Builder

Online tool: https://www.pwabuilder.com/

---

## 🎨 Customização

### Alterar Cores

Em `config/pwa.py`:

```python
PWA_APP_THEME_COLOR = "#FF6B6B"  # Vermelho
PWA_APP_BACKGROUND_COLOR = "#F8F9FA"  # Cinza claro
```

### Adicionar Shortcuts

Em `config/pwa.py`:

```python
PWA_APP_SHORTCUTS = [
    {
        "name": "Nova Tarefa",
        "short_name": "Tarefa",
        "url": "/work/tasks/create/",
        "icons": [...]
    }
]
```

### Categorias de App

Em `config/pwa.py`:

```python
MANIFEST_CATEGORIES = [
    "productivity",
    "business",
    "utilities"
]
```

---

## 🔒 Segurança

### HTTPS (Obrigatório)

```python
# production
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### CSP (Content Security Policy)

```python
SECURE_CONTENT_SECURITY_POLICY = {
    "default-src": ("'self'",),
    "script-src": ("'self'", "'unsafe-inline'"),
    "img-src": ("'self'", "data:", "https:"),
}
```

### Service Worker Verificação

```javascript
// Verificar se SW está ativo
if ("serviceWorker" in navigator) {
  navigator.serviceWorker.ready.then((registration) => {
    console.log("SW ativo:", registration.active);
  });
}
```

---

## 📊 Performance

### Métrica: Lighthouse PWA Score

Target: **90+**

```
✅ Installable
✅ Works offline
✅ Starts fast
✅ Installs promptly
✅ Safe & secure
```

### Otimizações

1. **Caching Strategy**

   - Network first para HTML
   - Cache first para assets
   - Stale while revalidate para APIs

2. **Static Files**

   - CompressedManifestStaticFilesStorage
   - WhiteNoise middleware
   - GZIP compression

3. **Database Queries**
   - Select_related para FK
   - Prefetch_related para M2M
   - Pagination

---

## 🐛 Troubleshooting

### Service Worker não registra

```javascript
// Verificar console
navigator.serviceWorker
  .register("/static/js/service-worker.js")
  .then((reg) => console.log("Registered:", reg))
  .catch((err) => console.error("Error:", err));
```

### Manifest inválido

- Verificar em DevTools → Application → Manifest
- Validar JSON: https://www.w3schools.com/json/json_validator.asp

### Cache muito grande

```python
# Limitar tamanho
OFFLINE_STORAGE_SIZE = 50 * 1024 * 1024  # 50MB

# No SW: limpar caches antigos
```

### Notificações não funcionam

- Verificar permissão em Settings
- Requer HTTPS
- Verificar `Notification.permission`

---

## 📚 Referências

- [Web App Manifest - MDN](https://developer.mozilla.org/en-US/docs/Web/Manifest)
- [Service Workers - MDN](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [PWA Checklist - web.dev](https://web.dev/pwa-checklist/)
- [PWA Builder](https://www.pwabuilder.com/)

---

## ✅ Checklist PWA

- [ ] HTTPS ativado
- [ ] Service Worker registrado
- [ ] Manifest.json válido
- [ ] Icons em múltiplos tamanhos
- [ ] Screenshots adicionados
- [ ] Offline page criada
- [ ] Caching strategy definida
- [ ] Push notifications testadas
- [ ] Lighthouse PWA score 90+
- [ ] Funciona em mobile
- [ ] Funciona offline
- [ ] App instalável

---

## 🚀 Próximos Passos

1. **Phase 2**: Implementar APIs (Serializers & ViewSets)
2. **Phase 3**: Melhorar frontend com React/Vue
3. **Phase 4**: Adicionar WebSockets em tempo real
4. **Phase 5**: Publicar em app stores (Google Play, App Store)

---

**PWA Configuration Complete!** ✅

Seu Worksuite Clone agora é um Progressive Web App completo e pronto para usar em qualquer dispositivo.
