"""
Unified Ingestion Pipeline — Phase 2
=====================================

This is the single entry point for ingesting any supported file.

Flow
----
    Input File
        ↓
    File Classifier (python-magic)
        ↓
    Router (based on detected type)
        ↓
    Appropriate Extractor
        ↓
    Document Object (unified dataclass)
        ↓
    Ingestion Summary

Supported file types:  PDF, DOCX, TXT, IMAGE
Scanned PDFs are auto-detected and handled via OCR.

Usage
-----
    python3 pipeline.py

Then enter a file path when prompted, for example:

    test_files/DRDO Offline Multimodal Intelligence Analysis System.pdf
"""

import os
import sys
import uuid

# ---------------------------------------------------------------------------
# Import the reusable functions from the experiment modules.
# We add the project root to sys.path so that `experiments.*` can be
# imported regardless of where the user runs this script from.
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ingestion.file_classifier import classify_file
from ingestion.pdf_parser import extract_pdf
from ingestion.docx_parser import extract_docx
from ingestion.txt_parser import extract_txt
from ingestion.image_parser import extract_image_text
from ingestion.scanned_pdf_parser import extract_scanned_pdf
from ingestion.vlm_captioner import generate_caption, process_video_frames
from ingestion.whisper_parser import transcribe_audio
from models.document import Document


def ingest(file_path: str) -> Document | None: #this means the function will either return a Document object or None
    """
    Ingest a single file:

    1. Classify its type using python-magic.
    2. Route to the correct extractor.
    3. Convert the extraction result into a unified Document object.
    4. Return the Document, or None if ingestion failed.
    """

    # --- 1. Validate --------------------------------------------------------
    if not os.path.isfile(file_path):
        print(f"  ⚠  File not found: {file_path}")
        return None

    # --- 2. Classify --------------------------------------------------------
    classification = classify_file(file_path)
    category = classification["category"]

    # --- 3. Route & Extract -------------------------------------------------
    try:
        if category == "PDF":
            result = extract_pdf(file_path)
            # Note: pdf_parser.py now implements the Mixed Pipeline (Per-page routing) internally.

        elif category == "DOCX":
            result = extract_docx(file_path)

        elif category == "TXT":
            result = extract_txt(file_path)

        elif category == "IMAGE":
            result = extract_image_text(file_path)
            
            # Apply Local VLM Scene Captioning
            caption = generate_caption(file_path)
            if caption:
                result["text"] += f"\n\n[VLM Scene Caption]: {caption}"

        elif category == "VIDEO":
            # Apply Whisper for audio transcription and VLM for keyframes
            result = transcribe_audio(file_path)
            captions = process_video_frames(file_path)
            if captions:
                result["text"] += "\n\n[VLM Scene Captions from Keyframes]:\n" + "\n".join(captions)
                
        elif category == "AUDIO":
            result = transcribe_audio(file_path)

        else:
            print(f"  ⚠  Unsupported file type: {classification['mime_type']}")
            return None

    except (FileNotFoundError, RuntimeError) as e:
        print(f"  ⚠  Extraction failed: {e}")
        return None

    # --- 4. Build unified Document object -----------------------------------
    #   Map extractor-specific fields into the common Document structure.
    # -----------------------------------------------------------------------

    # Try to extract a title from PDF metadata, otherwise use the filename.
    title = ""
    pdf_metadata = result.get("metadata", {})
    if pdf_metadata.get("title"):
        title = pdf_metadata["title"]
    else:
        title = os.path.basename(file_path)

    # Gather extra info into the metadata dict.
    metadata = {
        "extractor": result.get("extractor", "Unknown"),
    }
    if "metadata" in result:        # PDF metadata
        metadata["pdf"] = result["metadata"]
    if "paragraph_count" in result:  # DOCX
        metadata["paragraph_count"] = result["paragraph_count"]
    if "table_count" in result:      # DOCX tables
        metadata["table_count"] = result["table_count"]
    if "line_count" in result:       # TXT
        metadata["line_count"] = result["line_count"]
    if "detections" in result:       # IMAGE
        metadata["ocr_detections"] = result["detections"]

    # Set language from Whisper if available
    language = result.get("language", "")

    doc = Document(
        doc_id=str(uuid.uuid4()),
        source_type=category,
        source_path=os.path.abspath(file_path),
        raw_text=result.get("text", ""),
        title=title,
        language=language,
        page_count=result.get("page_count", 0),
        metadata=metadata,
    )

    return doc


def print_summary(doc: Document) -> None:
    """Print a structured ingestion summary from a Document object."""

    print()
    print("=" * 60)
    print("  INGESTION SUMMARY")
    print("=" * 60)
    print()
    print(f"  Document ID       : {doc.doc_id}")
    print(f"  Title             : {doc.title}")
    print(f"  Source Type       : {doc.source_type}")
    print(f"  Source Path       : {doc.source_path}")
    print(f"  Extractor Used    : {doc.metadata.get('extractor', 'N/A')}")
    print(f"  Characters        : {len(doc.raw_text)}")
    if doc.page_count:
        print(f"  Page Count        : {doc.page_count}")
    if doc.language:
        print(f"  Language          : {doc.language}")

    # Print any extra metadata
    extra_keys = [k for k in doc.metadata if k != "extractor"]
    if extra_keys:
        print()
        print("  --- Additional Metadata ---")
        for key in extra_keys:
            label = key.replace("_", " ").title()
            print(f"  {label:20s}: {doc.metadata[key]}")

    print()
    print("=" * 60)
    print()


def main():
    print()
    print("=" * 60)
    print("  DRDO Phase 2 — Unified Ingestion Pipeline")
    print("=" * 60)
    print()

    file_path = input("  Enter file path: ").strip()

    print()
    print(f"  Processing: {file_path}")
    print(f"  Classifying file type...")

    doc = ingest(file_path)

    if doc is None:
        print("\n  Ingestion failed. See errors above.")
        return

    print_summary(doc)

    # Show a preview of the extracted text
    if doc.raw_text.strip():
        print("  --- Extracted Text ---")
        print()
        if doc.source_type == "IMAGE" or len(doc.raw_text) <= 2000:
            # Print full text for images or short documents
            print(doc.raw_text.strip())
        else:
            # Truncate long documents (like huge PDFs)
            print(doc.raw_text[:1000].strip())
            print("\n  ... (truncated)")
        print()
    #print("also the full text is:")
    #print(doc.raw_text)

    

if __name__ == "__main__":
    main()
