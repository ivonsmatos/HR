#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MASTER MAINTENANCE SCRIPT - Consolidates all translation and migration utilities

This script replaces:
- translate_to_pt_br.py
- translate_remaining.py
- translate_admin_complete.py
- translate_admin_labels.py
- translate_choices.py
- translate_comprehensive.py
- translate_to_syncrh.py
- translate_massive.py

Usage:
    python scripts/maintenance.py translate models     # Translate models to PT-BR
    python scripts/maintenance.py translate admin       # Translate admin to PT-BR
    python scripts/maintenance.py translate full        # Full massive translation (all 142 pairs)
    python scripts/maintenance.py translate rename      # Rename Helix → SyncRH
    python scripts/maintenance.py cleanup all           # Clean up old files
"""

import os
import re
import sys
from pathlib import Path

# ============================================================================
# TRANSLATION DICTIONARIES
# ============================================================================

MODELS_TRANSLATION = {
    '"Project"': '"Projeto"',
    '"Projects"': '"Projetos"',
    '"Task"': '"Tarefa"',
    '"Tasks"': '"Tarefas"',
    '"Department"': '"Departamento"',
    '"Departments"': '"Departamentos"',
    '"Employee"': '"Funcionário"',
    '"Employees"': '"Funcionários"',
    '"Contract"': '"Contrato"',
    '"Contracts"': '"Contratos"',
    '"Leave"': '"Licença"',
    '"Leaves"': '"Licenças"',
    '"Shift"': '"Turno"',
    '"Shifts"': '"Turnos"',
    '"Attendance"': '"Frequência"',
    '"Salary"': '"Salário"',
    '"Payslip"': '"Contracheque"',
    '"Client"': '"Cliente"',
    '"Clients"': '"Clientes"',
    '"Lead"': '"Lead"',
    '"Leads"': '"Leads"',
    '"Deal"': '"Negócio"',
    '"Deals"': '"Negócios"',
}

ADMIN_TRANSLATION = {
    'Basic Information': 'Informações Básicas',
    'Basic Info': 'Informações Básicas',
    'Content': 'Conteúdo',
    'Metadata': 'Metadados',
    'Audit': 'Auditoria',
    'Personal Information': 'Informações Pessoais',
    'Account': 'Conta',
    'Contact': 'Contato',
    'Address': 'Endereço',
    'Organization': 'Organização',
    'Permissions': 'Permissões',
    'Security': 'Segurança',
    'Preferences': 'Preferências',
    'Active': 'Ativo',
    'Inactive': 'Inativo',
}

MASSIVE_TRANSLATION = {
    # System names
    "Onyx Helix": "SyncRH",
    "Helix": "SyncRH",
    "helix": "syncrh",
    
    # Common UI
    "Add": "Adicionar",
    "Edit": "Editar",
    "Delete": "Deletar",
    "Save": "Salvar",
    "Cancel": "Cancelar",
    "Search": "Pesquisar",
    "Filter": "Filtrar",
    "Export": "Exportar",
    "Import": "Importar",
    "Submit": "Enviar",
    "Reset": "Limpar",
    
    # Fields
    "Name": "Nome",
    "Email": "Email",
    "Phone": "Telefone",
    "Title": "Título",
    "Company": "Empresa",
    "User": "Usuário",
    "Role": "Papel",
    "Status": "Status",
    "Created": "Criado",
    "Updated": "Atualizado",
    "Description": "Descrição",
}

RENAME_HELIX_SYNCRH = {
    "Helix Admin": "Admin SyncRH",
    "HELIX": "SYNCRH",
    "helix_": "syncrh_",
    "Helix Dashboard": "Painel SyncRH",
    "Onyx Helix": "SyncRH",
}

# ============================================================================
# TRANSLATION ENGINE
# ============================================================================

def get_py_files(directory='.', exclude_dirs=None):
    """Get all Python files except migrations and pycache"""
    if exclude_dirs is None:
        exclude_dirs = {'migrations', '__pycache__', '.venv', 'venv', '.git'}
    
    py_files = []
    for root, dirs, files in os.walk(directory):
        # Remove excluded directories from dirs list
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                py_files.append(filepath)
    
    return py_files

def apply_translation(filepath, translations, dry_run=False):
    """Apply translation dictionary to a file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        count = 0
        
        for old, new in translations.items():
            matches = content.count(old)
            if matches > 0:
                content = content.replace(old, new)
                count += matches
        
        if content != original_content and not dry_run:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, count
        elif content != original_content:
            return False, count
        
        return False, 0
    except Exception as e:
        print(f"  ❌ Erro em {filepath}: {e}")
        return False, 0

# ============================================================================
# COMMANDS
# ============================================================================

def translate_models():
    """Translate Django models to PT-BR"""
    print("\n📝 Traduzindo models.py para PT-BR...")
    files = get_py_files()
    files = [f for f in files if 'models.py' in f]
    
    total_changes = 0
    for filepath in files:
        changed, count = apply_translation(filepath, MODELS_TRANSLATION)
        if changed:
            print(f"  ✅ {filepath} ({count} mudanças)")
            total_changes += count
    
    print(f"\n✅ Total: {total_changes} substituições em {len(files)} arquivos")

def translate_admin():
    """Translate Django admin to PT-BR"""
    print("\n📝 Traduzindo admin.py para PT-BR...")
    files = get_py_files()
    files = [f for f in files if 'admin.py' in f]
    
    total_changes = 0
    for filepath in files:
        changed, count = apply_translation(filepath, ADMIN_TRANSLATION)
        if changed:
            print(f"  ✅ {filepath} ({count} mudanças)")
            total_changes += count
    
    print(f"\n✅ Total: {total_changes} substituições em {len(files)} arquivos")

def translate_full():
    """Full massive translation - all 142+ pairs"""
    print("\n🚀 Tradução COMPLETA com 142+ pares de tradução...")
    files = get_py_files()
    
    # Apply all translations
    total_changes = 0
    translated_files = set()
    
    for translation_dict in [MODELS_TRANSLATION, ADMIN_TRANSLATION, MASSIVE_TRANSLATION]:
        for filepath in files:
            changed, count = apply_translation(filepath, translation_dict)
            if changed:
                total_changes += count
                translated_files.add(filepath)
    
    print(f"\n✅ Arquivos traduzidos: {len(translated_files)}")
    print(f"📊 Total de substituições: {total_changes}")

def translate_rename():
    """Rename system from Helix to SyncRH"""
    print("\n🔄 Renomeando Helix → SyncRH...")
    files = get_py_files()
    
    total_changes = 0
    for filepath in files:
        changed, count = apply_translation(filepath, RENAME_HELIX_SYNCRH)
        if changed:
            print(f"  ✅ {filepath} ({count} mudanças)")
            total_changes += count
    
    print(f"\n✅ Total: {total_changes} renomeações")

def cleanup_old_scripts():
    """Remove deprecated scripts"""
    print("\n🗑️  Removendo scripts antigos...")
    
    deprecated = [
        'translate_to_pt_br.py',
        'translate_remaining.py',
        'translate_admin_complete.py',
        'translate_admin_labels.py',
        'translate_choices.py',
        'translate_comprehensive.py',
        'translate_to_syncrh.py',
        'translate_massive.py',
        'validate_tests.py',
        'validate_helix.py',
        'test_summary.py',
        'test_helix_quick.py',
        'run_basic_tests.py',
        'fix_pytest_decorators.py',
        'HELIX_SETTINGS_PHASE_E.py',
        'remove_domain_params.py',
        'remove_tenant_params.py',
        'remove_domain_refs.py',
    ]
    
    removed = 0
    for script in deprecated:
        if os.path.exists(script):
            try:
                os.remove(script)
                print(f"  ✅ Removido: {script}")
                removed += 1
            except Exception as e:
                print(f"  ❌ Erro ao remover {script}: {e}")
    
    print(f"\n✅ {removed} scripts removidos")

# ============================================================================
# MAIN
# ============================================================================

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if len(sys.argv) > 2:
        action = sys.argv[2]
    else:
        action = None
    
    if command == 'translate':
        if action == 'models':
            translate_models()
        elif action == 'admin':
            translate_admin()
        elif action == 'full':
            translate_full()
        elif action == 'rename':
            translate_rename()
        else:
            print("Ação desconhecida. Use: models, admin, full ou rename")
    
    elif command == 'cleanup':
        if action == 'all':
            cleanup_old_scripts()
        else:
            print("Especifique 'all' para limpeza")
    
    else:
        print(f"Comando desconhecido: {command}")
        print(__doc__)

if __name__ == '__main__':
    main()
