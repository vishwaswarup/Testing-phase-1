import os
import sys

# Ensure src is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src', 'drdo_phase1')))

from pipeline import ingest, print_summary

files_to_test = [
    "tests/data/sample_incident.txt",
    "tests/data/sample-image.jpg",
    "tests/data/DRDO Offline Multimodal Intelligence Analysis System.pdf"
]

for file_path in files_to_test:
    print(f"\n=============================================")
    print(f"Testing: {file_path}")
    print(f"=============================================")
    
    try:
        doc = ingest(file_path)
        if doc:
            print_summary(doc)
            print("\n  --- Text Preview ---")
            print(doc.raw_text[:500] + ("..." if len(doc.raw_text) > 500 else ""))
        else:
            print(f"Failed to ingest: {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
