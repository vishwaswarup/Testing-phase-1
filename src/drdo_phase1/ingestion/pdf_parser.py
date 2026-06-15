"""
Experiment 2 — PDF Text Extraction using PyMuPDF
=================================================

Purpose
-------
Learn how PyMuPDF (imported as `fitz`) opens PDF files, exposes
metadata, and extracts text page-by-page.

Library
-------
PyMuPDF  →  `import fitz`

Key Concepts
------------
* `fitz.open(path)` returns a Document object.
* `doc.page_count` gives the total number of pages.
* `doc.metadata` is a dict with author, title, subject, etc.
* `page.get_text()` extracts all visible text from one page.
"""

import os
import fitz  # PyMuPDF


def extract_pdf(file_path: str) -> dict:
    """
    Open a PDF and extract text from all pages.

    Returns
    -------
    dict with keys:
        text       – full extracted text
        page_count – number of pages
        metadata   – PDF metadata dict
        extractor  – name of the extractor used
    """

    # --- 1. Validate path ----------------------------------------------------
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        doc = fitz.open(file_path)
    except Exception as e:
        raise RuntimeError(f"Could not open PDF: {e}")

    # --- 2. Extract text page-by-page (Mixed Pipeline) ----------------------
    all_text_parts = []
    
    # RapidOCR for per-page fallback on scanned pages
    from rapidocr_onnxruntime import RapidOCR
    import tempfile
    
    ocr = None

    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        page_text = page.get_text()
        
        # If very little digital text, fallback to OCR for THIS page
        if len(page_text.strip()) < 50:
            if ocr is None:
                ocr = RapidOCR()
                
            # Render page to image using PyMuPDF (no poppler needed)
            tmp_path = None
            try:
                mat = fitz.Matrix(300 / 72, 300 / 72)  # 300 DPI
                pix = page.get_pixmap(matrix=mat)
                tmp_path = tempfile.mktemp(suffix=".png")
                pix.save(tmp_path)
                results, _ = ocr(tmp_path)
                ocr_text = ""
                if results:
                    for line in results:
                        ocr_text += line[1] + " "
                page_text += f"\n[OCR Extracted]: {ocr_text.strip()}"
            except Exception as e:
                print(f"  [Warning] Per-page OCR failed on page {page_num+1}: {e}")
            finally:
                if tmp_path and os.path.exists(tmp_path):
                    try:
                        os.remove(tmp_path)
                    except OSError:
                        pass
                
        all_text_parts.append(page_text)

    full_text = "\n".join(all_text_parts)

    result = {
        "text": full_text,
        "page_count": doc.page_count,
        "metadata": dict(doc.metadata),
        "extractor": "PyMuPDF (Mixed Pipeline)",
    }

    doc.close()
    return result


def main():
    print("=" * 60)
    print("  Experiment 2 — PDF Extraction (PyMuPDF)")
    print("=" * 60)

    file_path = input("\nEnter PDF path: ").strip()

    try:
        result = extract_pdf(file_path)
    except (FileNotFoundError, RuntimeError) as e:
        print(f"[ERROR] {e}")
        return

    print(f"\n  Page Count : {result['page_count']}")
    print(f"  Metadata   :")
    for key, value in result["metadata"].items():
        if value:
            print(f"    {key:12s} : {value}")

    print(f"\n  Extracted Text:\n")
    print(result["text"] if result["text"].strip() else "  (no extractable text)")

    print("-" * 40)
    print(f"  Total extracted characters: {len(result['text'])}")
    print()


if __name__ == "__main__":
    main()
