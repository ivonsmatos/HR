# FASE D: PLANO DE EXECUÇÃO & ROADMAP DE DESENVOLVIMENTO

## 📋 Ordem Recomendada de Implementação

Para evitar dependências circulares e garantir desenvolvimento lógico, aqui está a ordem recomendada de implementação dos apps:

---

## STAGE 1: FUNDAÇÃO (CORE INFRASTRUTURA)

### Passo 1: CORE App ✅ PRONTO

**Duração**: 1-2 semanas

**O que implementar:**

- [ ] Serializers para `User`, `Company`
- [ ] ViewSets para `User`, `Company`
- [ ] Autenticação JWT
- [ ] Permissões customizadas
- [ ] Tests unitários

**Modelos a usar:**

- `core.User` (CustomUser)
- `core.Company` (Tenant)
- `core.AuditLog`

**Dependências externas:**

- Django-tenants (biblioteca)
- djangorestframework-simplejwt

**Tarefas:**

```bash
# 1. Serializers (apps/core/serializers.py)
# - UserSerializer
# - CompanySerializer
# - CompanyDetailSerializer

# 2. ViewSets (apps/core/views.py)
# - UserViewSet
# - CompanyViewSet

# 3. URLs (apps/core/urls.py)
# - router.register('users/', UserViewSet)
# - router.register('companies/', CompanyViewSet)

# 4. Tests (apps/core/tests/)
# - test_user_creation
# - test_company_creation
# - test_jwt_authentication
```

---

### Passo 2: SECURITY App ✅ PRONTO

**Duração**: 1 semana
**Dependência**: CORE

**O que implementar:**

- [ ] Serializers para `TwoFactorAuth`, `SecurityEvent`
- [ ] ViewSets para segurança
- [ ] Middleware de audit logging (JÁ CRIADO)
- [ ] Rate limiting
- [ ] IP blocklist management

**Modelos a usar:**

- `security.TwoFactorAuth`
- `security.UserSession`
- `security.SecurityEvent`
- `security.IpBlocklist`

**Tarefas:**

```bash
# 1. Implementar 2FA endpoints
# 2. Implementar IP blocklist
# 3. Testes de segurança
```

---

### Passo 3: SAAS_ADMIN App ✅ PRONTO

**Duração**: 1-2 semanas
**Dependência**: CORE

**O que implementar:**

- [ ] Serializers para `SubscriptionPlan`, `Subscription`
- [ ] ViewSets para planos e subscriptions
- [ ] Webhook handlers (Stripe, PayPal)
- [ ] Coupon system

**Modelos a usar:**

- `saas_admin.SubscriptionPlan`
- `saas_admin.Subscription`
- `saas_admin.BillingInvoice`
- `saas_admin.Coupon`

**Tarefas:**

```bash
# 1. Payment gateway integrations
# 2. Webhook listeners
# 3. Billing automation
```

---

## STAGE 2: GESTÃO DE PESSOAS

### Passo 4: HRM App (Fase 1: Employees) ✅ PRONTO

**Duração**: 2-3 semanas
**Dependência**: CORE

**O que implementar:**

- [ ] Serializers para `Employee`, `Department`, `Designation`
- [ ] ViewSets para HR basics
- [ ] Upload de documentos (RG, CPF, etc)
- [ ] Profile management
- [ ] Organization hierarchy

**Modelos a usar:**

- `hrm.Employee`
- `hrm.Department`
- `hrm.Designation`

**Tarefas:**

```bash
# 1. EmployeeSerializer, EmployeeViewSet
# 2. DepartmentSerializer, DepartmentViewSet
# 3. DesignationSerializer, DesignationViewSet
# 4. Hierarquia (reporting_manager)
# 5. Testes
```

---

### Passo 5: HRM App (Fase 2: Attendance & Leaves) ✅ PRONTO

**Duração**: 2 semanas
**Dependência**: HRM (Employees)

**O que implementar:**

- [ ] Serializers para `Attendance`, `Leave`, `LeaveType`
- [ ] ViewSets para presença e licenças
- [ ] Approval workflow
- [ ] Leave balance tracking
- [ ] Shift management

**Modelos a usar:**

- `hrm.Attendance`
- `hrm.Leave`
- `hrm.LeaveType`
- `hrm.Shift`

**Tarefas:**

```bash
# 1. LeaveTypeSerializer
# 2. LeaveViewSet (com approve/reject)
# 3. AttendanceSerializer
# 4. Shift management
# 5. Leave balance calculator (Service)
```

---

### Passo 6: HRM App (Fase 3: Payroll & Performance) ✅ PRONTO

**Duração**: 3-4 semanas
**Dependência**: HRM (Employees, Attendance)

**O que implementar:**

- [ ] Serializers para `Payslip`, `EmployeeSalary`, `SalaryStructure`
- [ ] Payroll processing engine
- [ ] Holerite PDF generation
- [ ] Performance reviews & goals
- [ ] Celery tasks para folha mensal

**Modelos a usar:**

- `hrm.Payslip`
- `hrm.EmployeeSalary`
- `hrm.SalaryStructure`
- `hrm.PerformanceReview`
- `hrm.PerformanceGoal`

**Tarefas:**

```bash
# 1. PayrollService (complexo!)
# 2. PayslipSerializer, PayslipViewSet
# 3. Celery task: generate_monthly_payslips()
# 4. PDF geração (reportlab)
# 5. Performance review endpoints
```

---

## STAGE 3: GESTÃO DE CLIENTES

### Passo 7: CRM App ✅ PRONTO

**Duração**: 2 semanas
**Dependência**: CORE

**O que implementar:**

- [ ] Serializers para `Client`, `Lead`, `Product`, `Order`
- [ ] ViewSets para CRM
- [ ] Sales pipeline (lead stages)
- [ ] Product catalog
- [ ] Order management

**Modelos a usar:**

- `crm.Client`
- `crm.Lead`
- `crm.Product`
- `crm.Order`
- `crm.OrderItem`

**Tarefas:**

```bash
# 1. ClientSerializer, ClientViewSet
# 2. LeadSerializer, LeadViewSet
# 3. ProductSerializer, ProductViewSet
# 4. OrderSerializer, OrderViewSet
# 5. Lead scoring logic (Service)
```

---

## STAGE 4: GESTÃO DE PROJETOS

### Passo 8: WORK App (Projects & Tasks) ✅ PRONTO

**Duração**: 3 semanas
**Dependência**: CORE + CRM (Client)

**O que implementar:**

- [ ] Serializers para `Project`, `ProjectMember`, `Task`
- [ ] ViewSets para projetos e tarefas
- [ ] Kanban board logic
- [ ] Task assignment workflow
- [ ] Project member allocation

**Modelos a usar:**

- `work.Project`
- `work.ProjectMember`
- `work.Task`
- `work.TaskComment`

**Tarefas:**

```bash
# 1. ProjectSerializer, ProjectViewSet
# 2. TaskSerializer, TaskViewSet (com Kanban states)
# 3. Task assignment workflow
# 4. Kanban board API (GET /projects/{id}/kanban/)
# 5. Signals para auto-sync completion percentage
```

---

### Passo 9: WORK App (TimeLogs & Contracts) ✅ PRONTO

**Duração**: 2 semanas
**Dependência**: WORK (Projects), HRM (Employees)

**O que implementar:**

- [ ] Serializers para `TimeLog`, `Contract`
- [ ] ViewSets para rastreamento de tempo
- [ ] Contract management
- [ ] Billing from TimeLogs

**Modelos a usar:**

- `work.TimeLog`
- `work.Contract`

**Tarefas:**

```bash
# 1. TimeLogSerializer, TimeLogViewSet
# 2. ContractSerializer, ContractViewSet
# 3. Billing calculations (Service)
# 4. Project profitability reports
```

---

## STAGE 5: GESTÃO FINANCEIRA

### Passo 10: FINANCE App ✅ PRONTO

**Duração**: 3-4 semanas
**Dependência**: WORK + CRM

**O que implementar:**

- [ ] Serializers para `Invoice`, `Estimate`, `Proposal`, `Expense`, `Payment`
- [ ] ViewSets para finanças
- [ ] Invoice generation from TimeLogs
- [ ] Payment gateway integration
- [ ] Expense approval workflow
- [ ] Financial reports

**Modelos a usar:**

- `finance.Invoice`
- `finance.InvoiceItem`
- `finance.Estimate`
- `finance.Proposal`
- `finance.Expense`
- `finance.Payment`
- `finance.PaymentGateway`

**Tarefas:**

```bash
# 1. InvoiceSerializer, InvoiceViewSet
# 2. EstimateSerializer
# 3. ProposalSerializer
# 4. ExpenseSerializer, ExpenseViewSet (com approval)
# 5. PaymentViewSet (webhook handling)
# 6. Invoice PDF generation
# 7. Financial reports (Service)
```

---

## STAGE 6: RECRUTAMENTO

### Passo 11: RECRUITMENT App ✅ PRONTO

**Duração**: 2-3 semanas
**Dependência**: CORE + HRM (Department, Designation)

**O que implementar:**

- [ ] Serializers para `Job`, `JobApplication`, `InterviewSchedule`, `OfferLetter`, `Candidate`
- [ ] ViewSets para recrutamento
- [ ] Application tracking pipeline
- [ ] Interview scheduling
- [ ] Offer letter generation
- [ ] Email notifications

**Modelos a usar:**

- `recruitment.Job`
- `recruitment.JobApplication`
- `recruitment.InterviewSchedule`
- `recruitment.OfferLetter`
- `recruitment.Candidate`

**Tarefas:**

```bash
# 1. JobSerializer, JobViewSet
# 2. JobApplicationSerializer, status transitions
# 3. InterviewScheduleSerializer (com notificações)
# 4. OfferLetterSerializer + PDF generation
# 5. CandidateSerializer (talent pool)
# 6. Email tasks (Celery)
```

---

## STAGE 7: UTILIDADES

### Passo 12: UTILITIES App ✅ PRONTO

**Duração**: 2 semanas
**Dependência**: CORE + HRM

**O que implementar:**

- [ ] Serializers para `Ticket`, `Asset`, `Event`, `Message`, `Notice`
- [ ] ViewSets para utilidades
- [ ] Helpdesk ticket system
- [ ] Asset allocation tracking
- [ ] Calendar events
- [ ] Internal messaging

**Modelos a usar:**

- `utilities.Ticket`
- `utilities.TicketReply`
- `utilities.Asset`
- `utilities.Event`
- `utilities.Message`
- `utilities.Notice`

**Tarefas:**

```bash
# 1. TicketSerializer, TicketViewSet
# 2. AssetSerializer, allocation logic
# 3. EventSerializer (calendar)
# 4. MessageSerializer (chat)
# 5. NoticeSerializer (announcements)
# 6. Email notifications
```

---

## DEPENDENCY GRAPH (Visual)

```
                        CORE ◄─ SECURITY
                    ╱     │     ╲
                   ╱      │      ╲
               SAAS      ✓       (Audit Logging ✓)
              ADMIN      │
                         │
        ╔═══════════════╩══════════════════╗
        │                                  │
       HRM ◄─────────────────────┐        CRM
        │                        │         │
        ├─ Employees (✓)        │         │
        ├─ Leaves/Attendance (✓)│         │
        └─ Payroll (✓)          │         │
           Performance (✓)      │         │
                                │         │
                            WORK (✓)      │
                           ╱    │    ╲    │
                          ╱     │     ╲   │
                    Projects   Tasks  Contracts ──┐
                         │              │          │
                         └──────────────┴──────────┤
                                                   │
                                            FINANCE (✓)
                                         ╱    │    │    ╲
                                        ╱     │    │     ╲
                                  Invoices Estimates Proposals
                                        │    │    │
                                    Expenses Payments

              RECRUITMENT ◄─ HRM (Departments, Designations)
                │                          │
                └──────────────────────────┘

              UTILITIES ◄─ HRM + WORK + CORE
```

---

## TIMELINE DE DESENVOLVIMENTO

### Estimativa Total: 4-6 MESES

| Stage | Apps                         | Duração | Cumulativo |
| ----- | ---------------------------- | ------- | ---------- |
| 1     | CORE + SECURITY + SAAS_ADMIN | 3-4 sem | 3-4 sem    |
| 2     | HRM (3 fases)                | 5-6 sem | 8-10 sem   |
| 3     | CRM                          | 2 sem   | 10-12 sem  |
| 4     | WORK (2 fases)               | 5 sem   | 15-17 sem  |
| 5     | FINANCE                      | 3-4 sem | 18-21 sem  |
| 6     | RECRUITMENT                  | 2-3 sem | 20-24 sem  |
| 7     | UTILITIES                    | 2 sem   | 22-26 sem  |

---

## INSTRUÇÕES PARA PRÓXIMA FASE (Phase 2)

### ✅ Já está pronto:

1. ✅ Estrutura de diretórios
2. ✅ Modelos de dados (57 modelos)
3. ✅ Admin Django customizado
4. ✅ Middleware de auditoria
5. ✅ Settings multi-tenant

### 🚀 Próximos passos:

#### 1. Instalar e validar ambiente

```bash
pip install -r requirements.txt
python manage.py check
```

#### 2. Criar migrações iniciais

```bash
python manage.py makemigrations
python manage.py migrate_schemas
```

#### 3. Criar superuser de teste

```bash
python manage.py createsuperuser
```

#### 4. Iniciar com CORE app

```bash
# Criar serializers (apps/core/serializers.py)
# Criar viewsets (apps/core/views.py)
# Atualizar urls (apps/core/urls.py)
# Adicionar testes (apps/core/tests/)
```

#### 5. Testar via Swagger

```bash
python manage.py runserver
# Acessar: http://localhost:8000/api/schema/swagger-ui/
```

---

## CHECKLIST PARA CADA NOVO APP

Ao começar um novo app, usar este checklist:

```markdown
### [ ] Serializers

- [ ] Listar fields todos
- [ ] Adicionar validações
- [ ] Nested serializers se necessário

### [ ] ViewSets/Views

- [ ] CRUD endpoints
- [ ] Filtering & search
- [ ] Pagination
- [ ] Permissions

### [ ] Signals/Hooks

- [ ] post_save signals
- [ ] Auto-update relacionados

### [ ] Services (se lógica complexa)

- [ ] Business logic separado
- [ ] Celery tasks

### [ ] Tests

- [ ] Unit tests
- [ ] Integration tests
- [ ] API tests

### [ ] Documentation

- [ ] Docstrings
- [ ] API documentation
```

---

## COMMITS RECOMENDADOS (Git)

```bash
# Cada passo completo = 1 commit

git add apps/core/
git commit -m "feat(core): add User, Company models and serializers"

git add apps/hrm/
git commit -m "feat(hrm): add Employee, Department, Designation models"

git add apps/core/views.py
git commit -m "feat(core): implement UserViewSet and CompanyViewSet"

# Etc...
```

---

## STATUS ATUAL

```
┌─────────────────────────────────────────────────────────────┐
│  FASE A: ARQUITETURA & MODELOS DE DADOS ✅ 100% COMPLETO   │
├─────────────────────────────────────────────────────────────┤
│  ✅ Estrutura de diretórios                                 │
│  ✅ 57 modelos de dados em 9 apps                           │
│  ✅ Django admin customizado                                │
│  ✅ Middleware de auditoria                                 │
│  ✅ Settings multi-tenant                                   │
│  ✅ Requirements.txt com 60+ pacotes                         │
│  ✅ Documentação completa                                   │
├─────────────────────────────────────────────────────────────┤
│  PRÓXIMA FASE: Phase 2 - Serializers & ViewSets             │
│  Começar por: CORE App (Stage 1, Passo 1)                   │
└─────────────────────────────────────────────────────────────┘
```

---

**Documento criado**: 1 de dezembro de 2025  
**Versão**: 1.0  
**Status**: Ready for Phase 2 development
