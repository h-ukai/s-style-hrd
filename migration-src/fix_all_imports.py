#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix all import statements to use proper module paths
"""
import os
import re

def fix_imports_in_file(filepath):
    """Fix import statements in a single file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    modified = False
    new_lines = []

    for line in lines:
        new_line = line

        # Pattern 1: from models. -> from application.models.
        if re.match(r'^from models\.', line):
            new_line = line.replace('from models.', 'from application.models.')
            modified = True
            print(f"  Fixed: {line.strip()} -> {new_line.strip()}")

        # Pattern 2: from models import -> from application.models import
        elif re.match(r'^from models import', line):
            new_line = line.replace('from models import', 'from application.models import')
            modified = True
            print(f"  Fixed: {line.strip()} -> {new_line.strip()}")

        # Pattern 3: from XXX import where XXX is an application module
        elif re.match(r'^from (bklistutl|GqlEncoder|wordstocker|messageManager|SecurePageBase|session|timemanager) import', line):
            match = re.match(r'^from (\w+) import', line)
            if match:
                module = match.group(1)
                new_line = line.replace(f'from {module} import', f'from application.{module} import')
                modified = True
                print(f"  Fixed: {line.strip()} -> {new_line.strip()}")

        new_lines.append(new_line)

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        return True
    return False

def main():
    """Main function"""
    app_dir = 'application'
    fixed_count = 0

    for root, dirs, files in os.walk(app_dir):
        for filename in files:
            if filename.endswith('.py'):
                filepath = os.path.join(root, filename)
                print(f"\nChecking: {filepath}")
                if fix_imports_in_file(filepath):
                    fixed_count += 1

    print(f"\n\nTotal fixed: {fixed_count} files")

if __name__ == '__main__':
    main()
