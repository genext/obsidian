# Word Migration Steps

## Quick Reference

**Working Directory:** `/tmp/vocab_migration/` (always work here first!)

**Setup:**
```bash
mkdir -p /tmp/vocab_migration
cp "3. English/Vocabulary/a.md" /tmp/vocab_migration/a.md
```

**Normalization Script:** `9. Prompts/normalize_format.py`
```bash
python3 "9. Prompts/normalize_format.py" <source_directory>
# Example:
python3 "9. Prompts/normalize_format.py" "/home/genext/Downloads/markdown-export/English"
```

**Migration Script:** `9. Prompts/migrate_words.py`
```bash
python3 "9. Prompts/migrate_words.py" <word_list> <working_file> <sr_date>
# Example (note: output to /tmp/vocab_migration/):
python3 "9. Prompts/migrate_words.py" /tmp/new_a_words.txt /tmp/vocab_migration/a.md "2025-11-15"
```

**Verification Script:** `9. Prompts/verify_migration.py`
```bash
python3 "9. Prompts/verify_migration.py" <working_file> <sr_date> <expected_count>
# Example (note: verify /tmp/vocab_migration/ file):
python3 "9. Prompts/verify_migration.py" /tmp/vocab_migration/a.md "2025-11-15" 120
```

**Deploy to Production (after confirmation):**
```bash
cp /tmp/vocab_migration/a.md "3. English/Vocabulary/a.md"
```

## Overview
Migrate vocabulary words from source directory to Obsidian Vault alphabetical files. When there is a problem in migration, stop working and show which word or markdown file caused the issue. After I check, I will let you know what to do.



## Working Directory Strategy

**IMPORTANT**: Always work in a designated working directory, never directly modify production files.

**Working Directory:** `/tmp/vocab_migration/`

**Workflow:**
1. Copy target file (e.g., `a.md`) from vault to working directory
2. Run all migration operations on the working directory copy
3. Review and verify results in working directory
4. **After user confirmation**, copy final result back to vault

**Example for letter 'a':**
```bash
# 1. Setup working directory
mkdir -p /tmp/vocab_migration
cp "3. English/Vocabulary/a.md" /tmp/vocab_migration/a.md

# 2. Run migration (output to working directory)
python3 "9. Prompts/migrate_words.py" /tmp/new_a_words.txt /tmp/vocab_migration/a.md "2025-11-15"

# 3. Review results
cat /tmp/vocab_migration/a.md | less

# 4. After confirmation, copy to production
cp /tmp/vocab_migration/a.md "3. English/Vocabulary/a.md"
```

**Benefits:**
- Safe: Production files never modified until confirmed
- Reversible: Can restart without losing original data
- Verifiable: Review working copy before deployment
- Clean: Easy to cleanup and restart if issues found

## Step-by-Step Process

### 1. Setup Working Directory
```bash
# Create working directory
mkdir -p /tmp/vocab_migration

# Copy target file to working directory
LETTER="a"  # Change as needed
cp "3. English/Vocabulary/${LETTER}.md" "/tmp/vocab_migration/${LETTER}.md"
```

### 2. Get User Input
- Ask for source directory (e.g., `/home/genext/Downloads/markdown-export/English`)
- Working directory: `/tmp/vocab_migration/`
- Target directory (final): `/home/genext/Documents/Obsidian Vault/3. English/Vocabulary`
- Ask for which letter to migrate (e.g., 'a', 'c', 'd')
- Ask for spaced repetition date (e.g., `2025-11-05`)

### 3. Identify Source Files
- Find all markdown files starting with the specified letter in source directory
- **IMPORTANT**: Exclude files with Korean titles (non-ASCII characters in filenames)
  - Korean filename files are out of scope for English vocabulary migration
  - Only process files with English/ASCII characters in the filename
  - Both scripts (`normalize_format.py` and `migrate_words.py`) automatically skip non-ASCII filenames
- Example:
  ```bash
  # Find all c*.md files, excluding Korean filenames
  find [source] -name "c*.md" -o -name "C*.md" | grep -v '[^[:ascii:]]' | sort
  ```

### 4. Extract Media References
- Read each source markdown file
- Parse and identify:
  - Audio files: `![](@media/filename.mp3)` or `![](filename.mp3)`
  - Image files: `![](@media/filename.jpg)` or `![](filename.png)`

### 5. Pre-Process Source Files (Normalize Format)

**CRITICAL STEP**: Some source files have **reversed format** where definition comes first and word comes last. These MUST be converted to standard format BEFORE running the migration script.

**Detection Method:**
- Split file content by `---` separator
- Check which section matches the word section pattern:
  - Starts with a word (lowercase letters, may include `++` markers)
  - Followed by media links `![](...)` with or without space
  - Pattern: `^[a-z][a-z\s+]*!?\[?\]?\(`
- The section matching this pattern is the word section
- The other section is the definition section

**Standard Format (Target):**
```markdown
word![](file.mp3)
---
definition text
```

**Reversed Format (Needs Conversion):**
```markdown
definition text (much longer)
---
word![](file.mp3)
```

**Pre-Processing Script:** `9. Prompts/normalize_format.py`

This script detects reversed format files by pattern matching (not by length) and converts them to standard format.

**Pattern Detection:**
- Word section: Starts with lowercase word + media links `![](...)`
- Pattern: `^[a-z][a-z\s+]*!?\[?\]?\(`
- Examples: `word![](file.mp3)`, `word ![](file.mp3)`, `abbr++e++viate![](file.mp3)`

**Run Pre-Processing:**
```bash
python3 "9. Prompts/normalize_format.py" "/home/genext/Downloads/markdown-export/English"
```

**Output:**
- Shows each converted file
- Reports total converted vs skipped files
- Warns about ambiguous files that couldn't be determined

**Why This Step is Critical:**
- The migration script expects standard format (word first, definition second)
- Reversed files will cause incorrect extraction of word names and definitions
- Pre-processing ensures consistent input format for the migration script
- Prevents content corruption and missing data

### 6. Copy Media Files
- Copy audio files to: `[target_vault]/100. media/audio/`
- Copy image files to: `[target_vault]/100. media/image/`
- Example: `cp file1.mp3 file2.mp3 ... "/path/to/100. media/audio/"`

### 7. Convert Format

**Use the migration script:** `9. Prompts/migrate_words.py`

**IMPORTANT:** Output to working directory, not production directory!

```bash
python3 "9. Prompts/migrate_words.py" /tmp/new_a_words.txt /tmp/vocab_migration/a.md "2025-11-15"
```

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
- Remove pronunciation markers: `++letter++` → `letter` (e.g., `abbr++e++viate` → `abbreviate`)
- Remove `---` separator lines
- Add `?` on line 2 for flashcard format
- Convert audio links: `![](@media/file.mp3)` → `![[100. media/audio/file.mp3]]`
- Convert audio links: `![](file.mp3)` → `![[100. media/audio/file.mp3]]`
- Convert image links: `![Alt](@media/file.jpg)` → `![[100. media/image/file.jpg|200]]`
- Convert image links: `![Alt](file.png)` → `![[100. media/image/file.png|200]]`
- Add spaced repetition tag: `<!--SR:!2025-11-05,1,230-->`
- Add separator: `-`
- Remove trailing spaces from lines

### 8. Append to Working File
- The migration script appends to the working directory file
- Entries inserted **before** the final `#Vocabulary` tag
- Each word entry separated by blank line

### 9. Verify Results in Working Directory

**Review working directory file before copying to production!**

```bash
# Quick review
cat /tmp/vocab_migration/a.md | less

# Count new entries
grep -c "2025-11-15" /tmp/vocab_migration/a.md

# Spot check random entries
grep -A 10 "^word_name" /tmp/vocab_migration/a.md
```

#### 9.1 Basic Verification
- Count entries with new SR date matches expected count
- All media files copied successfully to correct directories
- No file copy errors reported

#### 9.2 Structure Verification
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

#### 9.3 Content Verification
Sample 5-10 random entries and verify:
- Compare with source file
- All text content preserved (definitions, examples, Korean text, etymology, synonyms)
- All media files referenced
- No missing content
- No extra content added
- Proper spacing and formatting maintained

#### 9.4 Automated Verification Script

**Use the verification script:** `9. Prompts/verify_migration.py`

**Run on working directory file:**
```bash
python3 "9. Prompts/verify_migration.py" /tmp/vocab_migration/a.md "2025-11-15" 120
```

The script checks:
- Entry count matches expected
- All entries have word line starting with lowercase letter
- All entries have '?' marker on line 2
- All entries have SR tag with correct date
- All entries have separator '-'
- Reports detailed issues if found

#### 9.5 Manual Spot Checks
- Open working directory file in text editor
- Verify at least 3-5 entries render correctly
- Check formatting and media links
- Confirm no duplicate entries created

### 10. Deploy to Production (After User Confirmation)

**CRITICAL:** Only copy to production after user confirms verification is successful!

```bash
# Backup current production file (optional but recommended)
cp "3. English/Vocabulary/a.md" "3. English/Vocabulary/a.md.backup.$(date +%Y%m%d_%H%M%S)"

# Copy verified working file to production
cp /tmp/vocab_migration/a.md "3. English/Vocabulary/a.md"

echo "✅ Deployed to production!"
```

### 11. Final Validation in Obsidian
- Open production file in Obsidian
- Verify at least 3-5 entries render correctly
- Check that flashcards work with spaced repetition plugin
- Verify media files play/display correctly
- Test spaced repetition plugin functionality

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

**IMPORTANT**: Some markdown files have **reversed structure** where definition comes FIRST and title comes LAST.

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

**NOTE**: Reversed format files should be converted to standard format in **Step 4 (Pre-Process Source Files)** BEFORE running the migration script. This ensures the migration script always receives consistent input format

### Word Section Variations
- **Single line with audio:** `word![](file.mp3)![](file2.mp3)`
- **Multi-line with audio:**
  ```
  word
  ![](file1.mp3)![](file2.mp3)
  ```
- **Without audio:** `word` (no audio files in word section)
- **With pronunciation markers:** `abbr++e++viate` → convert to `abbr**e**viate` (change `++` to `**` for emphasis)
- **Phrases:** `account for something` (preserve entire phrase)
- **Mixed formats:** `word![4F7147D6065A97021A.mp3](DHED2Mzg.mp3)` (ID in alt text)

**IMPORTANT**: The word section is identified as the **shorter part** when content is split by `---`. Extract ALL media files from the ENTIRE word section, not just the first line.

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
