"""
Image OCR using RapidOCR
=========================

Extracts text from images using RapidOCR (ONNX Runtime backend).
This is a lightweight, pure-Python OCR engine that requires no
system-level dependencies like Tesseract or Poppler.
"""

import os
from rapidocr_onnxruntime import RapidOCR


def extract_image_text(file_path: str) -> dict:
    """
    Run OCR on an image and return extracted text.

    Returns
    -------
    dict with keys:
        text       – combined extracted text
        detections – number of text detections
        extractor  – name of the extractor used
    """

    # --- 1. Validate path ---------------------------------------------------
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # --- 2. Initialise RapidOCR ---------------------------------------------
    try:
        ocr = RapidOCR()
    except Exception as e:
        raise RuntimeError(f"Could not initialise RapidOCR: {e}")

    # --- 3. Run OCR ---------------------------------------------------------
    try:
        results, _ = ocr(file_path)
    except Exception as e:
        raise RuntimeError(f"OCR failed: {e}")

    # --- 4. Combine detected text -------------------------------------------
    combined_text = ""
    detections = 0
    if results:
        for line in results:
            # RapidOCR returns list of [bbox, text, confidence]
            combined_text += line[1] + " "
            detections += 1

    combined_text = combined_text.strip()

    return {
        "text": combined_text,
        "detections": detections,
        "extractor": "RapidOCR",
    }


def main():
    print("=" * 60)
    print("  Image OCR (RapidOCR)")
    print("=" * 60)

    file_path = input("\nEnter image path: ").strip()

    try:
        print("\n  Initialising RapidOCR...")
        print("  Running OCR...\n")
        result = extract_image_text(file_path)
    except (FileNotFoundError, RuntimeError) as e:
        print(f"[ERROR] {e}")
        return

    print("-" * 40)
    print(f"  Total Detections : {result['detections']}")
    print()
    print("  Combined Extracted Text:")
    print(f"  {result['text']}")
    print()


if __name__ == "__main__":
    main()
