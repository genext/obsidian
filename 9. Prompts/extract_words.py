#!/usr/bin/env python3
"""
Extract words from filenames.
Filename IS the word, just remove .md extension.
Keep pronunciation markers (++x++) for now - migration script will handle finding the file.
"""
import os, sys

def main():
    if len(sys.argv) < 3:
        print("Usage: extract_words.py <dir> <letter>")
        sys.exit(1)

    d, letter = sys.argv[1], sys.argv[2].lower()

    words = [f[:-3] for f in sorted(os.listdir(d)) 
             if f.endswith('.md') and f.lower().startswith(letter)]

    for w in words:
        print(w)
    
    print(f"\nTotal: {len(words)}", file=sys.stderr)

if __name__ == "__main__":
    main()
