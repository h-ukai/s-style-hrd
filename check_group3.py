#!/usr/bin/env python3
"""Check which Group 3 files are in the original document."""

from pathlib import Path

md_file = Path(r"C:\Users\hrsuk\prj\s-style-hrd\migration-progress.md")
content = md_file.read_text(encoding='utf-8')

# Group 3 files
group3_files = [
    'application/addresslist.py',
    'application/show.py',
    'application/mailinglist.py',
    'application/SecurePageBase.py',
    'application/GqlEncoder.py',
    'application/uploadaddressset.py',
    'application/memberSearchandMail.py',
    'application/bksearchutl.py',
]

print("Checking Group 3 files in original document:")
found_count = 0
for fname in group3_files:
    pattern = f"### ✅ {fname}"
    if pattern in content:
        print(f"  FOUND: {fname}")
        found_count += 1
    else:
        print(f"  MISSING: {fname}")

print(f"\nTotal found: {found_count}/8")
