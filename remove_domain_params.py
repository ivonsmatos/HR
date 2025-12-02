#!/usr/bin/env python
"""
Script para remover parâmetro 'domain' dos Company.objects.create() nos testes
O campo 'domain' agora é uma relação inversa de CompanyDomain, não um campo direto
"""

import os
import re

test_files = [
    'tests/test_config_settings.py',
    'tests/test_hrm_implemented.py',
    'tests/test_work_security_implemented.py',
    'tests/test_work_extended.py',
    'tests/test_extended_integration.py',
    'tests/test_multi_tenancy.py',
    'tests/test_coverage_improvement.py',
]

def remove_domain_parameter(file_path):
    """Remove domain= parameter from Company.objects.create() calls"""
    if not os.path.exists(file_path):
        return f"✗ File not found: {file_path}"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to find and remove domain parameter in Company.objects.create()
    # Matches: domain="something.local", or domain='something.local', or domain=...
    pattern = r',?\s*domain\s*=\s*["\']?[^,\)]*["\']?'
    new_content = re.sub(pattern, '', content)
    
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return f"✓ Updated: {file_path}"
    else:
        return f"- No changes: {file_path}"

# Process all test files
print("Removing 'domain=' parameters from test files...\n")
for test_file in test_files:
    result = remove_domain_parameter(test_file)
    print(result)

print("\n✅ Done! Domain parameters removed from Company.objects.create() calls.")
