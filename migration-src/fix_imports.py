#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix import statements to use proper module paths
"""
import os
import re

# Modules that should be imported from application
APPLICATION_MODULES = [
    'config',
    'messageManager',
    'timemanager',
    'wordstocker',
    'setting'
]

def fix_imports_in_file(filepath):
    """Fix import statements in a single file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    modified = False

    for module in APPLICATION_MODULES:
        # Pattern: import module (at start of line)
        pattern = f'^import {module}$'
        replacement = f'from application import {module}'

        new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        if new_content != content:
            modified = True
            content = new_content
            print(f"  Fixed: import {module} -> from application import {module}")

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
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
                print(f"Checking: {filepath}")
                if fix_imports_in_file(filepath):
                    fixed_count += 1

    print(f"\nFixed {fixed_count} files")

if __name__ == '__main__':
    main()
