#!/usr/bin/env python3
"""
Migration Verification Script
Verifies that migrated vocabulary entries have correct structure.

Usage:
    python3 verify_migration.py <target_file> <sr_date> <expected_count>

Example:
    python3 verify_migration.py "3. English/Vocabulary/a.md" "2025-11-15" 120
"""

import re
import sys
import os


def verify_migration(file_path, sr_date, expected_count=None):
    """Verify migrated entries have correct structure"""

    if not os.path.exists(file_path):
        print(f"ERROR: File not found: {file_path}")
        return False

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all entries with the migration SR date
    # Pattern captures from word line through SR tag and separator
    pattern = rf'(^[a-z][^\n]*?\n.*?<!--SR:!{sr_date},1,230-->\n-)'
    entries = re.findall(pattern, content, re.MULTILINE | re.DOTALL)

    print(f"Verification for SR date: {sr_date}")
    print(f"=" * 60)

    if expected_count:
        print(f"Expected entries: {expected_count}")
    print(f"Found entries: {len(entries)}\n")

    if expected_count and len(entries) != expected_count:
        print(f"⚠️  WARNING: Entry count mismatch!")
        print(f"   Expected {expected_count}, found {len(entries)}\n")

    issues = []
    valid = 0

    for i, entry in enumerate(entries, 1):
        lines = entry.strip().split('\n')

        # Check structure
        has_word_line = lines[0] and re.match(r'^[a-z]', lines[0])
        has_question_mark = len(lines) > 1 and lines[1].strip() == '?'
        has_sr_tag = any('<!--SR:!' in line for line in lines)
        has_separator = any(line.strip() == '-' for line in lines)

        if not has_word_line:
            issues.append(f"Entry {i}: Missing word line")
            print(f"❌ Entry {i}: Missing word line")
            print(f"   First line: {lines[0][:80]}")
            print()
            continue

        if not has_question_mark:
            issues.append(f"Entry {i}: Missing ? marker")
            print(f"❌ Entry {i}: Missing '?' marker")
            print(f"   Word: {lines[0][:60]}")
            print()
            continue

        if not has_sr_tag:
            issues.append(f"Entry {i}: Missing SR tag")
            print(f"❌ Entry {i}: Missing SR tag")
            print(f"   Word: {lines[0][:60]}")
            print()
            continue

        if not has_separator:
            issues.append(f"Entry {i}: Missing separator '-'")
            print(f"❌ Entry {i}: Missing separator")
            print(f"   Word: {lines[0][:60]}")
            print()
            continue

        valid += 1

    print("=" * 60)
    print(f"Summary:")
    print(f"  Total entries: {len(entries)}")
    print(f"  ✓ Valid: {valid}")
    print(f"  ✗ Issues: {len(issues)}")

    if len(issues) == 0:
        print(f"\n✅ SUCCESS: All entries have correct structure!")
        return True
    else:
        print(f"\n❌ FAILED: Found {len(issues)} structural issues")
        if len(issues) > 10:
            print(f"\nShowing first 10 issues:")
            for issue in issues[:10]:
                print(f"  - {issue}")
            print(f"  ... and {len(issues) - 10} more")
        else:
            print(f"\nIssues:")
            for issue in issues:
                print(f"  - {issue}")
        return False


def main():
    if len(sys.argv) < 3:
        print("Usage: verify_migration.py <file_path> <sr_date> [expected_count]")
        print("\nExample:")
        print('  python3 verify_migration.py "3. English/Vocabulary/a.md" "2025-11-15" 120')
        sys.exit(1)

    file_path = sys.argv[1]
    sr_date = sys.argv[2]
    expected_count = int(sys.argv[3]) if len(sys.argv) > 3 else None

    # Make file_path absolute if relative
    if not os.path.isabs(file_path):
        vault_dir = "/home/genext/Documents/Obsidian Vault"
        file_path = os.path.join(vault_dir, file_path)

    success = verify_migration(file_path, sr_date, expected_count)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
