#!/usr/bin/env python
"""
Remove domain references from test files
"""
import re
import os

test_files = [
    'tests/test_hrm_implemented.py',
    'tests/test_work_security_implemented.py',
]

for file_path in test_files:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove domain=... from Company.objects.create() calls
        # Match: domain="..." or domain='...' with optional comma
        content = re.sub(r',?\s*domain=["\'][^"\']*["\']\s*(?=[,)])', '', content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f'✓ Removed domain references from: {file_path}')

print("\n✅ Done!")
