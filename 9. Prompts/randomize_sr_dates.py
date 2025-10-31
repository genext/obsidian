#!/usr/bin/env python3
"""
Randomize SR dates for vocabulary entries
Keeps first entry at original date, spreads rest randomly between original and end date
"""

import sys
import re
from datetime import datetime, timedelta
import random

def random_date_between(start_date_str, end_date_str):
    """Generate random date between start and end dates"""
    start = datetime.strptime(start_date_str, "%Y-%m-%d")
    end = datetime.strptime(end_date_str, "%Y-%m-%d")

    delta = end - start
    random_days = random.randint(0, delta.days)
    random_date = start + timedelta(days=random_days)

    return random_date.strftime("%Y-%m-%d")

def main():
    if len(sys.argv) != 4:
        print("Usage: randomize_sr_dates.py <file> <start_date> <end_date>")
        print("\nExample:")
        print('  python3 randomize_sr_dates.py "3. English/Vocabulary/h.md" "2025-11-24" "2026-03-31"')
        sys.exit(1)

    file_path = sys.argv[1]
    start_date = sys.argv[2]
    end_date = sys.argv[3]

    # Read file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all SR tags with the start date
    pattern = f'<!--SR:!{re.escape(start_date)},1,230-->'
    matches = list(re.finditer(pattern, content))

    print(f"Found {len(matches)} entries with date {start_date}")
    print(f"Keeping first entry at {start_date}")
    print(f"Randomizing remaining {len(matches)-1} entries between {start_date} and {end_date}")

    # Generate random dates for all except first
    random_dates = [start_date]  # Keep first entry
    for i in range(len(matches) - 1):
        random_dates.append(random_date_between(start_date, end_date))

    # Replace each occurrence
    new_content = content
    offset = 0
    for i, match in enumerate(matches):
        old_tag = match.group(0)
        new_tag = f'<!--SR:!{random_dates[i]},1,230-->'

        start_pos = match.start() + offset
        end_pos = match.end() + offset

        new_content = new_content[:start_pos] + new_tag + new_content[end_pos:]
        offset += len(new_tag) - len(old_tag)

        if i == 0:
            print(f"  Entry 1: {start_date} (kept)")
        elif i < 5 or i >= len(matches) - 2:
            print(f"  Entry {i+1}: {random_dates[i]}")
        elif i == 5:
            print(f"  ... ({len(matches)-7} more entries) ...")

    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"\n✅ Randomization complete!")
    print(f"Updated {len(matches)} entries in {file_path}")

    # Show date distribution
    date_counts = {}
    for date in random_dates:
        month = date[:7]  # YYYY-MM
        date_counts[month] = date_counts.get(month, 0) + 1

    print(f"\nDistribution by month:")
    for month in sorted(date_counts.keys()):
        print(f"  {month}: {date_counts[month]} entries")

if __name__ == '__main__':
    main()
