#!/usr/bin/env python
"""
Script para adicionar @pytest.mark.django_db a todas as classes de teste
que herdam de django.test.TestCase ou APITestCase
"""

import os
import re

test_files = [
    'tests/test_config_settings.py',
    'tests/test_hrm_implemented.py',
    'tests/test_work_security_implemented.py',
    'tests/test_work_extended.py',
    'tests/test_helix_assistant.py',
    'tests/test_extended_integration.py',
    'tests/test_multi_tenancy.py',
    'tests/test_helix_e2e.py',
    'tests/test_e2e_critical_flows.py',
]

def fix_test_file(file_path):
    """Adiciona @pytest.mark.django_db a classes de teste"""
    if not os.path.exists(file_path):
        return f"✗ File not found: {file_path}"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Check if pytest is already imported
    has_pytest_import = any('import pytest' in line for line in lines)
    
    # Find where to add import (after other imports)
    import_end_idx = 0
    for i, line in enumerate(lines):
        if line.startswith(('from', 'import')) and not line.startswith('import pytest'):
            import_end_idx = i + 1
    
    # Add pytest import if not present
    if not has_pytest_import and import_end_idx > 0:
        lines.insert(import_end_idx, 'import pytest\n')
    
    # Now add decorators to class definitions
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check if this is a class definition inheriting from TestCase or APITestCase
        if re.match(r'^class\s+\w+\(.*(?:TestCase|APITestCase)\s*.*\):', line):
            # Check if previous line is already a pytest decorator
            if new_lines and '@pytest.mark' in new_lines[-1]:
                new_lines.append(line)
            else:
                new_lines.append('@pytest.mark.django_db\n')
                new_lines.append(line)
        else:
            new_lines.append(line)
        
        i += 1
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    return f"✓ Updated: {file_path}"

# Process all test files
print("Adding @pytest.mark.django_db to test classes...\n")
for test_file in test_files:
    result = fix_test_file(test_file)
    print(result)

print("\n✅ Done! All test classes decorated.")
