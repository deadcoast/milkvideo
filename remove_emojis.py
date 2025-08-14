#!/usr/bin/env python3
"""Remove emojis from source files."""

import argparse
import os
import re
from pathlib import Path


# Modern emoji Unicode ranges (includes emoji components and sequences)
EMOJI_PATTERN = re.compile(
    r"["
    "\U0001f600-\U0001f64f"  # Emoticons
    "\U0001f300-\U0001f5ff"  # Symbols & Pictographs
    "\U0001f680-\U0001f6ff"  # Transport & Map
    "\U0001f700-\U0001f77f"  # Alchemical Symbols
    "\U0001f780-\U0001f7ff"  # Geometric Shapes Extended
    "\U0001f800-\U0001f8ff"  # Supplemental Arrows-C
    "\U0001f900-\U0001f9ff"  # Supplemental Symbols and Pictographs
    "\U0001fa00-\U0001fa6f"  # Chess Symbols
    "\U0001fa70-\U0001faff"  # Symbols and Pictographs Extended-A
    "\U00002702-\U000027b0"  # Dingbats
    "\U000024c2-\U0001f251"  # Enclosed Characters
    "\U0001f004"  # Mahjong Tile Red Dragon
    "\U0001f0cf"  # Playing Card Black Joker
    "\U0001f18e"  # Negative Squared Cross Mark
    "\U0001f191-\U0001f19a"  # Squared Latin Letters
    "\U0001f201-\U0001f202"  # Squared Katakana
    "\U0001f21a"  # Squared CJK Ideograph
    "\U0001f22f"  # Squared CJK Ideograph
    "\U0001f232-\U0001f23a"  # Squared CJK Ideographs
    "\U0001f250"  # Circled Ideograph Advantage
    "\U0001f300-\U0001f320"  # Weather Symbols
    "\U0001f330-\U0001f335"  # Plant Symbols
    "\U0001f337-\U0001f37c"  # Food & Drink
    "\U0001f380-\U0001f393"  # Celebration
    "\U0001f3a0-\U0001f3c4"  # Activity
    "\U0001f3c6-\U0001f3ca"  # Award Symbols
    "\U0001f3e0-\U0001f3f0"  # Building Symbols
    "\U0001f3f4"  # Waving Black Flag
    "\U0001f3f8-\U0001f3ff"  # Skin Tone Modifiers
    "\U0001f400-\U0001f43e"  # Animal Symbols
    "\U0001f440"  # Eyes
    "\U0001f442-\U0001f4fc"  # Body Parts & Clothing
    "\U0001f4ff-\U0001f53d"  # Office & Stationery
    "\U0001f54b-\U0001f54e"  # Religious Symbols
    "\U0001f550-\U0001f567"  # Clock Faces
    "\U0001f57a"  # Man Dancing
    "\U0001f595-\U0001f596"  # Hand Gestures
    "\U0001f5a4"  # Black Heart
    "\U0001f5fb-\U0001f5ff"  # Map Symbols
    r"]+"
)


def remove_emojis(text: str) -> str:
    """Remove all modern emojis from text"""
    return EMOJI_PATTERN.sub("", text)


def process_file(file_path: Path, backup: bool):
    """Process a single file: remove emojis and save"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        print(f"Skipping binary file: {file_path}")
        return

    cleaned_content = remove_emojis(content)

    if content == cleaned_content:
        print(f"No emojis found in: {file_path}")
        return

    if backup:
        backup_path = file_path.with_suffix(f"{file_path.suffix}.bak")
        file_path.rename(backup_path)
        print(f"Created backup: {backup_path}")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(cleaned_content)
    print(f"Removed emojis from: {file_path}")


def main():
    parser = argparse.ArgumentParser(description="Remove modern emojis from source files")
    parser.add_argument("directory", help="Directory to process")
    parser.add_argument("--backup", action="store_true", help="Create backup files")
    args = parser.parse_args()

    valid_extensions = {".py", ".html", ".css", ".md", ".txt"}
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


if __name__ == "__main__":
    main()
