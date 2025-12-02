#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix remaining import statements in application directory
"""
import os
import re

# Modules that exist in application/ and should be imported with application. prefix
APP_MODULES = [
    'bksearchutl', 'bksearchensenutl', 'bklistutl', 'GqlEncoder',
    'wordstocker', 'messageManager', 'SecurePageBase', 'SecurePage',
    'session', 'timemanager', 'config', 'chkauth', 'qreki',
    'rotor', 'CriticalSection', 'zipper', 'tantochangetasks',
    'mailvalidation', 'blobstoreutl', 'email_decoder'
]

def fix_file(filepath):
    """Fix imports in a single file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    modified = False
    new_lines = []

    for line in lines:
        new_line = line

        # Pattern: import module (where module is in APP_MODULES)
        for module in APP_MODULES:
            if re.match(rf'^import {module}$', line.strip()):
                new_line = line.replace(f'import {module}', f'from application import {module}')
                modified = True
                print(f"  Fixed: {line.strip()} -> {new_line.strip()}")
                break

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
                if fix_file(filepath):
                    fixed_count += 1

    print(f"\n\nTotal fixed: {fixed_count} files")

if __name__ == '__main__':
    main()
