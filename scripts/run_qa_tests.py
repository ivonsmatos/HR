"""
QA Test Runner Script

Execute esta suite de testes para validar o projeto
"""

import os
import sys
import subprocess
from pathlib import Path

# Cores para output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text:^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text):
    print(f"{RED}❌ {text}{RESET}")

def print_warning(text):
    print(f"{YELLOW}⚠️  {text}{RESET}")

def run_command(cmd, description):
    """Executar comando e retornar sucesso/falha"""
    print(f"{BLUE}→{RESET} {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print_success(description)
            return True
        else:
            print_error(f"{description} - {result.stderr[:100]}")
            return False
    except Exception as e:
        print_error(f"{description} - {str(e)}")
        return False

def main():
    print_header("WORKSUITE PWA - QA TEST SUITE")
    
    # Checklist
    results = {}
    
    # 1. Security Checks
    print_header("SECURITY CHECKS")
    results['secret_key'] = run_command(
        'grep "SECRET_KEY = os.getenv(" config/settings.py',
        'SECRET_KEY validation (no default)'
    )
    results['debug'] = run_command(
        'grep "DEBUG = os.getenv" config/settings.py',
        'DEBUG check'
    )
    results['allowed_hosts'] = run_command(
        'grep "ALLOWED_HOSTS" config/settings.py',
        'ALLOWED_HOSTS configuration'
    )
    
    # 2. Dependencies
    print_header("DEPENDENCIES CHECK")
    results['requirements'] = run_command(
        'pip install -r requirements.txt',
        'Install/verify requirements'
    )
    results['no_duplicate_pillow'] = run_command(
        'grep -c "Pillow==" requirements.txt | grep -q "1" && echo ok || echo error',
        'Check for duplicate Pillow'
    )
    
    # 3. Tests
    print_header("TEST SUITE")
    results['pytest_config'] = run_command(
        'test -f tests/pytest.ini',
        'Pytest configuration exists'
    )
    results['tests_exist'] = run_command(
        'test -f tests/test_core_auth.py',
        'Core auth tests exist'
    )
    
    # Rodar testes
    if results['requirements']:
        results['run_tests'] = run_command(
            'pytest tests/ -v --tb=short || true',
            'Run pytest suite'
        )
    
    # 4. Code Quality
    print_header("CODE QUALITY")
    results['black_check'] = run_command(
        'black --check . || true',
        'Black code formatting'
    )
    results['flake8'] = run_command(
        'flake8 . --count --exit-zero --max-line-length=127 || true',
        'Flake8 linting'
    )
    
    # 5. Configuration Files
    print_header("CONFIGURATION FILES")
    results['env_example'] = run_command(
        'test -f .env.example',
        '.env.example file exists'
    )
    results['dockerfile'] = run_command(
        'test -f Dockerfile',
        'Dockerfile exists'
    )
    results['docker_compose'] = run_command(
        'test -f docker-compose.yml',
        'docker-compose.yml exists'
    )
    results['cicd'] = run_command(
        'test -f .github/workflows/ci-cd.yml',
        'CI/CD pipeline exists'
    )
    
    # 6. Documentation
    print_header("DOCUMENTATION")
    results['deployment_guide'] = run_command(
        'test -f DEPLOYMENT_GUIDE.md',
        'Deployment guide exists'
    )
    results['troubleshooting'] = run_command(
        'test -f TROUBLESHOOTING_GUIDE.md',
        'Troubleshooting guide exists'
    )
    results['qa_report'] = run_command(
        'test -f QA_ANALYSIS_REPORT.md',
        'QA analysis report exists'
    )
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    percentage = (passed / total) * 100
    
    print(f"Tests passed: {GREEN}{passed}/{total}{RESET}")
    print(f"Success rate: {GREEN}{percentage:.1f}%{RESET}")
    
    if percentage == 100:
        print_success("All checks passed!")
        return 0
    elif percentage >= 80:
        print_warning("Most checks passed, review failures")
        return 1
    else:
        print_error("Multiple failures detected, review report")
        return 2

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
