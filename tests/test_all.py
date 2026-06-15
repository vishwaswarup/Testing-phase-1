"""
Test All - Comprehensive Ingestion Pipeline Verification
=========================================================

This script automatically tests every file in `tests/data/` across all
categories (images, videos, documents) to ensure the unified ingestion
pipeline handles everything without exceptions.
"""

import os
import sys
import traceback

# Force UTF-8 output on Windows terminals
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "drdo_phase1")
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from pipeline import ingest
from incident_pipeline import build_incident

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

def get_all_test_files():
    files = []
    for root, _, filenames in os.walk(DATA_DIR):
        for filename in filenames:
            # Skip hidden files
            if filename.startswith('.'):
                continue
            files.append(os.path.join(root, filename))
    return files

def run_tests():
    print("=" * 70)
    print("  Test All - Comprehensive Ingestion Verification")
    print("=" * 70)
    print()

    test_files = get_all_test_files()
    if not test_files:
        print("  [!] No test files found in tests/data/")
        return

    success_count = 0
    failure_count = 0
    failed_files = []

    for idx, file_path in enumerate(test_files, start=1):
        filename = os.path.basename(file_path)
        print(f"  [{idx}/{len(test_files)}] Testing: {filename}")
        
        try:
            # 1. Test Phase 1A/1B (Ingestion)
            doc = ingest(file_path)
            
            if doc is None:
                raise ValueError("Ingestion returned None (failed to ingest).")
                
            if not doc.raw_text.strip():
                print("    [WARN] Extracted text is empty.")
            else:
                print(f"    [OK] Ingestion successful. Extracted {len(doc.raw_text)} characters.")
                
            # Print Document contract fields
            print(f"         Source Type : {doc.source_type}")
            print(f"         Extractor   : {doc.metadata.get('extractor', 'N/A')}")
            print(f"         Language    : {doc.language or '(not set)'}")
            if doc.page_count:
                print(f"         Page Count  : {doc.page_count}")
            if doc.metadata.get('table_count'):
                print(f"         Tables      : {doc.metadata['table_count']}")
            if doc.metadata.get('ocr_detections'):
                print(f"         OCR Hits    : {doc.metadata['ocr_detections']}")
                
            # 2. Test Phase 2 (Extraction)
            try:
                incident = build_incident(doc)
                print(f"    [OK] Incident extraction successful. Summary: {incident.summary[:50]}...")
            except Exception as e:
                 raise RuntimeError(f"Incident Extraction Pipeline failed: {e}")
                 
            success_count += 1
            
        except Exception as e:
            print(f"    [FAIL] {e}")
            traceback.print_exc()
            failure_count += 1
            failed_files.append((filename, str(e)))
            
        print("-" * 60)

    print("=" * 70)
    print(f"  TEST SUMMARY")
    print(f"  Total Files : {len(test_files)}")
    print(f"  Successful  : {success_count}")
    print(f"  Failed      : {failure_count}")
    
    if failure_count > 0:
        print("\n  Failed Files:")
        for fname, err in failed_files:
            print(f"    - {fname}: {err}")
    else:
        print("\n  All files passed! Phase 1A + 1B verified.")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
