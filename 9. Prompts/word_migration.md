# Word Migration Steps

## Quick Reference

**Migration Script:** `9. Prompts/migrate_words.py`
```bash
python3 "9. Prompts/migrate_words.py" <word_list> <target_file> <sr_date>
# Example:
python3 "9. Prompts/migrate_words.py" /tmp/new_a_words.txt "3. English/Vocabulary/a.md" "2025-11-15"
```

**Verification Script:** `9. Prompts/verify_migration.py`
```bash
python3 "9. Prompts/verify_migration.py" <target_file> <sr_date> <expected_count>
# Example:
python3 "9. Prompts/verify_migration.py" "3. English/Vocabulary/a.md" "2025-11-15" 120
```

## Overview
Migrate vocabulary words from source directory to Obsidian Vault alphabetical files.

## Step-by-Step Process

### 1. Get User Input
- Ask for source directory (e.g., `/home/genext/Downloads/markdown-export/export_words`)
- target directory is `/home/genext/Documents/Obsidian Vault/3. English/Vocabulary`
- Ask for which letter to migrate (e.g., 'a', 'c', 'd')
- Ask for spaced repetition date (e.g., `2025-11-05`)

### 2. Identify Source Files
- Find all markdown files starting with the specified letter in source directory
- Example: `find [source] -name "c*.md" -o -name "C*.md" | sort`

### 3. Extract Media References
- Read each source markdown file
- Parse and identify:
  - Audio files: `![](@media/filename.mp3)` or `![](filename.mp3)`
  - Image files: `![](@media/filename.jpg)` or `![](filename.png)`

### 4. Copy Media Files
- Copy audio files to: `[target_vault]/100. media/audio/`
- Copy image files to: `[target_vault]/100. media/image/`
- Example: `cp file1.mp3 file2.mp3 ... "/path/to/100. media/audio/"`

### 5. Convert Format

**Use the migration script:** `9. Prompts/migrate_words.py`

Transform from source format to Obsidian format:

**Source format:**
```markdown
word![](file.mp3)![](file2.mp3)
---
definition text
![Alt text](@media/image.jpg)
example sentence![](@media/audio.mp3)
---
```

**Target format:**
```markdown
word ![[100. media/audio/file.mp3]] ![[100. media/audio/file2.mp3]]
?
definition text
![[100. media/image/image.jpg|200]]
example sentence![[100. media/audio/audio.mp3]]
<!--SR:!2025-11-05,1,230-->
-
```

**Conversion rules:**
- Add space after word name
- Remove `---` separator lines
- Add `?` on line 2 for flashcard format
- Convert audio links: `![](@media/file.mp3)` → `![[100. media/audio/file.mp3]]`
- Convert audio links: `![](file.mp3)` → `![[100. media/audio/file.mp3]]`
- Convert image links: `![Alt](@media/file.jpg)` → `![[100. media/image/file.jpg|200]]`
- Convert image links: `![Alt](file.png)` → `![[100. media/image/file.png|200]]`
- Add spaced repetition tag: `<!--SR:!2025-11-05,1,230-->`
- Add separator: `-`
- Remove trailing spaces from lines

### 6. Append to Target File
- Determine target alphabetical file based on first letter (e.g., 'c' → `c.md`)
- Insert converted entry **before** the final `#Vocabulary` tag
- Each word entry separated by blank line

### 7. Verify Results

#### 7.1 Basic Verification
- Count entries with new SR date matches expected count
- All media files copied successfully to correct directories
- No file copy errors reported

#### 7.2 Structure Verification
For each migrated entry, verify:
- **Word line**: Starts with word name + audio files in `![[100. media/audio/...]]` format
- **Question mark**: Second line is exactly `?`
- **Definition**: Third line onwards contains definition and examples
- **Media links**: All converted to Obsidian format
  - Audio: `![[100. media/audio/filename.mp3]]`
  - Images: `![[100. media/image/filename.jpg|200]]`
- **SR tag**: Contains `<!--SR:![EXPECTED_DATE],1,230-->`
- **Separator**: Ends with `-` on its own line
- **Blank line**: Followed by blank line before next entry

#### 7.3 Content Verification
Sample 5-10 random entries and verify:
- Compare with source file
- All text content preserved (definitions, examples, Korean text, etymology, synonyms)
- All media files referenced
- No missing content
- No extra content added
- Proper spacing and formatting maintained

#### 7.4 Automated Verification Script

**Use the verification script:** `9. Prompts/verify_migration.py`

Usage:
```bash
python3 "9. Prompts/verify_migration.py" "3. English/Vocabulary/a.md" "2025-11-15" 120
```

The script checks:
- Entry count matches expected
- All entries have word line starting with lowercase letter
- All entries have '?' marker on line 2
- All entries have SR tag with correct date
- All entries have separator '-'
- Reports detailed issues if found

#### 7.5 Manual Spot Checks
- Open target file in Obsidian
- Verify at least 3-5 entries render correctly
- Check that flashcards work with spaced repetition plugin
- Verify media files play/display correctly
- Confirm no duplicate entries created

## Example Migration

**Source:** `canonical.md`
```markdown
canonical![4F7147D6065A97021A.mp3](DHED2Mzg.mp3)![4F71218F0624DF0204.mp3](CCtbzCKn.mp3)
---
according to canon law 교회법으로 정해진
That's the canonical example![speech.mp3](5VCy1xAG.mp3)
---
```

**Target:** Added to `c.md`
```markdown
canonical ![[100. media/audio/DHED2Mzg.mp3]] ![[100. media/audio/CCtbzCKn.mp3]]
?
according to canon law 교회법으로 정해진
That's the canonical example![[100. media/audio/5VCy1xAG.mp3]]
<!--SR:!2025-11-05,1,230-->
-
```

## Format Variations

Source files may have different formats. Handle these variations:

### File Structure Variations

**IMPORTANT**: Some markdown files have **reversed structure** where definition comes FIRST and title comes LAST:

**Standard Structure:**
```markdown
word![](file.mp3)
---
definition text
---
```

**Reversed Structure:**
```markdown
definition text
---
word![](file.mp3)
```

When encountering reversed structure:
1. Identify the word name (usually on the last line)
2. Extract all content above the last `---`
3. Rebuild in standard format: word name → ? → definition content

### Title Line Variations
- **With audio only:** `word![](file.mp3)![](file2.mp3)`
- **Without audio:** `word` (no audio files on title line)
- **Mixed formats:** `word![4F7147D6065A97021A.mp3](DHED2Mzg.mp3)` (ID in alt text)
- **Reversed file:** Word name appears at the END of file instead of beginning

### Definition Section Variations
- **With image:** Definition text followed by `![Alt](@media/image.jpg)`
- **Without image:** Only definition text, no image files
- **Multiple images:** Some entries may have multiple images

### Audio Placement Variations
- **In title:** Audio files on first line with word name
- **In examples:** Audio files inline with example sentences
- **Standalone:** Audio files on their own lines

### General Rules for Variations
- **Always preserve:** All text content, Korean translations, etymology, synonyms
- **Handle missing media:** If no image, skip image conversion
- **Handle extra media:** Convert all audio/image files found
- **Preserve structure:** Keep paragraph breaks and formatting

## Notes
- Spaced repetition format: `<!--SR:![DATE],1,230-->`
  - DATE: User-specified date (e.g., `2025-11-05`)
  - Interval: `1` (fixed)
  - Ease: `230` (fixed)
- Image width modifier: `|200` (always add to image links)
- Always maintain blank lines between entries
- Preserve all content including Korean translations and etymology
- Audio files may appear anywhere in source - convert all occurrences
- Images may or may not be present - only convert if they exist
