# 📊 Guia de Cobertura de Testes - Melhorias

**Status Atual:**
- apps/core/ - 75% ✅
- apps/security/ - 68% ⚠️
- apps/hrm/ - 55% ❌
- apps/work/ - 48% ❌ (Crítica)
- config/ - 82% ✅
- **TOTAL - 60%** (Target: 75%+)

---

## 🎯 Estratégia por Módulo

### apps/hrm/ (55% → 80%+) | +25 pontos

**O que testar:**

#### 1. Employee Management (Employee Model)
```python
# CRUD Tests
- test_employee_creation()          # Criar funcionário
- test_employee_update()            # Editar funcionário
- test_employee_delete()            # Deletar funcionário
- test_employee_retrieve()          # Recuperar funcionário
- test_employee_list()              # Listar com filtros

# Validation Tests
- test_employee_email_unique()      # Email único
- test_employee_phone_validation()  # Validação de telefone
- test_employee_date_of_birth()     # Validação de data
- test_employee_salary_range()      # Validação de salário

# Business Logic
- test_employee_tenure_calculation()     # Cálculo de tempo na empresa
- test_employee_retirement_eligibility() # Elegibilidade para aposentadoria
```

#### 2. Leave Management (Leave Model)
```python
# Leave Request Flow
- test_leave_request_creation()     # Solicitar licença
- test_leave_approval()             # Aprovação
- test_leave_rejection()            # Rejeição
- test_leave_cancellation()         # Cancelamento

# Validation
- test_leave_date_validation()      # Datas válidas
- test_overlapping_leaves()         # Detecção de sobreposição
- test_leave_balance()              # Saldo de dias

# Balance Tracking
- test_annual_leave_calculation()   # Licença anual
- test_sick_leave_calculation()     # Licença médica
- test_maternity_leave()            # Licença maternidade
```

#### 3. Attendance (Attendance Model)
```python
# Check-in/Check-out
- test_attendance_checkin()         # Entry de presença
- test_attendance_checkout()        # Saída de presença
- test_late_checkin()               # Detecção de atraso
- test_early_checkout()             # Saída antecipada

# Validation
- test_checkout_without_checkin()   # Validação de ordem
- test_duplicate_checkin()          # Prevenção de duplicata
- test_working_hours_calculation()  # Cálculo de horas

# Reports
- test_attendance_report()          # Relatório de presença
- test_absenteeism_tracking()       # Rastreamento de faltas
```

#### 4. Payroll (Payroll Model)
```python
# Salary Calculation
- test_gross_salary_calculation()   # Salário bruto
- test_deduction_application()      # Aplicação de descontos
- test_net_salary_calculation()     # Salário líquido

# Components
- test_basic_salary()               # Salário base
- test_allowances()                 # Adicionais
- test_bonus_calculation()          # Bônus
- test_overtime_calculation()       # Horas extras

# Validation
- test_payroll_date_range()         # Validação de período
- test_payroll_approval()           # Fluxo de aprovação
- test_payroll_finalization()       # Finalização
```

#### 5. Performance (PerformanceReview Model)
```python
# Review Cycle
- test_review_creation()            # Criar avaliação
- test_review_submission()          # Submeter avaliação
- test_review_approval()            # Aprovar avaliação

# Feedback
- test_self_assessment()            # Auto-avaliação
- test_manager_feedback()           # Feedback do gestor
- test_360_feedback()               # Feedback 360

# Metrics
- test_kpi_tracking()               # Acompanhamento de KPI
- test_rating_calculation()         # Cálculo de nota
```

**Total: 45 testes novos**

---

### apps/work/ (48% → 80%+) | +32 pontos

**O que testar:**

#### 1. Project Management (Project Model)
```python
# CRUD & Lifecycle
- test_project_creation()           # Criar projeto
- test_project_update()             # Editar projeto
- test_project_status_transition()  # Mudança de status
- test_project_completion()         # Conclusão
- test_project_archive()            # Arquivamento

# Validation
- test_project_dates()              # Validação de datas
- test_project_budget()             # Validação de orçamento
- test_required_fields()            # Campos obrigatórios

# Relationships
- test_project_team_assignment()    # Atribuir equipe
- test_project_resource_allocation()# Alocação de recursos
```

#### 2. Task Management (Task Model)
```python
# Task Lifecycle
- test_task_creation()              # Criar tarefa
- test_task_assignment()            # Atribuir tarefa
- test_task_status_update()         # Atualizar status
- test_task_completion()            # Marcar como concluída
- test_task_reopening()             # Reabrir tarefa

# Priority & Urgency
- test_task_priority_levels()       # Níveis de prioridade
- test_priority_change()            # Mudança de prioridade
- test_urgent_task_escalation()     # Escalonamento

# Dependencies
- test_subtask_creation()           # Criar subtarefa
- test_task_dependency()            # Dependência entre tarefas
- test_blocking_resolution()        # Resolução de bloqueios

# Validation
- test_task_date_validation()       # Datas válidas
- test_assignee_capacity()          # Capacidade de atribuído
```

#### 3. Time Tracking (TimeEntry Model)
```python
# Entry Management
- test_time_entry_creation()        # Criar entrada
- test_time_entry_update()          # Editar entrada
- test_time_entry_deletion()        # Deletar entrada
- test_time_entry_approval()        # Aprovar entrada

# Validation
- test_time_duration_validation()   # Validação de duração
- test_overlapping_entries()        # Detecção de sobreposição
- test_task_link_validation()       # Validação de tarefa

# Reporting
- test_daily_timesheet()            # Timesheet diária
- test_weekly_timesheet()           # Timesheet semanal
- test_monthly_timesheet()          # Timesheet mensal
- test_time_utilization_report()    # Relatório de utilização
```

#### 4. Contract Management (Contract Model)
```python
# Contract Lifecycle
- test_contract_creation()          # Criar contrato
- test_contract_amendment()         # Emenda de contrato
- test_contract_renewal()           # Renovação
- test_contract_termination()       # Rescisão

# Types
- test_vendor_contract()            # Contrato de fornecedor
- test_client_contract()            # Contrato de cliente
- test_service_contract()           # Contrato de serviço

# Terms
- test_contract_terms()             # Validação de termos
- test_payment_terms()              # Termos de pagamento
- test_renewal_conditions()         # Condições de renovação
```

#### 5. Milestone Tracking (Milestone Model)
```python
# Milestone Lifecycle
- test_milestone_creation()         # Criar marco
- test_milestone_update()           # Editar marco
- test_milestone_completion()       # Marcar como concluído

# Tracking
- test_milestone_dependency()       # Dependência de marcos
- test_milestone_status()           # Status do marco
- test_milestone_progress()         # Progresso do marco

# Reporting
- test_milestone_burndown()         # Gráfico de burndown
- test_milestone_timeline()         # Timeline de marcos
```

**Total: 50 testes novos**

---

### apps/security/ (68% → 85%+) | +17 pontos

**O que testar:**

```python
# Audit Logging
- test_audit_log_creation()         # Criar log
- test_audit_action_tracking()      # Rastrear ação
- test_audit_user_tracking()        # Rastrear usuário
- test_audit_timestamp()            # Registro de timestamp

# IP Blocking
- test_ip_blocking()                # Bloquear IP
- test_ip_whitelist()               # Whitelist de IP
- test_ip_bypass()                  # Bypass de IP

# 2FA
- test_2fa_setup()                  # Setup de 2FA
- test_2fa_token_generation()       # Geração de token
- test_2fa_validation()             # Validação de token

# Sessions
- test_session_management()         # Gerenciamento de sessão
- test_concurrent_session_limit()   # Limite de sessões
- test_session_timeout()            # Timeout de sessão
- test_session_logout()             # Logout de sessão
```

**Total: 14 testes novos**

---

## 📈 Impacto Esperado

| Módulo | Atual | Target | Novos Testes | Impacto |
|--------|-------|--------|--------------|---------|
| hrm/ | 55% | 80% | 45 | +25% |
| work/ | 48% | 80% | 50 | +32% |
| security/ | 68% | 85% | 14 | +17% |
| **TOTAL** | **60%** | **75%** | **109** | **+15%** |

---

## 🔧 Como Implementar

### 1. Estrutura de Teste Básica

```python
from django.test import TestCase

class EmployeeTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        # Setup uma vez por classe
        cls.company = Company.objects.create(...)
        cls.user = User.objects.create_user(...)
    
    def setUp(self):
        # Setup antes de cada teste
        self.client = Client()
        self.client.force_login(self.user)
    
    def test_something(self):
        # Teste individual
        response = self.client.post('/api/employees/', {...})
        self.assertEqual(response.status_code, 201)
```

### 2. Rodar Testes com Coverage

```bash
# Rodar todos os testes com coverage
coverage run -m pytest tests/ -v

# Gerar relatório
coverage report

# Relatório HTML
coverage html
open htmlcov/index.html
```

### 3. Executar por Módulo

```bash
# Apenas tests/test_coverage_improvement.py
pytest tests/test_coverage_improvement.py::HRMCoverageTests -v

# Apenas hrm
coverage run -m pytest tests/ -k "hrm" -v
coverage report
```

---

## ✅ Checklist de Implementação

- [ ] Implementar 45 testes para apps/hrm/
- [ ] Implementar 50 testes para apps/work/
- [ ] Implementar 14 testes para apps/security/
- [ ] Atingir 75% cobertura total
- [ ] Validar que todos os testes passam
- [ ] Gerar relatório final de cobertura
- [ ] Fazer commit com mensagem: "test: +109 testes para 75% cobertura"

---

## 📊 Próximos Passos

1. **Agora:** Você tem o arquivo `test_coverage_improvement.py` com estrutura pronta
2. **Próximo:** Implementar os testes seguindo a estratégia acima
3. **Final:** Rodar coverage e validar 75%+

Cada teste deve ser simples, focalizado e testável.

---

**Prioridade:** HIGH - Implementar nos próximos dias
