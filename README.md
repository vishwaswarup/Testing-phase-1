# DRDO Phase 1A & 2 — Library Exploration & Data Ingestion Research

> **Status:** Phase 1 & 2 — Data Ingestion & Incident Generation  
> **Objective:** Learn how different document ingestion libraries behave and extract incidents from documents *before* integrating them into a larger system.

---

## Project Purpose

This project is an **experimentation environment** for Phase 1 and 2 of an Offline Multimodal Intelligence Analysis System (DRDO-style).

It is intentionally **not** a production pipeline. There are no vector databases, no embeddings, no LLM integrations, and no RAG architecture here. The sole goal is to:

1. **Understand** how each library reads and processes different file formats.
2. **Observe** the raw outputs (text, metadata, OCR detections) first-hand.
3. **Extract** entities to form an `Incident` object.

Once this exploration phase is complete, the learnings will feed into the design of the real ingestion pipeline.

---

## Project Structure

```text
drdo_phase1/
│
├── tests/
│   ├── data/                      ← Drop sample PDFs, DOCX, TXT, images here
│   └── test_phase*.py             ← Test scripts for the extraction logic
│
├── src/drdo_phase1/               ← Application source code
│   ├── ingestion/                 ← File parsers (PDF, DOCX, TXT, etc.)
│   ├── extraction/                ← Entity extractors (Location, Date, etc.)
│   ├── models/                    ← Dataclasses (Document, Incident)
│   ├── pipeline.py                ← Unified Ingestion Pipeline (Phase 1)
│   └── incident_pipeline.py       ← Incident Generation Pipeline (Phase 2)
│
├── notebooks/                     ← Jupyter Notebooks for presentation
│   ├── 01_ingestion_phase.ipynb   ← Demo of document ingestion
│   └── 02_incident_generation.ipynb ← Demo of incident generation
│
├── requirements.txt
└── README.md
```

---

## Installation

### 1. Create a virtual environment

```bash
python -m venv .venv
```

### 2. Activate the virtual environment

**macOS / Linux:**

```bash
source .venv/bin/activate
```

**Windows (PowerShell):**

```powershell
.venv\Scripts\Activate.ps1
```

**Windows (CMD):**

```cmd
.venv\Scripts\activate.bat
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
# Additional packages for jupyter notebooks
pip install jupyter
```

### 4. System dependency — poppler (for pdf2image)

`pdf2image` requires the **poppler** command-line tools to convert PDF pages into images.

**macOS:**

```bash
brew install poppler
```

**Ubuntu / Debian:**

```bash
sudo apt-get install poppler-utils
```

**Windows:**

Download poppler from https://github.com/oschwartz10612/poppler-windows/releases and add the `bin/` folder to your system PATH.

---

## Running the Pipelines

### Using Jupyter Notebooks (Recommended for Presentation)

You can run the interactive notebooks to see step-by-step execution:

```bash
jupyter notebook notebooks/
```
Open `01_ingestion_phase.ipynb` or `02_incident_generation.ipynb` to view the workflows.

### Using the Command Line

You can also run the unified pipelines directly from the terminal:

**Phase 1 - Unified Ingestion Pipeline:**
```bash
python src/drdo_phase1/pipeline.py
```
*(When prompted, enter a path to a file like `tests/data/DRDO Offline Multimodal Intelligence Analysis System.pdf`)*

**Phase 2 - Incident Extraction Pipeline:**
```bash
python src/drdo_phase1/incident_pipeline.py
```

---

## Libraries Used

| Library        | Import         | Purpose                                        |
| -------------- | -------------- | ---------------------------------------------- |
| python-magic   | `magic`        | Detect file type from binary content            |
| PyMuPDF        | `fitz`         | Read and extract text from PDF files            |
| python-docx    | `docx`         | Read paragraphs from DOCX files                 |
| EasyOCR        | `easyocr`      | Optical Character Recognition on images          |
| Pillow         | `PIL`          | Image handling (used by EasyOCR and pdf2image)   |
| pdf2image      | `pdf2image`    | Convert PDF pages to images (requires poppler)   |

---

## Future Architecture

Eventually, this system will evolve into a full offline intelligence-analysis pipeline:

```text
Input File
    ↓
File Classifier          ← src/drdo_phase1/ingestion/file_classifier.py
    ↓
Format-Specific Loader   ← src/drdo_phase1/ingestion/*
    ↓
Text Extraction
    ↓
Document Object          ← src/drdo_phase1/models/document.py
    ↓
Incident Extraction      ← src/drdo_phase1/incident_pipeline.py
    ↓
Incident Records         ← src/drdo_phase1/models/incident.py
    ↓
Embeddings               ← (future phase)
    ↓
Retrieval                ← (future phase)
```

**This project currently goes up to the Incident Extraction stage.**  
Everything below that line (embeddings, retrieval) is for later phases.

---

## Notes

- Place your sample test files in the `tests/data/` directory.
- The `temp_pages/` folder is created automatically during scanned PDF extraction and can be deleted safely.
- All ingestion scripts use `gpu=False` for EasyOCR to ensure they run on any machine.
- Each script handles errors gracefully and prints helpful messages on failure.
