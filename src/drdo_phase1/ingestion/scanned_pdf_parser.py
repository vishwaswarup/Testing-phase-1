"""
Scanned PDF OCR (PyMuPDF + RapidOCR)
======================================

Handles PDFs that contain scanned images instead of selectable text.
Uses PyMuPDF (fitz) to render each page to an image, then runs
RapidOCR on every page image. This eliminates the need for poppler.
"""

import os
import tempfile
import fitz  # PyMuPDF
from rapidocr_onnxruntime import RapidOCR


def extract_scanned_pdf(file_path: str) -> dict:
    """
    Convert a scanned PDF to images via PyMuPDF, then OCR each page.

    Returns
    -------
    dict with keys:
        text       – full extracted text (all pages combined)
        page_count – number of pages processed
        extractor  – name of the extractor used
    """

    # --- 1. Validate path ---------------------------------------------------
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # --- 2. Open PDF with PyMuPDF -------------------------------------------
    try:
        doc = fitz.open(file_path)
    except Exception as e:
        raise RuntimeError(f"Could not open PDF: {e}")

    # --- 3. Initialise RapidOCR ---------------------------------------------
    try:
        ocr = RapidOCR()
    except Exception as e:
        raise RuntimeError(f"Could not initialise RapidOCR: {e}")

    # --- 4. Render each page and OCR ----------------------------------------
    all_page_texts = []

    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)

        # Render page to a high-DPI image (300 DPI for best OCR accuracy)
        mat = fitz.Matrix(300 / 72, 300 / 72)
        pix = page.get_pixmap(matrix=mat)

        # Save to a temp file for OCR
        tmp_path = tempfile.mktemp(suffix=".png")
        pix.save(tmp_path)
        try:
            results, _ = ocr(tmp_path)
            page_text = ""
            if results:
                for line in results:
                    page_text += line[1] + " "
            all_page_texts.append(page_text.strip())
        except Exception:
            all_page_texts.append("")
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass

    doc.close()
    full_text = "\n".join(all_page_texts)

    return {
        "text": full_text,
        "page_count": len(all_page_texts),
        "extractor": "PyMuPDF + RapidOCR",
    }


def main():
    print("=" * 60)
    print("  Scanned PDF OCR (PyMuPDF + RapidOCR)")
    print("=" * 60)

    file_path = input("\nEnter scanned PDF path: ").strip()

    try:
        print("\n  Rendering PDF pages...")
        print("  Initialising RapidOCR...")
        result = extract_scanned_pdf(file_path)
    except (FileNotFoundError, RuntimeError) as e:
        print(f"[ERROR] {e}")
        return

    print(f"  Pages Processed: {result['page_count']}")
    print()

    for page_num, page_text in enumerate(result["text"].split("\n"), start=1):
        print(f"===== PAGE {page_num} OCR =====")
        print(page_text if page_text.strip() else "  (no text detected)")
        print()

    print("-" * 40)
    print(f"  Total extracted characters: {len(result['text'])}")
    print()


if __name__ == "__main__":
    main()
