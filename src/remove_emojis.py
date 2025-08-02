#!/usr/bin/env python3
import os
import re
import argparse
from pathlib import Path

# Modern emoji Unicode ranges (includes emoji components and sequences)
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # Emoticons
    "\U0001F300-\U0001F5FF"  # Symbols & Pictographs
    "\U0001F680-\U0001F6FF"  # Transport & Map
    "\U0001F700-\U0001F77F"  # Alchemical Symbols
    "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
    "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
    "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
    "\U0001FA00-\U0001FA6F"  # Chess Symbols
    "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
    "\U00002702-\U000027B0"  # Dingbats
    "\U000024C2-\U0001F251"  # Enclosed Characters
    "\U0001F004"             # Mahjong Tile Red Dragon
    "\U0001F0CF"             # Playing Card Black Joker
    "\U0001F18E"             # Negative Squared Cross Mark
    "\U0001F191-\U0001F19A"  # Squared Latin Letters
    "\U0001F201-\U0001F202"  # Squared Katakana
    "\U0001F21A"             # Squared CJK Ideograph
    "\U0001F22F"             # Squared CJK Ideograph
    "\U0001F232-\U0001F23A"  # Squared CJK Ideographs
    "\U0001F250"             # Circled Ideograph Advantage
    "\U0001F300-\U0001F320"  # Weather Symbols
    "\U0001F330-\U0001F335"  # Plant Symbols
    "\U0001F337-\U0001F37C"  # Food & Drink
    "\U0001F380-\U0001F393"  # Celebration
    "\U0001F3A0-\U0001F3C4"  # Activity
    "\U0001F3C6-\U0001F3CA"  # Award Symbols
    "\U0001F3E0-\U0001F3F0"  # Building Symbols
    "\U0001F3F4"             # Waving Black Flag
    "\U0001F3F8-\U0001F3FF"  # Skin Tone Modifiers
    "\U0001F400-\U0001F43E"  # Animal Symbols
    "\U0001F440"             # Eyes
    "\U0001F442-\U0001F4FC"  # Body Parts & Clothing
    "\U0001F4FF-\U0001F53D"  # Office & Stationery
    "\U0001F54B-\U0001F54E"  # Religious Symbols
    "\U0001F550-\U0001F567"  # Clock Faces
    "\U0001F57A"             # Man Dancing
    "\U0001F595-\U0001F596"  # Hand Gestures
    "\U0001F5A4"             # Black Heart
    "\U0001F5FB-\U0001F5FF"  # Map Symbols
    "]+"
)

def remove_emojis(text: str) -> str:
    """Remove all modern emojis from text"""
    return EMOJI_PATTERN.sub('', text)

def process_file(file_path: Path, backup: bool):
    """Process a single file: remove emojis and save"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        print(f"Skipping binary file: {file_path}")
        return

    cleaned_content = remove_emojis(content)
    
    if content == cleaned_content:
        print(f"No emojis found in: {file_path}")
        return

    if backup:
        backup_path = file_path.with_suffix(file_path.suffix + '.bak')
        file_path.rename(backup_path)
        print(f"Created backup: {backup_path}")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)
    print(f"Removed emojis from: {file_path}")

def main():
    parser = argparse.ArgumentParser(description='Remove modern emojis from source files')
    parser.add_argument('directory', help='Directory to process')
    parser.add_argument('--backup', action='store_true', help='Create backup files')
    args = parser.parse_args()

    valid_extensions = {'.py', '.html', '.css', '.md', '.txt'}
    processed_count = 0

    for root, _, files in os.walk(args.directory):
        for filename in files:
            file_path = Path(root) / filename
            if file_path.suffix.lower() in valid_extensions:
                process_file(file_path, args.backup)
                processed_count += 1

    if processed_count == 0:
        print("No matching files found in the specified directory")
    else:
        print(f"Processed {processed_count} files")

if __name__ == '__main__':
    main()