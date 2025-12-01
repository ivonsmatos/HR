# 🔧 TROUBLESHOOTING GUIDE - Worksuite PWA

## Índice Rápido

1. [Erros de Inicialização](#erros-de-inicialização)
2. [Problemas de Database](#problemas-de-database)
3. [Problemas de Autenticação](#problemas-de-autenticação)
4. [Problemas de Performance](#problemas-de-performance)
5. [Problemas de PWA](#problemas-de-pwa)
6. [Problemas de Multi-Tenancy](#problemas-de-multi-tenancy)
7. [Problemas de Integração](#problemas-de-integração)

---

## Erros de Inicialização

### ❌ "ModuleNotFoundError: No module named 'django'"

**Causa**: Dependências não instaladas

**Solução**:

```bash
# Ativar virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt
```

---

### ❌ "RuntimeError: Sitepackages directory not found"

**Causa**: Virtual environment corrompido

**Solução**:

```bash
# Remover venv
rm -rf venv

# Recriar
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### ❌ "SECRET_KEY não configurada"

**Causa**: .env não existe ou SECRET_KEY não definido

**Solução**:

```bash
# Copiar exemplo
cp .env.example .env

# Editar .env
nano .env

# Gerar SECRET_KEY segura
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Adicionar ao .env
```

---

### ❌ "DEBUG=True não permitido em produção"

**Causa**: DEBUG definido como True

**Solução**:

```bash
# Editar .env
nano .env

# Mudar para
DEBUG=False

# Reiniciar aplicação
docker-compose restart web
```

---

## Problemas de Database

### ❌ "could not connect to server: Connection refused"

**Causa**: PostgreSQL não está rodando

**Solução**:

```bash
# Verificar se está rodando
docker-compose ps

# Se não estiver:
docker-compose up -d db

# Esperar 10 segundos e tentar novamente
sleep 10
docker-compose logs db

# Se ainda não funcionar, remover e recriar
docker-compose down
docker-compose up -d db
```

---

### ❌ "FATAL: role 'postgres' does not exist"

**Causa**: PostgreSQL não inicializou corretamente

**Solução**:

```bash
# Remover volume
docker volume rm hr_postgres_data

# Recriar
docker-compose up -d db

# Verificar logs
docker-compose logs db
```

---

### ❌ "relation 'core_user' does not exist"

**Causa**: Migrations não foram aplicadas

**Solução**:

```bash
# Aplicar migrations
docker-compose exec web python manage.py migrate

# Se erro persistir:
# 1. Remover banco
docker-compose down -v

# 2. Recriar
docker-compose up -d

# 3. Aplicar migrations novamente
docker-compose exec web python manage.py migrate
```

---

### ❌ "Duplicate key value violates unique constraint"

**Causa**: Dados duplicados no banco

**Solução**:

```bash
# SSH no container
docker-compose exec web bash

# Conectar ao banco
python manage.py dbshell

# Ver chaves duplicadas
SELECT * FROM core_user WHERE email LIKE '%duplicado%';

# Deletar duplicatas
DELETE FROM core_user WHERE id IN (SELECT id FROM core_user WHERE email = 'duplicado@example.com' ORDER BY id DESC LIMIT 1);

# Exit
\q
exit
```

---

## Problemas de Autenticação

### ❌ "Invalid token" em API requests

**Causa**: Token JWT expirado ou inválido

**Solução**:

```bash
# 1. Fazer login novamente para obter novo token
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'

# 2. Usar novo token em headers
curl -H "Authorization: Bearer TOKEN_AQUI" http://localhost:8000/api/v1/users/

# 3. Verificar JWT_EXPIRATION_HOURS em .env
```

---

### ❌ "403 Forbidden - CSRF token missing or incorrect"

**Causa**: CSRF protection ativado

**Solução**:

```python
# Para requisições AJAX, adicionar token:
fetch('/api/endpoint/', {
  method: 'POST',
  headers: {
    'X-CSRFToken': getCookie('csrftoken'),
  },
  body: JSON.stringify(data)
})

# Para API REST, usar JWT em vez de session auth
```

---

### ❌ "Authentication credentials were not provided"

**Causa**: Header Authorization ausente

**Solução**:

```bash
# Adicionar header correto
curl -H "Authorization: Bearer seu-token-aqui" \
  http://localhost:8000/api/v1/protected-endpoint/

# Verificar formato: "Bearer TOKEN" (não "Token TOKEN")
```

---

## Problemas de Performance

### ❌ "Slow API responses (> 500ms)"

**Causa**: Queries não otimizadas

**Solução**:

```python
# 1. Verificar queries com django-debug-toolbar
# Em settings.py
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

# 2. Usar select_related e prefetch_related
User.objects.select_related('company').prefetch_related('roles')

# 3. Adicionar índices ao banco
# Em migration:
python manage.py makemigrations
# Editar migration para adicionar:
field.db_index = True

# 4. Cache resultados
from django.core.cache import cache
users = cache.get('users_list')
if users is None:
    users = User.objects.all()
    cache.set('users_list', users, 3600)  # 1 hora
```

---

### ❌ "Memory usage creeping up"

**Causa**: Memory leak em background tasks

**Solução**:

```bash
# 1. Monitor Celery workers
docker-compose exec celery celery -A config inspect active

# 2. Ver memory por worker
docker-compose exec celery celery -A config inspect reserved

# 3. Restart worker
docker-compose restart celery

# 4. Limpar tasks expiradas
docker-compose exec celery celery -A config purge
```

---

### ❌ "Redis connection timeout"

**Causa**: Redis sobrecarregado ou não respondendo

**Solução**:

```bash
# 1. Verificar status
docker-compose exec redis redis-cli ping

# 2. Ver memória
docker-compose exec redis redis-cli info memory

# 3. Limpar cache
docker-compose exec redis redis-cli FLUSHDB

# 4. Aumentar limite de conexões
# Em docker-compose.yml adicionar:
# command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru

# 5. Reiniciar
docker-compose restart redis
```

---

## Problemas de PWA

### ❌ "Service Worker não está sendo registrado"

**Causa**: Service Worker file não encontrado ou erro de execução

**Solução**:

```bash
# 1. Verificar se arquivo existe
ls -la static/js/service-worker.js

# 2. Verificar erros no navegador
# F12 > Console > Ver erros de SW

# 3. Limpar cache do navegador
# Hard reload: Ctrl+Shift+R (Windows) ou Cmd+Shift+R (Mac)

# 4. Verificar MIME type em server
# django-debug-toolbar > Static files

# 5. Recolher static files
python manage.py collectstatic --noinput
```

---

### ❌ "Offline mode não funciona"

**Causa**: Cache strategy não configurada

**Solução**:

```javascript
// Em service-worker.js, adicionar:
const CACHE_NAME = "worksuite-v1";

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(["/", "/static/css/style.css", "/static/js/app.js"]);
    })
  );
});

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;

  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});
```

---

### ❌ "PWA não instala em iOS"

**Causa**: Configuração incompleta para iOS

**Solução**:

```html
<!-- Em templates/base.html, adicionar: -->
<meta name="apple-mobile-web-app-capable" content="yes" />
<meta name="apple-mobile-web-app-status-bar-style" content="black" />
<meta name="apple-mobile-web-app-title" content="Worksuite" />
<link rel="apple-touch-icon" href="/static/img/icon-192x192.png" />
```

---

## Problemas de Multi-Tenancy

### ❌ "Data vazando entre tenants"

**Causa**: Tenant context não está sendo preservado

**Solução**:

```python
# 1. Verificar middleware
# Em settings.py:
MIDDLEWARE = [
    'django_tenants.middleware.main.TenantMainMiddleware',  # DEVE estar primeiro
    ...
]

# 2. Adicionar schema_name no contexto
from django_tenants.utils import get_tenant_model
tenant = connection.tenant
print(f"Tenant atual: {tenant.schema_name}")

# 3. Forçar tenant correto em queries
from apps.core.models import Company
company = Company.objects.get(id=company_id)
connection.set_tenant(company)
```

---

### ❌ "Migration não aplica para todos os tenants"

**Causa**: Django-tenants requer migração especial

**Solução**:

```bash
# 1. Aplicar para tenant público
python manage.py migrate --schema=public

# 2. Aplicar para todos os tenants
python manage.py migrate_schemas

# 3. Se específico, forçar:
python manage.py migrate --schema=tenant_schema_name
```

---

## Problemas de Integração

### ❌ "Stripe integration failing"

**Causa**: API key inválida ou configuração incorreta

**Solução**:

```python
# Em .env:
STRIPE_PUBLIC_KEY=pk_test_xxx  # ou pk_live_xxx
STRIPE_SECRET_KEY=sk_test_xxx  # ou sk_live_xxx

# Em código:
import stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# Testar conexão
try:
    products = stripe.Product.list()
    print("✅ Stripe conectado")
except stripe.error.AuthenticationError:
    print("❌ API key inválida")
```

---

### ❌ "Email não está sendo enviado"

**Causa**: Configuração de email incorreta

**Solução**:

```bash
# 1. Verificar configuração em .env
cat .env | grep EMAIL

# 2. Testar envio
docker-compose exec web python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail(
...     'Subject aqui',
...     'Message aqui',
...     'from@example.com',
...     ['to@example.com'],
... )

# 3. Verificar logs
docker-compose logs web | grep -i "email"

# 4. Se usando Gmail:
# - Ativar "Less secure app access"
# - Ou usar App Password se tiver 2FA
# EMAIL_HOST_PASSWORD=seu-app-password
```

---

## Logs e Debugging

### 📋 Como visualizar logs

```bash
# Todos os serviços
docker-compose logs

# Serviço específico
docker-compose logs web

# Seguir em tempo real
docker-compose logs -f web

# Últimas 100 linhas
docker-compose logs --tail 100 web

# Com timestamp
docker-compose logs --timestamps
```

---

### 🔍 Debug Mode no Django

```python
# Em settings.py
if DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{levelname} {asctime} {module} {message}',
                'style': '{',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }
```

---

### 🐛 Shell do Django

```bash
# Acessar shell interativo
docker-compose exec web python manage.py shell

# Exemplos de debugging
>>> from apps.core.models import User
>>> user = User.objects.first()
>>> print(user)
>>> user.email = 'novo@email.com'
>>> user.save()
>>> exit()
```

---

**Mais problemas?** Verifique os logs com `docker-compose logs -f` 🔍
