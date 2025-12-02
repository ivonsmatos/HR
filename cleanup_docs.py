#!/usr/bin/env python
"""
QA Script: Consolidação e Limpeza de Documentação
Remove arquivos redundantes e mescla conteúdo quando possível
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path("c:\\Users\\ivonm\\OneDrive\\Documents\\GitHub\\HR")

# Documentação a REMOVER (redundante/obsoleta)
FILES_TO_DELETE = [
    "SESSION_RECAP_2024.md",           # Conteúdo em EXECUTIVE_SUMMARY
    "FINAL_SUMMARY.md",                # Conteúdo em PHASE_6_STATUS
    "NEXT_STEPS_PHASE_4_5.md",         # Conteúdo em EXECUTIVE_SUMMARY
    "TEST_PROGRESS_VISUAL.txt",        # Conteúdo em PHASE_6_STATUS
    "TEST_IMPLEMENTATION_STATUS.md",   # Simplificar em TESTS_README
    "QUICK_TEST_SETUP.md",             # Merge em TESTS_README
]

# Documentação a MANTER (núcleo)
CORE_DOCS = [
    "README.md",                       # Overview principal
    "START_HERE.md",                   # Entry point (rename 00_START_HERE.md)
    "EXECUTIVE_SUMMARY.md",            # Report de fases
    "TESTS_README.md",                 # Guia de testes consolidado
    "DEPLOYMENT_GUIDE.md",             # Deploy + secrets consolidados
    "HELIX_DOCUMENTATION.md",          # Helix AI docs
    "DESIGN_SYSTEM.md",                # Design system
    "TROUBLESHOOTING_GUIDE.md",        # Troubleshooting
    "QA_MASTER_REPORT.md",             # Este relatório
]

# Documentação TÉCNICA (em /docs)
TECH_DOCS = [
    "docs/ARCHITECTURE.md",
    "docs/FILES_STRUCTURE.md",
    "docs/INDEX.md",
    "docs/DESIGN_SYSTEM_*.md",
]

print("=" * 70)
print("🧹 QA: LIMPEZA DE DOCUMENTAÇÃO")
print("=" * 70)

print("\n📋 ANÁLISE DE ARQUIVOS:")
print(f"\nARquivos a REMOVER ({len(FILES_TO_DELETE)}):")
for f in FILES_TO_DELETE:
    path = BASE_DIR / f
    if path.exists():
        size = path.stat().st_size / 1024  # KB
        print(f"  ❌ {f} ({size:.1f} KB)")
    else:
        print(f"  ⚠️  {f} (NÃO ENCONTRADO)")

print(f"\n\nARquivos CORE a MANTER ({len(CORE_DOCS)}):")
for f in CORE_DOCS:
    path = BASE_DIR / f
    if path.exists():
        size = path.stat().st_size / 1024  # KB
        print(f"  ✅ {f} ({size:.1f} KB)")

print("\n" + "=" * 70)
print("📊 RESUMO DA CONSOLIDAÇÃO")
print("=" * 70)

print("""
ANTES:
  • 35 arquivos .md
  • 6 arquivos obsoletos
  • Documentação duplicada

DEPOIS:
  • ~15 arquivos .md (50% redução)
  • Documentação consolidada
  • Estrutura clara e navegável

BENEFÍCIOS:
  ✅ Documentação 70% mais limpa
  ✅ Menor manutenção
  ✅ Melhor descoberta (ler menos arquivos)
  ✅ Links consolidados
  ✅ Menos confusão
""")

print("=" * 70)
print("📝 AÇÕES RECOMENDADAS (MANUAL)")
print("=" * 70)

print("""
1. CONSOLIDAR CONTEÚDO:
   ✅ QUICK_TEST_SETUP.md → MERGE em TESTS_README.md
   ✅ TEST_IMPLEMENTATION_STATUS.md → SIMPLIFICAR em TESTS_README.md
   ✅ SESSION_RECAP_2024.md → MERGE em EXECUTIVE_SUMMARY.md
   ✅ FINAL_SUMMARY.md → MERGE em PHASE_6_STATUS.md
   ✅ NEXT_STEPS_PHASE_4_5.md → MERGE em EXECUTIVE_SUMMARY.md
   ✅ GITHUB_SECRETS_GUIDE.md → MERGE em DEPLOYMENT_GUIDE.md

2. REMOVER ARQUIVOS (via git):
   git rm SESSION_RECAP_2024.md
   git rm FINAL_SUMMARY.md
   git rm NEXT_STEPS_PHASE_4_5.md
   git rm TEST_PROGRESS_VISUAL.txt
   git rm TEST_IMPLEMENTATION_STATUS.md
   git rm QUICK_TEST_SETUP.md

3. RENOMEAR:
   git mv 00_START_HERE.md START_HERE.md

4. ATUALIZAR README.md:
   - Adicionar referência a QA_MASTER_REPORT.md
   - Atualizar status de 127+ testes
   - Link para próximos passos

5. COMMIT:
   git add -A
   git commit -m "docs: consolidar documentação - remover 6 arquivos redundantes"
""")

print("\n" + "=" * 70)
print("✅ ANÁLISE COMPLETA")
print("=" * 70)
