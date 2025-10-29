#!/usr/bin/env python3
import os
import sys
import re
import typing
from datetime import datetime

def is_word_section(text: str) -> bool:
    # Word section typically has only one newline (1 or none)
    # Definition section typically has multiple lines (2+ newlines)
    newline_count = text.count('\n')

    # If more than 1 newline, it's likely a definition section
    if newline_count > 1:
        return False

    # Word section can start with:
    # - Letters (a-z, A-Z)
    # - Plus signs (++) for pronunciation markers
    # - Minus/hyphen (-) for suffixes/prefixes
    # - Numbers (0-9) for phrases like "4 hour shift"
    # - Backslash (\) for escaped characters like "\-"
    # - Asterisk (*) for markdown bold/italic like "**word**"
    pattern = r'^[\+\-\*\\0-9a-z]'
    return bool(re.match(pattern, text, re.IGNORECASE))

def normalize_file(filepath: str, error_log: list) -> str:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by separator
    filename = os.path.basename(filepath)

    if '---' not in content:
        error_msg = "No separator (---) found"
        print(f"Warning: {error_msg} in {filename}")
        error_log.append({"filename": filename, "problem": error_msg})
        return 'error'

    parts = content.split('---', 1)
    if len(parts) != 2:
        error_msg = "Incorrect separator format (expected exactly one ---)"
        print(f"Warning: {error_msg} in {filename}")
        error_log.append({"filename": filename, "problem": error_msg})
        return 'error'
    
    part1 = parts[0].strip()
    part2 = parts[1].strip()
    
    part1_is_word = is_word_section(part1)
    part2_is_word = is_word_section(part2)

    if part1_is_word:
        return 'skipped'
    elif part2_is_word:
        normalized = f"{part2}\n---\n{part1}\n"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(normalized)
        return 'converted'
    else:
        error_msg = "Could not determine format (ambiguous: neither section matches word pattern)"
        print(f"Warning: {error_msg} for {filename}")
        error_log.append({"filename": filename, "problem": error_msg})
        return 'error'



def main():
    if len(sys.argv) < 2:
        print("Usage: normalize_format.py <source_directory>")
        print("\nExample:")
        print('  python3 normalize_format.py "/home/genext/Downloads/markdown-export/English"')
        sys.exit(1)

    source_dir = sys.argv[1]

    if not os.path.isdir(source_dir):
        print(f"Error: Directory not found: {source_dir}")
        sys.exit(1)

    print(f"Normalizing markdown files in: {source_dir}\n")

    converted_count = 0
    skipped_count = 0
    error_count = 0
    total_count = 0
    error_log = []

    for filename in os.listdir(source_dir):
        if filename.endswith('.md'):
            if not filename.isascii():
                continue

            total_count += 1
            filepath = os.path.join(source_dir, filename)
            result = normalize_file(filepath, error_log)
            if result == 'converted':
                converted_count += 1
            elif result == 'skipped':
                skipped_count += 1
            elif result == "error":
                error_count += 1

    print(f"\n{'='*60}")
    print(f"Total files processed: {total_count} (Korean filenames excluded)")
    print(f"Converted (reversed → standard): {converted_count} files")
    print(f"Skipped (already standard): {skipped_count} files")
    print(f"Error files: {error_count} files")
    print(f"{'='*60}")

    # Save error log to file
    if error_log:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"normalize_errors_{timestamp}.log"
        log_path = os.path.join(os.getcwd(), log_filename)

        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(f"Normalize Format Error Log\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Source Directory: {source_dir}\n")
            f.write(f"{'='*80}\n\n")

            for i, error in enumerate(error_log, 1):
                f.write(f"{i}. {error['filename']}\n")
                f.write(f"   Problem: {error['problem']}\n\n")

        print(f"\n✅ Error log saved to: {log_path}")
        print(f"   Total errors logged: {len(error_log)}")


if __name__ == "__main__":
    main()