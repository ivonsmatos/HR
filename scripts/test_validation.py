#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MASTER TEST VALIDATION SCRIPT - Consolidates all test utilities

This script replaces:
- validate_tests.py
- validate_helix.py
- test_summary.py
- test_helix_quick.py
- run_basic_tests.py
- fix_pytest_decorators.py

Usage:
    python scripts/test_validation.py validate all       # Validate all tests
    python scripts/test_validation.py summary            # Test implementation summary
    python scripts/test_validation.py coverage           # Coverage report
    python scripts/test_validation.py run                # Run all tests
"""

import os
import sys
import subprocess

class TestValidator:
    def __init__(self):
        self.tests_dir = 'tests'
        self.test_files = [
            'test_core_auth.py',
            'test_api_endpoints.py',
            'test_config_settings.py',
            'test_hrm_implemented.py',
            'test_work_security_implemented.py',
            'test_work_extended.py',
            'test_helix_assistant.py',
            'test_extended_integration.py',
            'test_e2e_critical_flows.py',
            'test_coverage_improvement.py',
        ]
    
    def validate_all(self):
        """Validate all test implementations"""
        print("\n" + "="*70)
        print("VALIDAÇÃO COMPLETA DE TESTES")
        print("="*70 + "\n")
        
        all_valid = True
        total_lines = 0
        total_tests = 0
        
        for test_file in self.test_files:
            filepath = os.path.join(self.tests_dir, test_file)
            
            if not os.path.exists(filepath):
                print(f"❌ {test_file} - NÃO ENCONTRADO")
                all_valid = False
                continue
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = len(content.split('\n'))
                test_methods = content.count('def test_')
                imports = content.count('import ')
                classes = content.count('class Test')
                
                total_lines += lines
                total_tests += test_methods
                
                print(f"✅ {test_file}")
                print(f"   • Linhas: {lines}")
                print(f"   • Testes (def test_*): {test_methods}")
                print(f"   • Classes: {classes}")
                print(f"   • Imports: {imports}\n")
        
        print("="*70)
        print(f"📊 RESUMO TOTAL")
        print(f"   • Linhas totais: {total_lines}")
        print(f"   • Testes totais: {total_tests}")
        print(f"   • Arquivos: {len(self.test_files)}")
        print(f"   • Status: {'✅ VÁLIDO' if all_valid else '❌ INVÁLIDO'}")
        print("="*70 + "\n")
    
    def test_summary(self):
        """Print test implementation summary"""
        print("\n" + "="*70)
        print("RESUMO DE IMPLEMENTAÇÃO DE TESTES")
        print("="*70 + "\n")
        
        created_files = []
        missing_files = []
        total_lines = 0
        total_tests = 0
        
        for test_file in self.test_files:
            filepath = os.path.join(self.tests_dir, test_file)
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = len(content.split('\n'))
                    test_methods = content.count('def test_')
                    
                    created_files.append((test_file, lines, test_methods))
                    total_lines += lines
                    total_tests += test_methods
                    
                    print(f"✅ {test_file}")
                    print(f"   • Linhas: {lines}")
                    print(f"   • Testes: {test_methods}\n")
            else:
                missing_files.append(test_file)
                print(f"❌ {test_file} - NÃO ENCONTRADO\n")
        
        print("="*70)
        print(f"📊 TOTAL")
        print(f"   • Linhas: {total_lines}")
        print(f"   • Testes: {total_tests}")
        print(f"   • Arquivos criados: {len(created_files)}")
        print(f"   • Arquivos faltantes: {len(missing_files)}")
        print("="*70 + "\n")
    
    def coverage_report(self):
        """Generate coverage report"""
        print("\n" + "="*70)
        print("RELATÓRIO DE COBERTURA")
        print("="*70 + "\n")
        
        try:
            result = subprocess.run(
                ['pytest', '--cov=apps', '--cov-report=term-missing', '-v'],
                capture_output=True,
                text=True
            )
            print(result.stdout)
            if result.stderr:
                print("ERROS:", result.stderr)
        except Exception as e:
            print(f"❌ Erro ao executar pytest: {e}")
            print("   Certifique-se que pytest está instalado")
    
    def run_tests(self):
        """Run all tests"""
        print("\n" + "="*70)
        print("EXECUTANDO TESTES")
        print("="*70 + "\n")
        
        try:
            result = subprocess.run(
                ['pytest', 'tests/', '-v', '--tb=short'],
                capture_output=True,
                text=True
            )
            print(result.stdout)
            if result.returncode != 0:
                print("ERROS:", result.stderr)
            return result.returncode
        except Exception as e:
            print(f"❌ Erro ao executar testes: {e}")
            return 1

def main():
    validator = TestValidator()
    
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'validate':
        validator.validate_all()
    elif command == 'summary':
        validator.test_summary()
    elif command == 'coverage':
        validator.coverage_report()
    elif command == 'run':
        return validator.run_tests()
    else:
        print(f"Comando desconhecido: {command}")
        print(__doc__)

if __name__ == '__main__':
    sys.exit(main() or 0)
