# Worksuite Clone - Enterprise ERP System

Comprehensive Django 5.x multi-tenant SaaS application for enterprise resource planning.

## 📋 Project Overview

**Worksuite Clone** é um ERP empresarial modular construído com Django 5.x e PostgreSQL, suportando multi-tenancy com isolamento de schema. O sistema é dividido em 9 domínios principais (25+ apps), cada um com funcionalidades específicas para gestão completa de recursos humanos, projetos, finanças, CRM e recrutamento.

## 🏗️ Architecture

### Multi-Tenancy Strategy

- **Approach**: Schema isolation via `django-tenants`
- **Database**: PostgreSQL (obrigatório)
- **Tenant Model**: `core.Company`
- **Domain Routing**: Via `core.CompanyDomain`

### Technology Stack

- **Backend**: Django 5.0.1
- **API**: Django REST Framework 3.14.0
- **Database**: PostgreSQL 13+
- **Cache/Queue**: Redis
- **Task Queue**: Celery
- **WebSockets**: Channels + Daphne
- **Auth**: JWT + OAuth2 (via django-oauth-toolkit)
- **Payment**: Stripe, PayPal, Razorpay integrations
- **Documentation**: Swagger/OpenAPI (drf-spectacular)

## 📦 Project Structure

```
HR/
├── config/                    # Django configuration
│   ├── settings.py           # Settings (multi-env support via .env)
│   ├── urls.py              # Main URL routing
│   ├── wsgi.py              # WSGI application
│   └── asgi.py              # ASGI application (WebSockets)
│
├── apps/                      # Django applications (25+ apps)
│   ├── core/                 # Core: Users, Companies, Auth, Audit
│   ├── hrm/                  # HR: Employees, Leaves, Attendance, Payroll, Performance
│   ├── work/                 # Work: Projects, Tasks, TimeLogs, Contracts
│   ├── finance/              # Finance: Invoices, Estimates, Expenses, Payments
│   ├── crm/                  # CRM: Clients, Leads, Products, Orders
│   ├── recruitment/          # ATS: Jobs, Applications, Interviews, Offers
│   ├── security/             # Security: Audit, IP Blocking, 2FA, Sessions
│   ├── saas_admin/           # SaaS: Plans, Subscriptions, Billing, Coupons
│   └── utilities/            # Utilities: Tickets, Assets, Events, Messages, Notices
│
├── templates/                 # HTML templates
├── static/                    # Static assets (CSS, JS, images)
├── media/                     # User-uploaded media
├── docs/                      # Documentation
│
├── manage.py                  # Django CLI
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (not in git)
└── .gitignore                 # Git ignore rules
```

## 🌐 Progressive Web App (PWA)

**Worksuite Clone** é um **Progressive Web App** completo:

- ✅ **Instalável** - Instale como aplicativo nativo
- ✅ **Offline-first** - Funciona sem conexão de internet
- ✅ **Responsiva** - Funciona em desktop, tablet e mobile
- ✅ **Rápida** - Cache inteligente e carregamento otimizado
- ✅ **Segura** - HTTPS obrigatório e isolamento de origem
- ✅ **Notificações** - Push notifications em tempo real

**[📖 Leia o guia PWA completo →](docs/PWA.md)**

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL 13+
- Redis 6+ (for Celery)
- Git
- HTTPS (required for PWA - use mkcert in development)

### Installation

1. **Clone repository**

   ```bash
   git clone https://github.com/ivonsmatos/HR.git
   cd HR
   ```

2. **Create virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**

   ```bash
   cp .env .env.local
   # Edit .env.local with your database credentials and settings
   ```

5. **Create PostgreSQL database**

   ```bash
   createdb worksuite_db
   ```

6. **Run migrations**

   ```bash
   python manage.py migrate_schemas
   ```

7. **Create superuser**

   ```bash
   python manage.py createsuperuser
   ```

8. **Start development server**

   ```bash
   python manage.py runserver
   ```

9. **Access admin panel**
   - Admin: http://localhost:8000/admin
   - API Docs: http://localhost:8000/api/schema/swagger-ui/

## 📚 Apps & Modules

### 1. Core (`apps/core`)

- **CustomUser**: User model com suporte a multi-tenant
- **Company**: Modelo tenant com domínio customizável
- **UserPermission**: Controle granular de acesso
- **AuditLog**: Registro de todas as ações

### 2. HRM (`apps/hrm`)

- **Employees**: Gestão de perfis, departamentos, designações
- **Leaves**: Solicitação e aprovação de férias
- **Attendance**: Ponto, turnos, frequência
- **Payroll**: Folha de pagamento, estrutura salarial, holerites
- **Performance**: Avaliações, OKRs, metas

### 3. Work (`apps/work`)

- **Projects**: Gestão de projetos e membros
- **Tasks**: Kanban, status, prioridades
- **TimeLogs**: Rastreamento de horas por tarefa
- **Contracts**: Gestão de contratos com clientes

### 4. Finance (`apps/finance`)

- **Invoices**: Faturas e itens de fatura
- **Estimates**: Orçamentos para clientes
- **Proposals**: Propostas comerciais
- **Expenses**: Controle de despesas
- **Payments**: Integração com gateways (Stripe, PayPal, etc.)

### 5. CRM (`apps/crm`)

- **Clients**: Cadastro de clientes
- **Leads**: Gestão de oportunidades
- **Products**: Catálogo de produtos/serviços
- **Orders**: Pedidos de venda

### 6. Recruitment (`apps/recruitment`)

- **Jobs**: Vagas abertas
- **JobApplications**: Pipeline de candidatos
- **Interviews**: Agendamento de entrevistas
- **OfferLetters**: Cartas de oferta
- **Candidates**: Banco de talentos

### 7. Security (`apps/security`)

- **AuditLogs**: Logs de auditoria
- **IpBlocklist**: Bloqueio de IPs suspeitos
- **TwoFactorAuth**: Autenticação em 2 fatores
- **UserSession**: Gerenciamento de sessões
- **SecurityEvents**: Eventos de segurança

### 8. SaaS Admin (`apps/saas_admin`)

- **SubscriptionPlans**: Planos de assinatura
- **Subscriptions**: Assinaturas de clientes
- **BillingInvoice**: Faturas SaaS
- **Coupons**: Códigos promocionais

### 9. Utilities (`apps/utilities`)

- **Tickets**: Helpdesk e suporte
- **Assets**: Gestão de patrimônio
- **Events**: Calendário de eventos
- **Messages**: Chat interno
- **Notices**: Mural de avisos

## 🔐 Authentication & Authorization

### User Roles (WIP)

- **Super Admin**: Gerencia todas as tenants
- **Tenant Admin**: Gerencia sua empresa
- **Manager**: Gerencia equipe/departamento
- **Employee**: Acesso básico
- **Contractor**: Acesso limitado

### 2FA Methods

- Email OTP
- SMS via Twilio
- Authenticator App (Google Authenticator)

## 📊 Database Models

### Base Classes

- **BaseModel**: Abstrato com `created_at`, `updated_at`, `is_active`
- **TenantAwareModel**: Herda de BaseModel, adiciona `company` FK
- Todas as models businessse herdam de `TenantAwareModel` para garantir isolamento

### Key Relationships

- `Company` (1) → `User` (M): Usuários pertencem a uma empresa
- `Company` (1) → `AuditLog` (M): Logs isolados por empresa
- `Project` (1) → `Task` (M) → `TimeLog` (M)
- `Client` (1) → `Invoice` (M), `Order` (M)
- `Job` (1) → `JobApplication` (M) → `InterviewSchedule` (M)

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# Django
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=worksuite_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Stripe
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific app tests
pytest apps/core/tests/

# With coverage
pytest --cov=apps --cov-report=html
```

## 📖 Development Guidelines

### Models (Fat Models, Skinny Views)

- Lógica de negócio deve estar nos modelos
- Use métodos no modelo para regras complexas
- Exemplo:
  ```python
  class Leave(TenantAwareModel):
      def approve(self, approved_by):
          self.status = 'approved'
          self.approved_by = approved_by
          self.save()
  ```

### Services Pattern (para lógica complexa)

```python
# apps/payroll/services.py
class PayrollService:
    @staticmethod
    def generate_monthly_payslip(employee, month):
        # Complex payroll logic
        pass
```

### Selectors Pattern (para queries complexas)

```python
# apps/hrm/selectors.py
class EmployeeSelector:
    @staticmethod
    def get_active_employees(company):
        return Employee.objects.filter(company=company, status='active')
```

### API ViewSets

```python
# apps/hrm/views.py
from rest_framework.viewsets import ModelViewSet

class EmployeeViewSet(ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]
```

## 🚢 Deployment

### Docker (Recomendado)

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### Gunicorn + Nginx

```bash
# Install
pip install gunicorn

# Run
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Celery Worker

```bash
celery -A config worker -l info
```

## 📋 Roadmap

### Phase 1 (MVP)

- ✅ Estrutura base e modelos
- ⏳ REST APIs
- ⏳ Admin Django personalizado

### Phase 2

- ⏳ Frontend (React)
- ⏳ WebSockets em tempo real
- ⏳ Notificações

### Phase 3

- ⏳ Mobile app
- ⏳ Integração com APIs externas (Zoom, Google Calendar)
- ⏳ Relatórios avançados

## 🛠️ Contributing

1. Fork o repositório
2. Crie uma branch (`git checkout -b feature/amazing-feature`)
3. Commit suas mudanças (`git commit -m 'Add amazing feature'`)
4. Push para a branch (`git push origin feature/amazing-feature`)
5. Abra um Pull Request

## 📝 License

Este projeto está sob a licença MIT.

## 📧 Contact

- **Author**: Ivon Smatos
- **Email**: ivon@example.com
- **GitHub**: @ivonsmatos

---

**Last Updated**: December 1, 2025
