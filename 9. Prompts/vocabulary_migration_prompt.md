# Vocabulary Migration Prompt Template

## Context
I have vocabulary files in a migration directory that need to be integrated into my Obsidian vault's alphabetical vocabulary files.

**Source Directory**: `[SPECIFY YOUR SOURCE DIRECTORY HERE]` (e.g., `/home/genext/Downloads/migration`)
**Target Directory**: `/home/genext/Documents/Obsidian Vault/3. English/Vocabulary`
**Media Directories**:
- Audio: `/home/genext/Documents/Obsidian Vault/100. media/audio`
- Images: `/home/genext/Documents/Obsidian Vault/100. media/image`

## Source File Format
Each vocabulary word in the migration directory has:
- Markdown file named `{word}.md`
- Audio files referenced with syntax: `![filename.mp3](shortcode.mp3)` or `![4F7152D7052A3A00CB.mp3](shortcode.mp3)`
- Image files referenced with syntax: `![image.png](shortcode.png)`
- Content separator: `---`
- Word on first line with audio references

Example source format:
```
apprise![4F7152D7052A3A00CB.mp3](lCnIMS8V.mp3)![4F712CCE0430B902CA.mp3](4ONup1lF.mp3)
---
![image.png](msgYOZd4.png)
formal to tell or give someone information about something SYN inform
(격식) 주로 상업·통신문에 사용.

He wasn't on shift, but he was kept apprised at all times.![speech_20250828231441108.mp3](RG7xkwNN.mp3)
```

## Target File Format
Vocabulary files are organized alphabetically (a.md, b.md, c.md, etc.) with this structure:
```
{word} ![[100. media/audio/file1.mp3]] ![[100. media/audio/file2.mp3]]
?
definition and notes

Example sentence ![[100. media/audio/example.mp3]]
<!--SR:!2025-10-25,3,228-->
-
```

**Important constraints**:
- Never, ever delete existing files. If there is a problem just ask me.
- Content separator: `?` (on line 2 for flashcard compatibility)
- Do NOT add SR (spaced repetition) metadata for new words (no `<!--SR:!...-->` lines)
- Convert markdown links `![...](file)` to Obsidian wiki-links `![[100. media/audio/file]]`
- Images get `|200` size modifier: `![[100. media/image/file.png|200]]`
- Each entry ends with `-` on its own line
- Words are appended to the file matching their first letter
- **New words must be inserted BEFORE the `#Vocabulary` tag** (the tag must always be at the end of the file)

## Task Requirements

Please perform the following steps:

### Step 1: Analyze Source Files
- List all markdown files in the migration directory
- Read 2-3 sample files to understand the exact format
- Identify all audio and image file references
- Map the relationship between markdown syntax and actual filenames

### Step 2: Create Processing Script
Create a bash script that:
- Iterates through all `.md` files in migration directory
- Extracts the word name (filename without .md extension)
- Determines target file based on first letter (lowercase)
- Reads file content and identifies all media references

### Step 3: Copy Media Files
For each vocabulary entry:
- Find all audio files (`.mp3`) referenced in the markdown
- Find all image files (`.png`, `.jpg`, `.jpeg`) referenced
- Copy audio files to `/home/genext/Documents/Obsidian Vault/100. media/audio/`
- Copy image files to `/home/genext/Documents/Obsidian Vault/100. media/image/`

### Step 4: Convert Link Syntax
Transform markdown links to Obsidian format:
- `![anything](audio.mp3)` → `![[100. media/audio/audio.mp3]]`
- `![anything](image.png)` → `![[100. media/image/image.png|200]]`
- Remove any `---` separator lines
- Ensure the word appears on first line with audio references

### Step 5: Format Entry
Structure each entry as:
```
{word} ![[audio1.mp3]] ![[audio2.mp3]]
?
{remaining content with converted links}
-
```

### Step 6: Insert into Target File
- Insert formatted entry into appropriate alphabetical file (a.md, b.md, etc.)
- **Insert BEFORE the `#Vocabulary` tag** (not at the end of file)
- Create the file if it doesn't exist (for letters like r.md, s.md, t.md)
- Add blank line before entry for separation
- Ensure `#Vocabulary` tag remains at the end of the file

### Step 7: Fix Audio References
After initial migration, verify that:
- Word name appears once (not duplicated like "apprise apprise")
- All audio files from the first line are properly formatted
- The `?` separator is present on line 2

### Step 8: Verification
Create a verification script that:
- Counts migrated words
- Verifies audio files were copied (compare source vs destination count)
- Verifies image files were copied
- Displays sample output for each migrated word (first 8-10 lines)
- Confirms proper formatting

### Step 9: Generate Summary
Provide a summary showing:
- Number of words migrated
- Which words went to which files (grouped by letter)
- Count of audio files copied
- Count of image files copied
- Confirmation that link syntax was converted
- Confirmation that no SR metadata was added

## Expected Output Format

The script should produce vocabulary entries like:

```
apprise ![[100. media/audio/lCnIMS8V.mp3]] ![[100. media/audio/4ONup1lF.mp3]]
?
![[100. media/image/msgYOZd4.png|200]]
formal to tell or give someone information about something SYN inform
(격식) 주로 상업·통신문에 사용.

He wasn't on shift, but he was kept apprised at all times.![[100. media/audio/RG7xkwNN.mp3]]![[100. media/audio/FoNrWMWw.mp3]]

The district chairman was fully apprised of all the details.![[100. media/audio/vGphOuiu.mp3]]![[100. media/audio/vm5xRmk9.mp3]]
-
```

## Notes
- Handle edge cases where words may not have audio on the first line (like "flush")
- Some words may have related forms (like "refute" and "refutation" in same entry)
- Preserve all Korean translations and notes
- Maintain the exact formatting of example sentences
- Do not modify existing entries in target files, only append new ones

---

## Customization Points

When reusing this prompt, update these values:
- **Source directory path**: **REQUIRED** - Specify your migration source directory in the Context section
- **Target directory path**: Currently `/home/genext/Documents/Obsidian Vault/3. English/Vocabulary` (update if different)
- **Source format details**: Update the example if your source format differs
- **Target format details**: Update if your vocabulary structure is different
- **Link syntax rules**: Modify if you use different Obsidian link patterns
- **Metadata handling**: Change SR metadata instructions if needed
