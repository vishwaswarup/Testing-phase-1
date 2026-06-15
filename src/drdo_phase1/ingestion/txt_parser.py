"""
Experiment 4 — Plain Text File Reading
========================================

Purpose
-------
Learn the basics of reading .txt files in Python — line counting,
character counting, and encoding handling.

Library
-------
Python standard library only (no third-party packages needed).

Key Concepts
------------
* `open(path, "r", encoding="utf-8")` opens a text file.
* `.readlines()` returns a list of lines (including newlines).
* `.read()` returns the entire file as a single string.
"""

import os


def extract_txt(file_path: str) -> dict:
    """
    Read a plain-text file and return its contents.

    Returns
    -------
    dict with keys:
        text       – full file contents
        line_count – number of lines
        extractor  – name of the extractor used
    """

    # --- 1. Validate path ---------------------------------------------------
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            contents = f.read()
    except UnicodeDecodeError:
        # Fall back to latin-1 which never raises decode errors
        with open(file_path, "r", encoding="latin-1") as f:
            contents = f.read()
    except Exception as e:
        raise RuntimeError(f"Could not read file: {e}")

    return {
        "text": contents,
        "line_count": len(contents.splitlines()),
        "extractor": "Built-in (open)",
    }


def main():
    print("=" * 60)
    print("  Experiment 4 — TXT Extraction")
    print("=" * 60)

    file_path = input("\nEnter TXT path: ").strip()

    try:
        result = extract_txt(file_path)
    except (FileNotFoundError, RuntimeError) as e:
        print(f"[ERROR] {e}")
        return

    print()
    print(f"  Line Count      : {result['line_count']}")
    print(f"  Character Count : {len(result['text'])}")
    print()
    print("--- Contents ---\n")
    print(result["text"])
    print()


if __name__ == "__main__":
    main()
