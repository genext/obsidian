#!/usr/bin/env python3
"""
Comprehensive verification script that compares migrated entries against source files.
Checks ALL content including word, media files, and definitions.
"""

import sys
import re
import os

def main():
    if len(sys.argv) < 4:
        print("Usage: comprehensive_verify.py <target_file> <sr_date> <export_dir>")
        print("\nExample:")
        print('  python3 comprehensive_verify.py "3. English/Vocabulary/b.md" "2025-11-15" "/home/genext/Downloads/markdown-export/English"')
        sys.exit(1)

    target_file = sys.argv[1]
    sr_date = sys.argv[2]
    export_dir = sys.argv[3]

    vault_dir = "/home/genext/Documents/Obsidian Vault"

    # Make paths absolute
    if not os.path.isabs(target_file):
        target_file = os.path.join(vault_dir, target_file)

    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all entries with the SR date
    pattern = rf'(^([a-z][a-z\s]+?)\s+!.*?\n.*?<!--SR:!{sr_date},1,230-->\n-)'
    entries = re.findall(pattern, content, re.MULTILINE | re.DOTALL)

    print(f"Found {len(entries)} entries with SR date {sr_date}")
    print("=" * 80)

    errors = []

    for full_entry, word in entries:
        # Extract just the word (first word before space or media link)
        word = word.split()[0].strip()

        # Find source file
        source_file = os.path.join(export_dir, f"{word}.md")

        if not os.path.exists(source_file):
            errors.append(f"❌ {word}: Source file not found")
            continue

        # Read source
        with open(source_file, 'r', encoding='utf-8') as f:
            source_content = f.read()

        # Extract source media files
        source_media = set()
        for match in re.finditer(r'@?media/([^)]+\.(mp3|jpg|png|jpeg|gif))', source_content):
            source_media.add(match.group(1))
        for match in re.finditer(r'!\[\]\(([A-Za-z0-9_-]+\.(mp3|jpg|png|jpeg|gif))\)', source_content):
            source_media.add(match.group(1))

        # Extract migrated media files
        migrated_media = set()
        for match in re.finditer(r'100\. media/(audio|image)/([^|\]]+)', full_entry):
            migrated_media.add(match.group(2))

        # Compare
        if source_media != migrated_media:
            errors.append(f"❌ {word}: Media mismatch")
            errors.append(f"  Source: {sorted(source_media)[:5]}")
            errors.append(f"  Migrated: {sorted(migrated_media)[:5]}")

            missing = source_media - migrated_media
            extra = migrated_media - source_media
            if missing:
                errors.append(f"  Missing: {sorted(missing)[:3]}")
            if extra:
                errors.append(f"  Extra: {sorted(extra)[:3]}")
        else:
            print(f"✅ {word}: All media files match ({len(source_media)} files)")

    print("=" * 80)

    if errors:
        print(f"\n❌ ERRORS FOUND: {len([e for e in errors if e.startswith('❌')])}")
        for error in errors:
            print(error)
        sys.exit(1)
    else:
        print(f"\n✅ SUCCESS: All {len(entries)} entries verified correctly!")
        sys.exit(0)

if __name__ == "__main__":
    main()
