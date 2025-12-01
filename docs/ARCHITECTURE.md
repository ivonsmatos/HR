# ARQUITETURA WORKSUITE CLONE - DOCUMENTAÇÃO TÉCNICA

## 1. VISÃO GERAL DA ARQUITETURA

### Padrão Arquitetural

- **Tipo**: Modular Monolith com Multi-Tenancy
- **Framework**: Django 5.0 + Django REST Framework
- **Database**: PostgreSQL (schema isolation via django-tenants)
- **Cache**: Redis
- **Task Queue**: Celery + Redis

### Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────┐
│                    Load Balancer (Nginx)                 │
├─────────────────────────────────────────────────────────┤
│                                                            │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐     │
│  │ Gunicorn    │  │ Gunicorn    │  │   Daphne     │     │
│  │ (Workers)   │  │ (Workers)   │  │ (WebSocket)  │     │
│  └──────┬──────┘  └──────┬──────┘  └──────┬───────┘     │
│         │                │                │              │
│         └────────────────┼────────────────┘              │
│                          │                                │
│              ┌───────────▼──────────┐                    │
│              │  Django Application  │                    │
│              │  - 25+ Apps          │                    │
│              │  - Tenant Routing    │                    │
│              │  - REST APIs         │                    │
│              └───────────┬──────────┘                    │
└──────────────────────────┼─────────────────────────────┘
                           │
          ┌────────────────┼─────────────────┐
          │                │                  │
    ┌─────▼────┐      ┌────▼────┐      ┌─────▼─────┐
    │PostgreSQL│      │  Redis  │      │  Celery   │
    │(Schemas) │      │ (Cache) │      │(Workers)  │
    └──────────┘      └─────────┘      └───────────┘
```

---

## 2. ESTRATÉGIA DE MULTI-TENANCY

### Schema Isolation (Isolamento de Schema)

Cada tenant (empresa) possui seu próprio **schema PostgreSQL** isolado.

**Vantagens:**

- ✅ Máxima segurança e isolamento de dados
- ✅ Performance (queries isoladas por schema)
- ✅ Fácil backup/restore por tenant
- ✅ Conformidade com regulações (LGPD, GDPR)

**Desvantagens:**

- ❌ Mais complexo de gerenciar
- ❌ Maior consumo de memória (múltiplos schemas)

### Fluxo de Requisição Multi-Tenant

```
1. Requisição HTTP chega: GET /api/v1/hrm/employees/
   Domain: tenant1.worksuite.com

2. TenantMainMiddleware intercepta
   ↓
3. Localiza CompanyDomain → identifica Company
   ↓
4. Define schema correto no banco: SET search_path = 'tenant1'
   ↓
5. Django processa requisição com dados isolados
   ↓
6. Retorna resposta ao cliente
```

### Modelos Shared (Não Tenant-Aware)

Alguns modelos são **globais** (não isolados por tenant):

- `SubscriptionPlan` - Planos SaaS (compartilhados)
- `Coupon` - Cupons (podem ser aplicáveis a múltiplos tenants)
- `Company` - Tenant modelo (raiz)

---

## 3. ESTRUTURA DE APPS E DEPENDÊNCIAS

### Hierarquia de Dependências

```
CORE (Independente)
├── Usuários (User)
├── Empresas (Company)
├── Permissões (UserPermission)
└── Auditoria (AuditLog)

HRM (Depende de: CORE)
├── Employees (depende de: core.User)
├── Leaves
├── Attendance
├── Payroll
└── Performance

WORK (Depende de: CORE + HRM + CRM)
├── Projects (depende de: crm.Client)
├── Tasks
├── TimeLogs (depende de: hrm.Employee)
└── Contracts

FINANCE (Depende de: CORE + WORK + CRM)
├── Invoices (depende de: crm.Client)
├── Estimates
├── Proposals
├── Expenses (depende de: core.User)
└── Payments

CRM (Depende de: CORE)
├── Clients
├── Leads
├── Products
└── Orders

RECRUITMENT (Depende de: CORE + HRM)
├── Jobs (depende de: hrm.Department, hrm.Designation)
├── JobApplications
├── InterviewSchedule
├── OfferLetters
└── Candidates

SECURITY (Depende de: CORE)
├── AuditConfig
├── TwoFactorAuth
├── UserSession
├── IpBlocklist
└── SecurityEvent

SAAS_ADMIN (Independente - apenas referencia CORE para Company)
├── SubscriptionPlan
├── Subscription (depende de: core.Company)
├── BillingInvoice
└── Coupon

UTILITIES (Depende de: CORE + HRM + WORK)
├── Tickets (depende de: core.User)
├── TicketReply
├── Assets (depende de: hrm.Employee)
├── Events
├── Messages
└── Notices
```

### Ordem de Criação Recomendada

Para evitar **circular dependencies**:

1. **CORE** → Usuários, Empresas, Permissões, Auditoria
2. **SECURITY** → Segurança, 2FA, Sessions
3. **SAAS_ADMIN** → Planos e Subscriptions
4. **CRM** → Clientes, Leads
5. **HRM** → Employees, Leaves, Attendance, Payroll, Performance
6. **RECRUITMENT** → Jobs, Applications, Offers
7. **WORK** → Projects, Tasks, TimeLogs, Contracts (usa CRM.Client)
8. **FINANCE** → Invoices, Payments (usa CRM.Client)
9. **UTILITIES** → Tickets, Assets, Events (usa tudo anterior)

---

## 4. PADRÕES DE DESENVOLVIMENTO

### Fat Models, Skinny Views

**Modelo:**

```python
# apps/hrm/models.py
class Leave(TenantAwareModel):
    def approve(self, approved_by):
        """Business logic no modelo."""
        if self.status != 'submitted':
            raise ValueError("Only submitted leaves can be approved")
        self.status = 'approved'
        self.approved_by = approved_by
        self.approval_date = timezone.now()
        self.save()
        self._notify_employee()

    def _notify_employee(self):
        """Enviar notificação."""
        send_email_task.delay(self.employee.user.email, ...)
```

**View:**

```python
# apps/hrm/views.py
class LeaveViewSet(ModelViewSet):
    def perform_approve(self, serializer):
        leave = serializer.instance
        leave.approve(approved_by=self.request.user)  # Lógica no modelo!
```

### Services Pattern (para lógica complexa)

```python
# apps/payroll/services.py
class PayrollService:
    @staticmethod
    def generate_monthly_payslip(employee, month):
        """Gera holerite mensal com deduções e bônus."""
        salary = employee.salary.base_salary

        # Calcular deduções
        tax = salary * 0.15  # IRRF
        inss = salary * 0.08

        # Horas extras
        timesheets = Attendance.objects.filter(
            employee=employee,
            date__month=month.month
        )
        overtime_hours = sum(t.overtime_hours for t in timesheets)
        overtime_amount = overtime_hours * (salary / 22 / 8) * 1.5

        # Gerar holerite
        payslip = Payslip.objects.create(
            employee=employee,
            month=month,
            salary_amount=salary,
            deductions=tax + inss,
            net_amount=salary - tax - inss + overtime_amount
        )
        return payslip
```

### Selectors Pattern (para queries complexas)

```python
# apps/hrm/selectors.py
class EmployeeSelector:
    @staticmethod
    def get_active_employees(company):
        return Employee.objects.filter(
            company=company,
            status='active'
        )

    @staticmethod
    def get_employees_by_department(company, department):
        return EmployeeSelector.get_active_employees(company).filter(
            department=department
        )

    @staticmethod
    def get_employees_needing_appraisal(company):
        """Employees sem avaliação há 6+ meses."""
        six_months_ago = timezone.now() - timedelta(days=180)
        return EmployeeSelector.get_active_employees(company).exclude(
            performance_reviews__created_at__gte=six_months_ago
        )
```

### Repository Pattern (para persistência)

```python
# apps/core/repositories.py
class UserRepository:
    @staticmethod
    def create_user(company, email, username, **kwargs):
        user = User.objects.create_user(
            company=company,
            email=email,
            username=username,
            **kwargs
        )
        return user

    @staticmethod
    def get_by_email(company, email):
        return User.objects.get(company=company, email=email)
```

---

## 5. REST API STRUCTURE

### Versionamento de API

```
/api/v1/core/users/              # GET, POST, PATCH, DELETE
/api/v1/core/companies/          # GET, POST
/api/v1/hrm/employees/           # GET, POST, PATCH, DELETE
/api/v1/hrm/employees/{id}/details/
/api/v1/work/projects/           # GET, POST
/api/v1/work/projects/{id}/tasks/
/api/v1/finance/invoices/        # GET, POST
/api/v1/crm/clients/             # GET, POST
/api/v1/recruitment/jobs/        # GET, POST
```

### Response Format

```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com"
  },
  "meta": {
    "timestamp": "2025-12-01T10:30:00Z"
  }
}
```

### Pagination

```json
{
  "count": 100,
  "next": "http://example.com/api/v1/employees/?page=2",
  "previous": null,
  "results": [...]
}
```

### Filtering & Search

```
/api/v1/hrm/employees/?department=sales&status=active
/api/v1/work/tasks/?project=1&status=in_progress
/api/v1/finance/invoices/?client=5&status=paid&date_from=2025-01-01
```

---

## 6. SEGURANÇA

### Autenticação

#### JWT (JSON Web Tokens)

```python
# settings.py
INSTALLED_APPS = [..., 'rest_framework_simplejwt']

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ]
}

# Fluxo:
# 1. POST /api/token/ → recebe access_token + refresh_token
# 2. Authorization: Bearer {access_token}
# 3. Token expira em 15 min → usar refresh_token
# 4. POST /api/token/refresh/ → novo access_token
```

### Autorização

#### Permission Classes

```python
class IsCompanyAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_admin_of_company

class IsEmployeeOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.employee.user == request.user
```

### Proteção contra OWASP Top 10

1. **Injection**: Usar Django ORM (prepared statements)
2. **Broken Auth**: JWT + 2FA + rate limiting
3. **Sensitive Data Exposure**: HTTPS + encryption
4. **XML/XXE**: Não usar XML parsing inseguro
5. **CORS**: Configurar whitelist de origens
6. **Security Misconfiguration**: Django's default security settings
7. **XSS**: Django templates auto-escape HTML
8. **CSRF**: CSRF middleware ativo
9. **Insecure Deserialization**: Não usar pickle
10. **Insufficient Logging**: AuditLog em tudo

---

## 7. PERFORMANCE

### Database Optimization

```python
# Use select_related para FK
employees = Employee.objects.select_related('department', 'designation')

# Use prefetch_related para M2M
projects = Project.objects.prefetch_related('members')

# Indexing em queries frequentes
class Meta:
    indexes = [
        models.Index(fields=['company', '-created_at']),
        models.Index(fields=['user', 'status']),
    ]
```

### Caching Strategy

```python
# Redis cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# Cache frequent queries
from django.core.cache import cache

def get_company_settings(company_id):
    key = f"company_settings_{company_id}"
    settings = cache.get(key)
    if not settings:
        settings = Company.objects.get(id=company_id)
        cache.set(key, settings, 3600)  # 1 hora
    return settings
```

### Background Tasks (Celery)

```python
# tasks.py
@shared_task
def send_payslip_emails(month):
    """Enviar holerites para todos os employees."""
    payslips = Payslip.objects.filter(month=month)
    for payslip in payslips:
        send_payslip_email.delay(payslip.id)

# Scheduling (Celery Beat)
# Rodar todo 1º dia do mês
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'generate-payslips': {
        'task': 'apps.payroll.tasks.send_payslip_emails',
        'schedule': crontab(day_of_month=1, hour=0, minute=0),
    },
}
```

---

## 8. TESTING

### Test Structure

```python
# apps/hrm/tests/test_models.py
class EmployeeModelTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Test Co")
        self.dept = Department.objects.create(name="Sales", company=self.company)

    def test_employee_creation(self):
        emp = Employee.objects.create(
            company=self.company,
            employee_id="EMP001",
            department=self.dept
        )
        self.assertEqual(emp.employee_id, "EMP001")

# apps/hrm/tests/test_views.py
class EmployeeViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(...)
        self.client.force_authenticate(user=self.user)

    def test_list_employees(self):
        response = self.client.get('/api/v1/hrm/employees/')
        self.assertEqual(response.status_code, 200)
```

---

## 9. DEPLOYMENT CHECKLIST

- [ ] Configurar SECRET_KEY em produção
- [ ] DEBUG = False
- [ ] ALLOWED_HOSTS configurados
- [ ] HTTPS/SSL ativo
- [ ] Database backups automatizados
- [ ] Celery workers rodando
- [ ] Redis ativo
- [ ] Email SMTP configurado
- [ ] Static files coletados
- [ ] Monitoring/Logging ativo (Sentry)
- [ ] Rate limiting ativo
- [ ] Firewall configurado

---

## 10. PRÓXIMAS FASES

### Phase 1 (Atual): Esqueleto

- ✅ Estrutura de apps
- ✅ Modelos base
- ✅ Admin Django

### Phase 2: APIs & Frontend

- ⏳ Serializers DRF
- ⏳ ViewSets e URLs
- ⏳ React/Vue frontend

### Phase 3: Features Avançadas

- ⏳ WebSockets (Channels)
- ⏳ Notificações em tempo real
- ⏳ Relatórios (Pandas + ReportLab)
- ⏳ Integrações (Zoom, Google Calendar)

---

**Documento gerado**: 1 de dezembro de 2025
**Versão**: 1.0
