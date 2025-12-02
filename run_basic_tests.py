#!/usr/bin/env python
"""
Script simples para validar testes básicos sem Django complexity
Roda apenas testes que não dependem de models/migrations
"""

import sys
import os
import subprocess

# Testes básicos que devem funcionar com SQLite
BASIC_TESTS = [
    "tests/test_coverage_improvement.py",  # Não usa modelos
]

def run_test_file(test_file):
    """Roda um arquivo de teste individual"""
    print(f"\n{'='*70}")
    print(f"🧪 Testando: {test_file}")
    print(f"{'='*70}")
    
    cmd = [
        "pytest",
        test_file,
        "-v",
        "--tb=short",
        "-x",  # Stop on first error
    ]
    
    result = subprocess.run(cmd, cwd=os.getcwd())
    return result.returncode == 0

def main():
    """Main entry point"""
    os.chdir(".")
    
    print("\n" + "="*70)
    print("🚀 VALIDAÇÃO PROGRESSIVA DE TESTES")
    print("="*70)
    
    passed = 0
    failed = 0
    
    for test_file in BASIC_TESTS:
        if os.path.exists(test_file):
            if run_test_file(test_file):
                passed += 1
                print(f"✅ {test_file}: PASSOU")
            else:
                failed += 1
                print(f"❌ {test_file}: FALHOU")
        else:
            print(f"⚠️  {test_file}: NÃO ENCONTRADO")
    
    print("\n" + "="*70)
    print(f"📊 RESULTADO: {passed} passed, {failed} failed")
    print("="*70)
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
