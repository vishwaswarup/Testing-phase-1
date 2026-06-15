"""
Experiment 1 — File Classification using python-magic
======================================================

Purpose
-------
Learn how to classify files based on their *actual binary content*
(magic bytes / file signatures) rather than relying on the file
extension, which can be renamed or missing.

Library
-------
python-magic  →  `import magic`

Key Concept
-----------
Every file format writes a unique "magic number" (a short byte
sequence) at the very beginning of the file.  python-magic reads
those bytes and returns the MIME type and a human-readable
description — exactly how the UNIX `file` command works.
"""

import os
import sys
import magic  # from python-magic


def classify_file(file_path: str) -> dict:
    """
    Analyse a file and return its MIME type, description,
    and a high-level category.
    """

    # --- 1. Check the file exists -------------------------------------------
    if not os.path.isfile(file_path):
        print(f"[ERROR] File not found: {file_path}")
        sys.exit(1)

    # --- 2. Detect MIME type -------------------------------------------------
    mime_type = magic.from_file(file_path, mime=True)

    # --- 3. Get a human-readable description --------------------------------
    description = magic.from_file(file_path)

    # --- 4. Map MIME type to a simple category ------------------------------
    if mime_type == "application/pdf":
        category = "PDF"
    elif mime_type in (
        "application/vnd.openxmlformats-officedocument"
        ".wordprocessingml.document",
        "application/msword",
    ):
        category = "DOCX"
    elif mime_type.startswith("text/"):
        category = "TXT"
    elif mime_type.startswith("image/"):
        category = "IMAGE"
    elif mime_type.startswith("video/"):
        category = "VIDEO"
    elif mime_type.startswith("audio/"):
        category = "AUDIO"
    else:
        # Fallback: use file extension when magic bytes are ambiguous
        ext = os.path.splitext(file_path)[1].lower()
        ext_map = {
            ".pdf": "PDF",
            ".docx": "DOCX", ".doc": "DOCX",
            ".txt": "TXT", ".csv": "TXT", ".log": "TXT",
            ".jpg": "IMAGE", ".jpeg": "IMAGE", ".png": "IMAGE",
            ".bmp": "IMAGE", ".gif": "IMAGE", ".tiff": "IMAGE",
            ".mp4": "VIDEO", ".avi": "VIDEO", ".mkv": "VIDEO",
            ".mov": "VIDEO", ".flv": "VIDEO",
            ".mp3": "AUDIO", ".wav": "AUDIO", ".flac": "AUDIO",
        }
        category = ext_map.get(ext, "UNKNOWN")

    return {
        "file_path": file_path,
        "mime_type": mime_type,
        "description": description,
        "category": category,
    }


def main():
    print("=" * 60)
    print("  Experiment 1 — File Classifier (python-magic)")
    print("=" * 60)
    print()

    file_path = input("Enter file path: ").strip()

    result = classify_file(file_path)

    print()
    print(f"  File Path   : {result['file_path']}")
    print(f"  MIME Type   : {result['mime_type']}")
    print(f"  Description : {result['description']}")
    print()
    print(f"  ➜  Classification: {result['category']}")
    print()


if __name__ == "__main__":
    main()
