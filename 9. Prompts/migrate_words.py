#!/usr/bin/env python3
"""
Word Migration Script
Migrates vocabulary words from source directory to Obsidian Vault alphabetical files.

Usage:
    python3 migrate_words.py <word_list_file> <target_md_file> <sr_date>

Example:
    python3 migrate_words.py /tmp/new_a_words.txt "3. English/Vocabulary/a.md" "2025-11-15"
"""

import os
import re
import sys
import shutil


def extract_word_from_filename(filename):
    """Remove ++x++ markers from filename"""
    return re.sub(r'\+\+[a-z]\+\+', '', filename.replace('.md', ''))


def find_source_file(export_dir, word):
    """Find source file for word, handling ++x++ markers"""
    # Try exact match first
    exact = os.path.join(export_dir, f"{word}.md")
    if os.path.exists(exact):
        return exact

    # Try with markers
    for f in os.listdir(export_dir):
        if f.endswith('.md'):
            extracted = extract_word_from_filename(f)
            if extracted == word:
                return os.path.join(export_dir, f)
    return None


def convert_media_link(text):
    """Convert media links to Obsidian format"""
    # ![](@media/file.mp3) -> ![[100. media/audio/file.mp3]]
    text = re.sub(r'!\[\]\(@media/([^)]+\.mp3)\)', r'![[100. media/audio/\1]]', text)
    # ![](file.mp3) -> ![[100. media/audio/file.mp3]]
    text = re.sub(r'!\[\]\(([^)]+\.mp3)\)', r'![[100. media/audio/\1]]', text)
    # ![Alt](@media/file.jpg) -> ![[100. media/image/file.jpg|200]]
    text = re.sub(r'!\[[^\]]*\]\(@media/([^)]+\.(jpg|png|jpeg|gif))\)', r'![[100. media/image/\1|200]]', text)
    # ![](file.jpg) -> ![[100. media/image/file.jpg|200]]
    text = re.sub(r'!\[\]\(([^)]+\.(jpg|png|jpeg|gif))\)', r'![[100. media/image/\1|200]]', text)
    return text


def process_word(export_dir, word, sr_date):
    """Process a single word file and return converted entry + media files"""
    source_file = find_source_file(export_dir, word)
    if not source_file:
        print(f"  WARNING: File not found for '{word}'")
        return None, []

    with open(source_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    if not lines:
        return None, []

    content = ''.join(lines)
    first_line = lines[0].strip()
    last_line = lines[-1].strip()

    media_files = []

    # Detect structure (standard or reversed)
    if re.match(r'^[a-z]', first_line) and '![]' in first_line:
        # Standard structure: word on first line
        word_line = first_line
        # Get content between --- markers
        parts = content.split('---')
        if len(parts) >= 2:
            definition_content = parts[1].strip()
        else:
            definition_content = '\n'.join(lines[1:]).strip()
    else:
        # Reversed structure: word on last line
        word_line = last_line
        # Get content before last ---
        parts = content.split('---')
        if len(parts) >= 2:
            definition_content = parts[0].strip()
        else:
            definition_content = '\n'.join(lines[:-1]).strip()

    # Extract audio files from word line
    # Handle both ![]() and ![ID]() formats
    converted_word = word
    for match in re.finditer(r'!\[[^\]]*\]\((@?media/)?([^)]+\.mp3)\)', word_line):
        audio_file = match.group(2)
        converted_word += f" ![[100. media/audio/{audio_file}]]"
        media_files.append(audio_file)

    # Extract and convert media from definition
    for match in re.finditer(r'@?media/([^)]+\.(mp3|jpg|png|jpeg|gif))', definition_content):
        media_files.append(match.group(1))

    # Also check for direct filenames
    for match in re.finditer(r'!\[\]\(([A-Za-z0-9_-]+\.(mp3|jpg|png|jpeg|gif))\)', definition_content):
        media_files.append(match.group(1))

    # Convert definition media links
    converted_def = convert_media_link(definition_content)

    # Remove trailing spaces from each line
    converted_def = '\n'.join(line.rstrip() for line in converted_def.split('\n'))

    # Build entry
    entry = f"{converted_word}\n?\n{converted_def}\n<!--SR:!{sr_date},1,230-->\n-\n\n"

    return entry, media_files


def main():
    if len(sys.argv) < 4:
        print("Usage: migrate_words.py <word_list> <target_file> <sr_date>")
        print("\nExample:")
        print('  python3 migrate_words.py /tmp/words.txt "3. English/Vocabulary/a.md" "2025-11-15"')
        sys.exit(1)

    word_list_file = sys.argv[1]
    target_file = sys.argv[2]
    sr_date = sys.argv[3]

    export_dir = "/home/genext/Downloads/markdown-export/English"
    vault_dir = "/home/genext/Documents/Obsidian Vault"
    audio_dir = os.path.join(vault_dir, "100. media", "audio")
    image_dir = os.path.join(vault_dir, "100. media", "image")

    # Make target_file absolute if relative
    if not os.path.isabs(target_file):
        target_file = os.path.join(vault_dir, target_file)

    print(f"Starting migration...")
    print(f"Source: {export_dir}")
    print(f"Target: {target_file}")
    print(f"SR Date: {sr_date}\n")

    # Read word list
    with open(word_list_file, 'r') as f:
        words = [line.strip() for line in f if line.strip()]

    all_entries = []
    all_media = set()
    word_count = 0
    total_words = len(words)

    for word in words:
        word_count += 1
        print(f"[{word_count}/{total_words}] Processing: {word}")

        entry, media_files = process_word(export_dir, word, sr_date)
        if entry:
            all_entries.append(entry)
            all_media.update(media_files)

    print(f"\nCopying {len(all_media)} unique media files...")
    copied_count = 0
    for media_file in all_media:
        source = os.path.join(export_dir, media_file)
        if os.path.exists(source):
            if media_file.endswith('.mp3') or media_file.endswith('.wav'):
                dest = os.path.join(audio_dir, media_file)
            else:
                dest = os.path.join(image_dir, media_file)

            try:
                shutil.copy2(source, dest)
                copied_count += 1
            except Exception as e:
                print(f"  Error copying {media_file}: {e}")

    print(f"Copied {copied_count} media files!")

    print(f"\nAppending {len(all_entries)} entries to {target_file}...")

    # Read target file
    with open(target_file, 'r', encoding='utf-8') as f:
        target_content = f.read()

    # Find #Vocabulary tag
    if '\n#Vocabulary' in target_content:
        parts = target_content.split('\n#Vocabulary')
        new_content = parts[0] + '\n'.join(all_entries) + '\n#Vocabulary' + parts[1]
    else:
        new_content = target_content + '\n' + ''.join(all_entries)

    # Write back
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"\nMigration complete!")
    print(f"Migrated {word_count} words")
    print(f"\nRun verification:")
    print(f'  python3 verify_migration.py "{target_file}" "{sr_date}" {len(all_entries)}')


if __name__ == '__main__':
    main()
