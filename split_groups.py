#!/usr/bin/env python3
"""Split migration-progress.md into 10 group files."""

import re
from pathlib import Path

# Read the original file
md_file = Path(r"C:\Users\hrsuk\prj\s-style-hrd\migration-progress.md")
content = md_file.read_text(encoding='utf-8')

# グループ定義
groups = {
    1: [
        'application/proc.py',
        'application/bkedit.py',
        'application/blobstoreutl.py',
        'application/handler.py',
        'application/RemoveAll.py',
        'application/uploadbkdata.py',
        'application/uploadbkdataformaster.py',
        'application/duplicationcheck.py',
    ],
    2: [
        'application/json.py',
        'application/memberedit.py',
        'application/test.py',
        'application/bksearch.py',
        'application/follow.py',
        'application/mypage.py',
        'application/bkjoukyoulist.py',
        'application/bkdchk.py',
    ],
    3: [
        'application/addresslist.py',
        'application/show.py',
        'application/mailinglist.py',
        'application/SecurePageBase.py',
        'application/GqlEncoder.py',
        'application/uploadaddressset.py',
        'application/memberSearchandMail.py',
        'application/bksearchutl.py',
    ],
    4: [
        'application/cron.py',
        'application/sendmsg.py',
        'application/email_receiver.py',
        'application/matching.py',
        'application/messageManager.py',
        'application/tantochange.py',
    ],
    5: [
        'application/index.py',
        'application/models/member.py',
        'application/models/CorpOrg.py',
        'application/models/Branch.py',
        'application/session.py',
        'application/chkauth.py',
        'application/mapreducemapper.py',
    ],
    6: [
        'application/models/bkdata.py',
        'application/models/bklist.py',
        'application/models/blob.py',
        'application/bklistutl.py',
    ],
    7: [
        'application/view.py',
        'dataProvider/bkdataProvider.py',
        'application/timemanager.py',
        'application/wordstocker.py',
        'application/config.py',
    ],
    8: [
        'application/models/ziplist.py',
        'application/models/station.py',
        'application/models/message.py',
        'application/models/msgcombinator.py',
        'application/SecurePage.py',
        'application/models/bksearchaddress.py',
        'application/models/bksearchdata.py',
    ],
    9: [
        'application/models/bksearchmadori.py',
        'dataProvider/bkdataSearchProvider.py',
        'application/bksearchensenutl.py',
        'application/models/address.py',
        'application/zipper.py',
        'application/qreki.py',
        'application/mailvalidation.py',
        'application/models/matchingparam.py',
        'application/models/matchingdate.py',
    ],
    10: [
        'application/email_decoder.py',
        'application/CriticalSection.py',
        'application/rotor.py',
        'application/tantochangetasks.py',
        'geo/geomodel.py',
        'application/models/bksearchensen.py',
        'application/models/bksearcheki.py',
        'geo/geocell.py',
        'geo/geomath.py',
        'geo/geotypes.py',
        'geo/util.py',
    ],
}

# 共通ファイル
common_files = [
    'app.yaml',
    'main.py',
    'appengine_config.py',
    'setting.py',
    'autolistedindex.yaml',
    'backends.yaml',
    'corpzip.yaml',
    'cron.yaml',
    'dos.yaml',
    'index.yaml',
    'mapreduce.yaml',
    'queue.yaml',
    'application/login.py',
    'application/logout.py',
    'application/regist.py',
]

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

print(f"Total sections found: {len(sections)}")
print(f"Common files: {len(common_files)}")

# Extract common sections content
common_header = "# Migration Progress\n\n**Start time**: 2025-11-16 13:52:49\n**Total files**: 15\n\n"
common_sections_content = []

for fname in common_files:
    if fname in sections:
        common_sections_content.append(sections[fname])

# Create group files
for group_num in range(1, 11):
    group_files = groups[group_num]

    # Build content
    output = common_header
    output += f"## Migration Progress Group {group_num}\n\n"

    # Add common sections
    for content_section in common_sections_content:
        output += content_section + "\n\n"

    # Add group-specific sections
    output += f"## Group {group_num} Specific Sections\n\n"

    for fname in group_files:
        if fname in sections:
            output += sections[fname] + "\n\n"
        else:
            print(f"Warning: {fname} not found in sections")

    # Write to file
    output_file = md_file.parent / f"migration-progress-group-{group_num}.md"
    output_file.write_text(output, encoding='utf-8')
    print(f"Created: {output_file.name} ({len(output)} bytes)")

print("\nDone!")
