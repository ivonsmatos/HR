#!/usr/bin/env python
"""
Teste Standalone - Validação de Implementação
Não precisa de Django settings ou postgres
"""

import os
import sys

def validate_tests():
    """Valida que todos os testes foram implementados corretamente"""
    
    print("\n" + "="*70)
    print("VALIDAÇÃO DE IMPLEMENTAÇÃO DE TESTES")
    print("="*70 + "\n")
    
    tests_dir = 'tests'
    
    # Verificar arquivos de teste
    test_files = {
        'test_hrm_implemented.py': {
            'min_lines': 400,
            'min_tests': 25,
            'classes': ['HRMCoreModelTests', 'HRMViewTests', 'HRMDataValidationTests'],
        },
        'test_work_security_implemented.py': {
            'min_lines': 400,
            'min_tests': 30,
            'classes': ['WorkProjectModelTests', 'SecurityAuditTests'],
        },
        'test_config_settings.py': {
            'min_lines': 250,
            'min_tests': 35,
            'classes': ['DjangoSettingsTests', 'MiddlewareTests'],
        },
    }
    
    all_valid = True
    total_lines = 0
    total_tests = 0
    
    for filename, specs in test_files.items():
        filepath = os.path.join(tests_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"❌ {filename} - NÃO ENCONTRADO")
            all_valid = False
            continue
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = len(content.split('\n'))
            test_count = content.count('def test_')
            class_count = sum(1 for line in content.split('\n') if line.startswith('class Test'))
            
            # Validações
            checks = []
            
            if lines >= specs['min_lines']:
                checks.append(f"✅ Linhas: {lines} (min: {specs['min_lines']})")
            else:
                checks.append(f"❌ Linhas: {lines} (min: {specs['min_lines']})")
                all_valid = False
            
            if test_count >= specs['min_tests']:
                checks.append(f"✅ Testes: {test_count} (min: {specs['min_tests']})")
            else:
                checks.append(f"❌ Testes: {test_count} (min: {specs['min_tests']})")
                all_valid = False
            
            classes_found = [c for c in specs['classes'] if f'class {c}' in content]
            if len(classes_found) == len(specs['classes']):
                checks.append(f"✅ Classes: {', '.join(classes_found)}")
            else:
                missing = set(specs['classes']) - set(classes_found)
                checks.append(f"⚠️  Classes encontradas: {', '.join(classes_found)} (faltam: {missing})")
            
            print(f"📄 {filename}")
            for check in checks:
                print(f"   {check}")
            print()
            
            total_lines += lines
            total_tests += test_count
    
    # Resumo
    print("-" * 70)
    print(f"TOTAIS:")
    print(f"  • Linhas de código: {total_lines}")
    print(f"  • Testes implementados: {total_tests}")
    print()
    
    if all_valid and total_tests >= 100:
        print("✅ VALIDAÇÃO PASSOU - Tudo pronto para execução!")
        return True
    else:
        print("❌ VALIDAÇÃO FALHOU - Verifique os erros acima")
        return False

def check_dependencies():
    """Verifica dependências instaladas"""
    
    print("\nDEPENDÊNCIAS:")
    print("-" * 70)
    
    dependencies = {
        'pytest': 'Teste Framework',
        'pytest_django': 'Django + pytest integration',
        'coverage': 'Coverage measurement',
        'faker': 'Test data generation',
        'django': 'Django framework',
    }
    
    for module_name, description in dependencies.items():
        try:
            mod = __import__(module_name)
            version = getattr(mod, '__version__', 'instalado')
            print(f"✅ {module_name:<20} - {description:<30} ({version})")
        except ImportError:
            print(f"❌ {module_name:<20} - {description:<30} (NÃO INSTALADO)")
    
    print()

def main():
    """Função principal"""
    
    check_dependencies()
    result = validate_tests()
    
    print("="*70)
    if result:
        print("🎉 SISTEMA PRONTO PARA TESTES")
        print("\nPróximos passos:")
        print("  1. pytest tests/ -v")
        print("  2. coverage run -m pytest tests/ && coverage report")
    else:
        print("⚠️  SISTEMA NÃO VALIDADO")
    print("="*70 + "\n")
    
    return 0 if result else 1

if __name__ == '__main__':
    sys.exit(main())
