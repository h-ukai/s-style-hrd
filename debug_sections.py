#!/usr/bin/env python3
"""Debug script to check which sections are found."""

from pathlib import Path

# Read the original file
md_file = Path(r"C:\Users\hrsuk\prj\s-style-hrd\migration-progress.md")
content = md_file.read_text(encoding='utf-8')

# Parse sections by filename
sections = {}
current_file = None
current_section = []
lines = content.split('\n')

for i, line in enumerate(lines):
    if line.startswith('### ✅ '):
        # Save previous section
        if current_file:
            sections[current_file] = '\n'.join(current_section)

        # Extract filename
        current_file = line.replace('### ✅ ', '').strip()
        current_section = [line]
    elif line.startswith('### ') and '✅' not in line and current_file:
        # End of section (new category)
        sections[current_file] = '\n'.join(current_section)
        current_file = None
        current_section = []
    elif current_file:
        current_section.append(line)

if current_file:
    sections[current_file] = '\n'.join(current_section)

print("Found sections:")
for key in sorted(sections.keys()):
    print(f"  - {key}")

# Check for specific files
test_files = [
    'application/proc.py',
    'application/models/bkdata.py',
    'application/models/bklist.py',
    'application/models/blob.py',
    'application/bklistutl.py',
    'geo/geomodel.py',
]

print("\nSearch results:")
for fname in test_files:
    if fname in sections:
        print(f"  ✓ {fname}")
    else:
        print(f"  ✗ {fname}")
