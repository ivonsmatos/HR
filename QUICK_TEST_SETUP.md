# QUICK_TEST_SETUP.md

## Setup Rápido - Testes Prontos para Executar

### 1️⃣ Instalação Mínima (2 minutos)

```bash
# Instalar pacotes de teste
pip install pytest pytest-django coverage faker

# OPÇÃO A: Usar SQLite (Recomendado - Rápido)
# Nenhuma instalação adicional necessária!

# OPÇÃO B: Usar PostgreSQL (se necessário)
pip install psycopg2-binary==2.9.9
# Criar banco: createdb hr_test
```

### 2️⃣ Validar Instalação

```bash
# Ver resumo dos testes implementados
python test_summary.py

# Esperado:
# ✅ test_hrm_implemented.py - 28 testes
# ✅ test_work_security_implemented.py - 35 testes  
# ✅ test_config_settings.py - 42 testes
# TOTAL: 105 testes implementados
```

### 3️⃣ Executar Testes

```bash
# ✅ Executar tudo (Recomendado para primeira vez)
pytest tests/ -v --tb=short

# ✅ Executar módulo específico
pytest tests/test_hrm_implemented.py -v
pytest tests/test_work_security_implemented.py -v
pytest tests/test_config_settings.py -v

# ✅ Executar teste específico
pytest tests/test_hrm_implemented.py::HRMCoreModelTests::test_user_creation -v

# ✅ Executar com saída resumida
pytest tests/ -q

# ✅ Parar no primeiro erro
pytest tests/ -x

# ✅ Mostrar prints durante testes
pytest tests/ -v -s
```

### 4️⃣ Medir Cobertura

```bash
# ✅ Executar com cobertura
coverage run -m pytest tests/ -v

# ✅ Ver relatório no terminal
coverage report

# ✅ Gerar HTML report (abrir em browser)
coverage html
# Abrir: htmlcov/index.html

# ✅ Ver cobertura de arquivo específico
coverage report tests/test_hrm_implemented.py
```

### 5️⃣ Troubleshooting

#### Erro: `ModuleNotFoundError: No module named 'django'`
```bash
pip install django==4.2.8 djangorestframework==3.14.0
```

#### Erro: `ModuleNotFoundError: No module named 'psycopg2'`
```bash
# Use SQLite em vez de PostgreSQL para testes
# Ou instale: pip install psycopg2-binary==2.9.9
```

#### Erro: `ImproperlyConfigured: Requested setting DATABASES`
```bash
# Usar conftest.py automático
# Ou: pytest --ds=config.settings.test
```

#### Testes rodam lento?
```bash
# Usar -n para paralelização (instalar pytest-xdist)
pip install pytest-xdist
pytest tests/ -n auto
```

---

## 📊 Matriz de Cobertura Esperada

| Módulo | Testes | Linhas | Cobertura Esperada |
|--------|--------|--------|-------------------|
| HRM | 28 | 432 | 65-70% |
| Work | 16 | 250 | 55-60% |
| Security | 20 | 200 | 75-85% |
| Config | 42 | 305 | 90%+ |
| **TOTAL** | **105** | **1181** | **65-70%** |

---

## 🎯 Próximos Passos

### Passo 1: Rodar testes básicos
```bash
pytest tests/test_config_settings.py::DjangoSettingsTests -v
```

### Passo 2: Ver cobertura inicial
```bash
coverage run -m pytest tests/test_config_settings.py
coverage report
```

### Passo 3: Expandir para outros módulos
```bash
pytest tests/test_hrm_implemented.py -v
pytest tests/test_work_security_implemented.py -v
```

### Passo 4: Medir cobertura total
```bash
coverage run -m pytest tests/ -v
coverage report --skip-covered
coverage html
```

---

## 📝 Estrutura de Testes

```
tests/
├── conftest.py                          # Setup pytest + Django + fixtures
├── test_hrm_implemented.py              # 28 testes HRM
├── test_work_security_implemented.py    # 35 testes Work/Security
├── test_config_settings.py              # 42 testes Config
├── test_coverage_improvement.py         # 121 stubs (framework)
└── __init__.py

root/
├── test_summary.py                      # Script resumo
├── TEST_IMPLEMENTATION_STATUS.md        # Status completo
├── QUICK_TEST_SETUP.md                  # Este arquivo
└── COVERAGE_IMPROVEMENT_GUIDE.md        # Estratégia detalhada
```

---

## ✅ Checklist Execução

- [ ] 1. Instalou pytest? `pip install pytest`
- [ ] 2. Instalou pytest-django? `pip install pytest-django`
- [ ] 3. Instalou coverage? `pip install coverage`
- [ ] 4. Rodou `python test_summary.py`?
- [ ] 5. Viu 105 testes listados?
- [ ] 6. Rodou `pytest tests/ -v`?
- [ ] 7. Todos os testes passaram?
- [ ] 8. Rodou `coverage report`?
- [ ] 9. Viu cobertura (esperada 65-70%)?
- [ ] 10. Gerou `coverage html`?

---

## 🚀 Executar Agora (Cópia/Cola)

### Para usuários Linux/macOS:
```bash
pip install pytest pytest-django coverage faker && \
python test_summary.py && \
pytest tests/ -v
```

### Para usuários Windows (PowerShell):
```powershell
pip install pytest pytest-django coverage faker; `
python test_summary.py; `
pytest tests/ -v
```

---

## 📞 Dúvidas Frequentes

**P: Por que usar SQLite e não PostgreSQL?**  
R: SQLite é mais rápido para desenvolvimento e não precisa de servidor. PostgreSQL é para produção.

**P: Quanto tempo levam os testes?**  
R: ~5-10 segundos para 105 testes (SQLite em memória)

**P: Posso rodar testes enquanto desenvolvendo?**  
R: Sim! Use `pytest-watch` ou `pytest --looponfail`

**P: Como adicionar novos testes?**  
R: Veja COVERAGE_IMPROVEMENT_GUIDE.md para exemplos

**P: Preciso de todas as dependências?**  
R: Não. Mínimo é: pytest, pytest-django, coverage

---

**Status**: ✅ 105 testes implementados e prontos para rodar  
**Última atualização**: 2024  
**Próximo milestone**: Atingir 75% de cobertura total
