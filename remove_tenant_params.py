#!/usr/bin/env python
"""
Script para remover parâmetro 'tenant=' dos User.objects.create_user() calls nos testes
"""

import os
import re

test_files = [
    'tests/test_hrm_implemented.py',
    'tests/test_work_security_implemented.py',
    'tests/test_coverage_improvement.py',
]

def remove_tenant_param(file_path):
    """Remove tenant= parameter from User.objects.create_user() calls"""
    if not os.path.exists(file_path):
        return f"✗ File not found: {file_path}"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to find and remove tenant parameter
    # Matches: tenant=..., on a line
    pattern = r',?\s*tenant\s*=\s*[^\)]*'
    
    # Also remove .tenant references in assertions
    new_content = re.sub(pattern, '', content)
    new_content = re.sub(r'\.tenant', '', new_content)
    new_content = re.sub(r'self\.tenant', 'self.company', new_content)
    
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return f"✓ Updated: {file_path}"
    else:
        return f"- No changes: {file_path}"

# Process all test files
print("Removing 'tenant=' parameters from test files...\n")
for test_file in test_files:
    result = remove_tenant_param(test_file)
    print(result)

print("\n✅ Done! Tenant parameters removed.")
