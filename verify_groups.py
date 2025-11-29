#!/usr/bin/env python3
"""Verify group files."""

from pathlib import Path

base_dir = Path(r"C:\Users\hrsuk\prj\s-style-hrd")

print("=" * 60)
print("Migration Progress Group Files Verification")
print("=" * 60)

total_files_created = 0
total_bytes = 0

for i in range(1, 11):
    file_path = base_dir / f"migration-progress-group-{i}.md"
    if file_path.exists():
        size = file_path.stat().st_size
        lines = file_path.read_text(encoding='utf-8').count('\n')
        content = file_path.read_text(encoding='utf-8')
        sections = content.count('### ✅')

        # Count group-specific sections (after "## Group N Specific Sections")
        group_specific_marker = f"## Group {i} Specific Sections"
        if group_specific_marker in content:
            group_part = content.split(group_specific_marker)[1]
            group_sections = group_part.count('### ✅')
        else:
            group_sections = 0

        print(f"\nGroup {i}:")
        print(f"  File: migration-progress-group-{i}.md")
        print(f"  Size: {size:,} bytes")
        print(f"  Lines: {lines}")
        print(f"  Total sections: {sections}")
        print(f"  Group-specific sections: {group_sections}")

        total_files_created += 1
        total_bytes += size
    else:
        print(f"\nGroup {i}: NOT FOUND")

print("\n" + "=" * 60)
print(f"Summary:")
print(f"  Total files created: {total_files_created}")
print(f"  Total size: {total_bytes:,} bytes ({total_bytes / 1024:.1f} KB)")
print("=" * 60)
