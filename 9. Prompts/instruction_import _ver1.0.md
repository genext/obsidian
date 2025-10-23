# Roam Import Instructions

## Overview
Instructions for importing Roam research page exports into Obsidian Vault with proper media file organization.

**IMPORTANT**: When running the import, Claude will ask you:
1. Where the roam export is located (source directory)
2. Where you want to save the converted markdown files (target directory)

Media files (mp3, mp4, png, jpg, etc) are always moved to: `/home/genext/Documents/Obsidian Vault/100. media/`

## Import Steps for Claude

### Step 1: Ask User for Directories
Ask the user:
- **Source**: Where is the Roam export? (e.g., `/home/genext/Documents/Obsidian Vault/Roam/genext-2025-10-05-02-18-30/[page title]`)
- **Target**: Where should converted markdown files be saved? (e.g., `/home/genext/Documents/Obsidian Vault/[folder name]/[note title]`)

### Step 2: Create Target Directory
```bash
mkdir -p "[USER_SPECIFIED_TARGET_DIRECTORY]"
```

### Step 3: Ensure Media Directory Exists
```bash
mkdir -p "/home/genext/Documents/Obsidian Vault/100. media"
```

### Step 4: Copy Markdown Files
```bash
cp "[SOURCE_DIRECTORY]"/*.md "[USER_SPECIFIED_TARGET_DIRECTORY]/"
```

### Step 5: Move Media Files to Fixed Location
```bash
# Move audio files
mv "[SOURCE_DIRECTORY]"/*.mp3 "/home/genext/Documents/Obsidian Vault/100. media/"

# Move image files
mv "[SOURCE_DIRECTORY]"/*.png "/home/genext/Documents/Obsidian Vault/100. media/" 2>/dev/null || true
mv "[SOURCE_DIRECTORY]"/*.jpg "/home/genext/Documents/Obsidian Vault/100. media/" 2>/dev/null || true
```

### Step 6: Fix Media Links in Markdown Files
Run this Python script in the target directory:

```bash
cd "[USER_SPECIFIED_TARGET_DIRECTORY]" && python3 << 'EOF'
import os
import re

for filename in os.listdir('.'):
    if filename.endswith('.md'):
        filepath = os.path.join('.', filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Replace markdown links with Obsidian wiki-links
        # Pattern: ![filename.mp3](../../100. media/filename.mp3) -> ![[100. media/filename.mp3]]
        content = re.sub(r'\!\[[^\]]*\]\(\.\./\.\./100\. media/([^)]+)\)', r'![[100. media/\1]]', content)

        # Also handle any remaining ../../100. media/ paths
        content = re.sub(r'\]\(\.\./\.\./100\. media/([^)]+)\)', r'[[100. media/\1]]', content)

        # Handle direct file references (no path)
        content = re.sub(r'\!\[image\.png\]\(([^/\)]+\.(?:png|jpg|jpeg))\)', r'![[100. media/\1]]', content)
        content = re.sub(r'\!\[speech_[^\]]*\]\(([^/\)]+\.mp3)\)', r'![[100. media/\1]]', content)

        # Add line break before media embeds if text is right before them
        content = re.sub(r'([^\n])\!\[\[100\. media/', r'\1\n![[100. media/', content)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Fixed: {filename}")
EOF
```

## Media Link Format

### Before (Mochi Export)
```markdown
![speech_20250908003335657.mp3](2JkKUZZE.mp3)
![image.png](p5sgLxfr.png)
```

### After (Obsidian Format)
```markdown
![[100. media/2JkKUZZE.mp3]]
![[100. media/image/p5sgLxfr.png]]
```

## Verification

### Check file counts
```bash
# Count markdown files in target directory
ls "[USER_SPECIFIED_TARGET_DIRECTORY]"/*.md | wc -l

# Count media files moved
ls "/home/genext/Documents/Obsidian Vault/100. media/" | grep -E "\.(mp3|png|jpg)$" | wc -l
```

### Verify media links
```bash
# Check a sample file
cat "[USER_SPECIFIED_TARGET_DIRECTORY]/[sample-file].md"
```

## Expected Results
- ✅ Markdown files in user-specified target directory
- ✅ All media files in `100. media/`
- ✅ Audio files play when clicked in Obsidian
- ✅ Images display inline in Obsidian
- ✅ Links use Obsidian wiki-link format: `![[100. media/filename]]`

## Troubleshooting

### Media not rendering
- Check if media files exist in `100. media/` directory
- Verify link format is `![[100. media/filename]]` not `![](path)`
- Ensure no spaces or special characters in filenames

### Audio not playing
- Confirm `.mp3` extension is lowercase
- Check file permissions: `chmod 644 100. media/*.mp3`

### Images not showing
- Verify image format (png, jpg, jpeg)
- Check file size (very large images may not render)
- Ensure Obsidian has permission to read media directory
